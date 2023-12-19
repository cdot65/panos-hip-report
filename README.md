# PAN-OS HIP Log CSV Exporter

## Overview

This tool exports Host Information Profile (HIP) logs from PAN-OS firewalls into CSV format for convenient analysis and reporting. HIP logs offer insights into the health and compliance status of devices connecting to your network, and this tool is designed to streamline the extraction and conversion of this data.

## Features

- Automated HIP Log Retrieval: Fetch HIP logs directly from the PAN-OS firewall.
- CSV Export: Converts HIP logs into a CSV format for ease of data analysis.
- Error Handling: Robust error handling for network issues and data processing.
- Customizable Querying: Allows specification of start date and log quantity for fetching logs.

## Prerequisites

Ensure you have the following prerequisites before running the tool:

- API key to a PAN-OS firewall, stored in `settings.yaml`.
- Python 3.x installed on the machine running the script (if applicable).
- Required Python Packages:
  - requests
  - defusedxml
  - dynaconf (optional, used for storing and importing variables in settings.yaml)

## Installation

To set up the HIP Log CSV Exporter, follow these steps:

```bash
git clone https://github.com/cdot65/panos-hip-report.git
cd panos-hip-report
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Configure the firewall settings in settings.yaml:

```yaml
---
api_key: "your api key goes here"
```

## Usage

Run the script with the necessary parameters:

```bash
python app.py --hostname datacenter.example.io --startdate '2023/12/01 00:00:00'
```

### Parameters

```bash
--hostname: Address of the PAN-OS firewall.
--startdate: Start date for the log query in 'YYYY/MM/DD HH:MM:SS' format.
--logs: (Optional) Number of logs to retrieve (default is 5000).
--debug: (Optional) Enable debug logging for troubleshooting.
```

### Example

```bash
python app.py --hostname datacenter.example.io --startdate '2023/12/01 00:00:00'
```

Upon successful execution, the HIP logs will be exported to a CSV file in the local directory.

## Troubleshooting

- Authentication Errors: Ensure the API key in settings.yaml is correct.
- Network Issues: Verify network connectivity to the firewall.
- Data Parsing Errors: Check if the firewall's API response format has changed.
- Debugging: Use the --debug flag to enable detailed logging.

For further assistance or to report issues, please open an issue on the GitHub repository.

