# standard library imports
import argparse
import csv
import logging
import time

# third party imports
import defusedxml.ElementTree as ET
import requests
from config import settings
from requests.exceptions import RequestException


def parse_arguments():
    """
    Parses command line arguments.
    :return: Parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Script to interact with Panorama appliance.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--hostname",
        help="Hostname of the PAN-OS appliance",
    )
    parser.add_argument(
        "--logs",
        default=5000,
        help="Number of logs to capture, defaults to 5000",
    )
    parser.add_argument(
        "--startdate",
        default="2023/01/01 00:00:00",
        help="Date to start the query, format: YYYY/MM/DD HH:MM:SS",
    )
    return parser.parse_args()


def initiate_job(hostname, startdate, api_key):
    """
    Initiates a job on the firewall to fetch the HIP Users report.
    :param hostname: Hostname of the firewall
    :param startdate: Date to start the query
    :param api_key: API Key for authentication
    :return: Job ID
    """

    try:
        url = f"https://{hostname}/api/"
        querystring = {
            "type": "log",
            "log-type": "hipmatch",
            "query": f"(receive_time geq '{startdate}')",
            "key": api_key,
        }
        response = requests.get(url, headers={}, params=querystring, timeout=30)

        if response.status_code != 200:
            logging.error(f"Failed to initiate job: HTTP {response.status_code}")
            return None

        root = ET.fromstring(response.text)
        job_element = root.find(".//job")
        if job_element is None:
            logging.error("Failed to find job element in response.")
            return None

        return job_element.text
    except RequestException as e:
        logging.error(f"Network error while initiating job: {e}")
    except ET.ParseError:
        logging.error("Error parsing XML response.")
    return None


def poll_for_job_completion(hostname, job_id, api_key, interval=10, max_retries=30):
    """
    Polls the firewall for job completion.
    :param hostname: Hostname of the firewall
    :param job_id: The job ID to poll for
    :param api_key: API Key for authentication
    :param interval: Interval in seconds between each poll
    :param max_retries: Maximum number of retries before giving up
    :return: True if job completed successfully, False otherwise
    """

    retries = 0
    url = f"https://{hostname}/api/"

    while retries < max_retries:
        querystring = {
            "type": "log",
            "action": "get",
            "job-id": job_id,
            "key": api_key,
        }
        response = requests.get(url, params=querystring, timeout=30)

        logging.debug(f"Polling Job Response: {response.text}")

        # Parse the XML response
        root = ET.fromstring(response.text)

        if root.attrib.get("status") == "success":
            return True
        elif "not found" in response.text:
            logging.warning(
                f"Retry {retries + 1}/{max_retries}: Job {job_id} not found. Waiting before retry..."
            )
        else:
            logging.warning(
                f"Retry {retries + 1}/{max_retries}: Unexpected response. Waiting before retry..."
            )

        retries += 1
        time.sleep(interval)

    logging.error("Max retries reached without successful job completion.")
    return False


def fetch_job_results(hostname, job_id, api_key):
    """
    Fetches the results of a completed job.
    :param hostname: Hostname of the firewall
    :param job_id: The job ID to fetch results for
    :param api_key: API Key for authentication
    :return: XML string of job results
    """

    url = f"https://{hostname}/api/"
    full_url = f"{url}?type=log&action=get&job-id={job_id}&key={api_key}"
    response = requests.get(full_url, timeout=30)
    return response.text


def parse_xml_to_csv(xml_data, csv_filename):
    """
    Parses XML data and saves it into a CSV file.
    :param xml_data: XML data string
    :param csv_filename: Name of the CSV file to save the data
    """

    root = ET.fromstring(xml_data)
    entries = root.findall(".//entry")

    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        headers = [
            elem.tag
            for elem in entries[0]
            if elem.tag != "padding1" and elem.tag != "padding2"
        ]
        writer.writerow(headers)

        for entry in entries:
            row = [
                entry.find(tag).text if entry.find(tag) is not None else ""
                for tag in headers
            ]
            writer.writerow(row)


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Initiate job
    job_id = initiate_job(args.hostname, args.startdate, settings.api_key)
    if job_id is None:
        print(
            "Failed to initiate job. Please check your API key and log output for more details."
        )
        return

    # Poll for job completion
    print(f"Job ID: {job_id}")
    if poll_for_job_completion(args.hostname, job_id, settings.api_key):
        job_results = fetch_job_results(args.hostname, job_id, settings.api_key)
        parse_xml_to_csv(job_results, "hip_users_report.csv")
        print("HIP Users report saved to hip_users_report.csv")
    else:
        print("Job did not complete within the specified timeout.")


# Run the script
if __name__ == "__main__":
    main()
