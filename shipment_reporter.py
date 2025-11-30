import requests
import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://public-api.easyship.com/2024-09"

def get_all_shipments(api_key):
    """
    Fetches all shipments from the Easyship API, handling pagination.

    Args:
        api_key (str): Your Easyship API key.

    Returns:
        list: A list of all Easyship shipment objects.
    """
    all_shipments = []
    page = 1
    has_next_page = True
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    while has_next_page:
        try:
            response = requests.get(
                f"{BASE_URL}/shipments",
                headers=headers,
                params={"page": page, "per_page": 100}
            )
            response.raise_for_status()
            data = response.json()

            shipments = data.get("shipments", [])
            all_shipments.extend(shipments)

            meta = data.get("meta", {})
            has_next_page = meta.get("has_next_page", False)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"An API error occurred: {e}")
            return None

    return all_shipments

def filter_undelivered_insured_shipments(shipments):
    """
    Filters a list of shipments for those that are undelivered and insured.

    Args:
        shipments (list): A list of Easyship shipment objects.

    Returns:
        list: A filtered list of Easyship shipment objects.
    """
    filtered = []
    for shipment in shipments:
        is_insured = shipment.get("insurance", {}).get("is_insured", False)
        status = shipment.get("shipment_state")

        if is_insured and status != 'delivered':
            filtered.append(shipment)

    return filtered

def generate_md_report(shipments, filename):
    """
    Generates a Markdown report of shipments.

    Args:
        shipments (list): A list of Easyship shipment objects.
        filename (str): The name of the output MD file.
    """
    if not shipments:
        print("No shipments to generate a report for.")
        return

    with open(filename, 'w') as f:
        f.write("# Undelivered and Insured Shipments Report\n\n")
        f.write(f"Total shipments found: {len(shipments)}\n\n")

        for shipment in shipments:
            f.write(f"## Shipment ID: `{shipment.get('easyship_shipment_id')}`\n\n")

            f.write(f"- **Status:** {shipment.get('shipment_state')}\n")
            f.write(f"- **Label State:** {shipment.get('label_state')}\n")
            f.write(f"- **Created At:** {shipment.get('created_at')}\n")
            f.write(f"- **Is Insured:** {shipment.get('insurance', {}).get('is_insured')}\n")
            f.write(f"- **Courier:** {shipment.get('selected_courier', {}).get('name')}\n")
            f.write(f"- **Tracking Number:** `{shipment.get('courier_tracking_number')}`\n\n")

            f.write("### Full Details:\n")
            f.write("```json\n")
            f.write(json.dumps(shipment, indent=2))
            f.write("\n```\n\n")
            f.write("---\n\n")

    print(f"Report generated successfully: {filename}")


def main():
    """
    Main function to retrieve, filter, and report on shipments.
    """
    parser = argparse.ArgumentParser(description="Retrieve and report on Easyship shipments.")
    parser.add_argument('--api-key', help="Your Easyship API key.")
    parser.add_argument('--output-file', default='undelivered_insured_shipments.md', help="The path to the output MD file.")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("EASYSHIP_API_KEY")
    if not api_key:
        print("Error: API key not provided. Please use the --api-key argument or set the EASYSHIP_API_KEY environment variable.")
        return

    print("Retrieving all shipments...")
    all_shipments = get_all_shipments(api_key)

    if all_shipments is not None:
        print(f"Found {len(all_shipments)} total shipments.")

        print("Filtering for undelivered and insured shipments...")
        undelivered_shipments = filter_undelivered_insured_shipments(all_shipments)

        if undelivered_shipments:
            print(f"Found {len(undelivered_shipments)} undelivered and insured shipments.")
            generate_md_report(undelivered_shipments, args.output_file)
        else:
            print("No undelivered and insured shipments found.")

if __name__ == "__main__":
    main()
