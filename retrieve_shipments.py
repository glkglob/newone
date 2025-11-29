import requests
import os

# Get API key from environment variable
api_key = os.getenv("EASYSHIP_API_KEY")
if not api_key:
    raise ValueError("Missing EASYSHIP_API_KEY environment variable. Please set it before running the script.")

BASE_URL = "https://public-api.easyship.com/2024-09"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

def get_all_shipments():
    """Fetches all shipments from the Easyship API, handling pagination."""
    all_shipments = []
    page = 1
    has_next_page = True

    while has_next_page:
        try:
            response = requests.get(
                f"{BASE_URL}/shipments",
                headers=headers,
                params={"page": page, "per_page": 100}
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            
            shipments = data.get("shipments", [])
            all_shipments.extend(shipments)

            meta = data.get("meta", {})
            has_next_page = meta.get("has_next_page", False)
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while communicating with the Easyship API: {e}")
            return None # Exit the function if there's a request error

    return all_shipments


def main():
    """Main function to retrieve and filter shipments."""
    print("Retrieving shipments from Easyship...")
    shipments = get_all_shipments()

    if shipments is None:
        print("Could not retrieve shipments due to an API error.")
        return

    print(f"Total shipments retrieved: {len(shipments)}")

    undelivered_insured_shipments = []
    for shipment in shipments:
        is_insured = shipment.get("insurance", {}).get("is_insured", False)
        status = shipment.get("shipment_state")

        # Filter for shipments that are insured and not yet delivered
        if is_insured and status != 'delivered':
            undelivered_insured_shipments.append(shipment)

    if undelivered_insured_shipments:
        print("\n--- Undelivered and Insured Shipments ---")
        for shipment in undelivered_insured_shipments:
            shipment_id = shipment.get("easyship_shipment_id")
            status = shipment.get("shipment_state")
            print(f"  Shipment ID: {shipment_id}, Status: {status}, Insured: True")
        print("----------------------------------------")
    else:
        print("No undelivered and insured shipments found.")


if __name__ == "__main__":
    main()
