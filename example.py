import requests
import xml.etree.ElementTree as ET


# Function to extract IP and computer name from the first API response
def extract_user_details(xml_response):
    root = ET.fromstring(xml_response)
    users = []
    for entry in root.findall(".//entry"):
        user_info = {
            "username": entry.find("username").text,
            "ip": entry.find("virtual-ip").text,
            "computer": entry.find("computer").text,
        }
        users.append(user_info)
    return users


# First API call to get Global Protect users
def get_global_protect_users():
    url = "https://datacenter.cdot.io/api/?type=op&cmd=<show><global-protect-gateway><current-user/></global-protect-gateway></show>"
    headers = {"X-PAN-KEY": "mykeywashere=="}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return extract_user_details(response.text)
    else:
        print("Failed to retrieve Global Protect users")
        return []


# Second API call to get HIP report for a user
def get_hip_report(user_info):
    url_template = "https://datacenter.cdot.io/api/?type=op&cmd=<show><user><hip-report><user>{username}</user><ip>{ip}</ip><computer>{computer}</computer></hip-report></user></show>"
    url = url_template.format(
        username=user_info["username"],
        ip=user_info["ip"],
        computer=user_info["computer"],
    )
    headers = {"X-PAN-KEY": "mykeywashere=="}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        print(f"HIP report for {user_info['username']}:\n{response.text}")
    else:
        print(f"Failed to retrieve HIP report for {user_info['username']}")


# Main function to orchestrate the calls
def main():
    users = get_global_protect_users()
    for user in users:
        get_hip_report(user)


if __name__ == "__main__":
    main()
