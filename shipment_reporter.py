import requests
import os
import csv
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

def generate_csv_report(shipments, filename):
    """
    Generates a CSV report of shipments.

    Args:
        shipments (list): A list of Easyship shipment objects.
        filename (str): The name of the output CSV file.
    """
    if not shipments:
        print("No shipments to generate a report for.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'shipment_id', 'created_at', 'shipment_state', 'label_state', 'tracking_number', 'is_insured', 'courier',
            'destination_name', 'destination_address_line_1', 'destination_city', 'destination_state', 'destination_postal_code', 'destination_country_alpha2',
            'origin_name', 'origin_company_name', 'origin_address_line_1', 'origin_city', 'origin_state', 'origin_postal_code', 'origin_country_alpha2',
            'parcel_length', 'parcel_width', 'parcel_height', 'parcel_weight'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for shipment in shipments:
            dest = shipment.get("destination_address", {})
            origin = shipment.get("origin_address", {})
            parcels = shipment.get("parcels")
            parcel = parcels[0] if parcels else {}

            writer.writerow({
                'shipment_id': shipment.get('easyship_shipment_id'),
                'created_at': shipment.get('created_at'),
                'shipment_state': shipment.get('shipment_state'),
                'label_state': shipment.get('label_state'),
                'tracking_number': shipment.get('courier_tracking_number'),
                'is_insured': shipment.get("insurance", {}).get("is_insured"),
                'courier': shipment.get('selected_courier', {}).get('name'),
                'destination_name': dest.get('contact_name'),
                'destination_address_line_1': dest.get('line_1'),
                'destination_city': dest.get('city'),
                'destination_state': dest.get('state'),
                'destination_postal_code': dest.get('postal_code'),
                'destination_country_alpha2': dest.get('country_alpha2'),
                'origin_name': origin.get('contact_name'),
                'origin_company_name': origin.get('company_name'),
                'origin_address_line_1': origin.get('line_1'),
                'origin_city': origin.get('city'),
                'origin_state': origin.get('state'),
                'origin_postal_code': origin.get('postal_code'),
                'origin_country_alpha2': origin.get('country_alpha2'),
                'parcel_length': parcel.get('length'),
                'parcel_width': parcel.get('width'),
                'parcel_height': parcel.get('height'),
                'parcel_weight': parcel.get('actual_weight', {}).get('value'),
            })
    print(f"Report generated successfully: {filename}")


def main():
    """
    Main function to retrieve, filter, and report on shipments.
    """
    parser = argparse.ArgumentParser(description="Retrieve and report on Easyship shipments.")
    parser.add_argument('--api-key', help="Your Easyship API key.")
    parser.add_argument('--output-file', default='undelivered_insured_shipments.csv', help="The path to the output CSV file.")
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
            generate_csv_report(undelivered_shipments, args.output_file)
        else:
            print("No undelivered and insured shipments found.")

if __name__ == "__main__":
    main()
