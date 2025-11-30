import easyship
import os
import csv
import argparse

def get_all_shipments(client):
    """
    Retrieves all shipments from the EasyPost API, handling pagination.

    Args:
        client: An EasyPostClient instance.

    Returns:
        list: A list of all EasyPost shipment objects.
    """
    all_shipments = []
    shipments_page = client.shipment.all(page_size=100)

    while True:
        all_shipments.extend(shipments_page['shipments'])

        if not shipments_page['has_more']:
            break

        last_id = shipments_page['shipments'][-1].id
        shipments_page = client.shipment.all(
            page_size=100,
            before_id=last_id
        )

    return all_shipments

def filter_undelivered_insured_shipments(shipments):
    """
    Filters a list of shipments for those that are undelivered and insured.

    Args:
        shipments (list): A list of EasyPost shipment objects.

    Returns:
        list: A filtered list of EasyPost shipment objects.
    """
    filtered = []
    for shipment in shipments:
        is_insured = shipment.insurance is not None
        is_delivered = shipment.tracker and shipment.tracker.status == "delivered"

        if is_insured and not is_delivered:
            filtered.append(shipment)

    return filtered

def generate_csv_report(shipments, filename):
    """
    Generates a CSV report of shipments.

    Args:
        shipments (list): A list of EasyPost shipment objects.
        filename (str): The name of the output CSV file.
    """
    if not shipments:
        print("No shipments to generate a report for.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['shipment_id', 'status', 'tracking_code', 'insurance', 'carrier']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for shipment in shipments:
            writer.writerow({
                'shipment_id': shipment.id,
                'status': shipment.tracker.status if shipment.tracker else 'N/A',
                'tracking_code': shipment.tracking_code,
                'insurance': shipment.insurance,
                'carrier': shipment.selected_rate.carrier if shipment.selected_rate else 'N/A'
            })
    print(f"Report generated successfully: {filename}")


def main():
    """
    Main function to retrieve, filter, and report on shipments.
    """
    parser = argparse.ArgumentParser(description="Retrieve and report on EasyPost shipments.")
    parser.add_argument('--api-key', help="Your EasyPost API key.")
    parser.add_argument('--output-file', default='undelivered_insured_shipments.csv', help="The path to the output CSV file.")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("EASYPOST_API_KEY", "sand_vRDxb71bEvRPurPeand1SIE")
    if not api_key:
        print("Error: API key not provided. Please use the --api-key argument or set the EASYPOST_API_KEY environment variable.")
        return

    try:
        client = easypost.EasyPostClient(api_key)

        print("Retrieving all shipments...")
        all_shipments = get_all_shipments(client)
        print(f"Found {len(all_shipments)} total shipments.")

        print("Filtering for undelivered and insured shipments...")
        undelivered_shipments = filter_undelivered_insured_shipments(all_shipments)

        if undelivered_shipments:
            print(f"Found {len(undelivered_shipments)} undelivered and insured shipments.")
            generate_csv_report(undelivered_shipments, args.output_file)
        else:
            print("No undelivered and insured shipments found.")

    except easypost.errors.api.api_error.ApiError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
