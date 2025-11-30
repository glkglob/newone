import requests
import os
import json

def get_all_shipments(api_key):
    """Fetches all shipments from the Easyship API, handling pagination."""
    all_shipments = []
    page = 1
    has_next_page = True
    base_url = "https://public-api.easyship.com/2024-09"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    while has_next_page:
        try:
            response = requests.get(
                f"{base_url}/shipments",
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
            print(f"An error occurred while communicating with the Easyship API: {e}")
            return None
    return all_shipments

def generate_markdown_report(shipments):
    """Generates a Markdown report from a list of shipments."""
    undelivered_insured_shipments = []
    for shipment in shipments:
        is_insured = shipment.get("insurance", {}).get("is_insured", False)
        status = shipment.get("shipment_state")
        if is_insured and status != 'delivered':
            undelivered_insured_shipments.append(shipment)

    if not undelivered_insured_shipments:
        print("No undelivered and insured shipments found.")
        return

    with open("undelivered_insured_shipments.md", "w") as f:
        f.write("# Undelivered and Insured Shipments\n\n")
        for shipment in undelivered_insured_shipments:
            f.write(f"## Shipment ID: {shipment.get('easyship_shipment_id')}\n\n")
            f.write(f"- **Status:** {shipment.get('shipment_state')}\n")
            f.write(f"- **Insured:** {shipment.get('insurance', {}).get('is_insured')}\n")
            f.write("### Details:\n")
            f.write("```json\n")
            f.write(json.dumps(shipment, indent=2))
            f.write("\n```\n\n")

def main():
    """Main function to retrieve shipments and generate a report."""
    api_key = os.getenv("EASYSHIP_API_KEY")
    if not api_key:
        raise ValueError("Missing EASYSHIP_API_KEY environment variable.")

    print("Retrieving shipments from Easyship...")
    shipments = get_all_shipments(api_key)

    if shipments is None:
        print("Could not retrieve shipments due to an API error.")
        return

    print(f"Total shipments retrieved: {len(shipments)}")
    generate_markdown_report(shipments)

if __name__ == "__main__":
    main()
