import easypost
import os


def get_undelivered_insured_shipments():
    """
    Retrieves shipments that have not been successfully delivered and have insurance.

    Returns:
        list: A list of EasyPost shipment objects.
    """
    try:
        # Set the API key
        client = easypost.EasyPostClient(os.getenv("EASYPOST_API_KEY", "sand_vRDxb71bEvRPurPeand1SIE"))

        undelivered_insured_shipments = []
        shipments_page = client.shipment.all(page_size=100)

        while True:
            for shipment in shipments_page['shipments']:
                # Check if the shipment is insured
                is_insured = shipment.insurance is not None

                # Check if the shipment has been delivered
                is_delivered = False
                if shipment.tracker:
                    if shipment.tracker.status == "delivered":
                        is_delivered = True

                # Add to the list if it's not delivered and is insured
                if is_insured and not is_delivered:
                    undelivered_insured_shipments.append(shipment)

            if shipments_page['has_more']:
                last_id = shipments_page['shipments'][-1].id
                shipments_page = client.shipment.all(
                    page_size=100,
                    before_id=last_id
                )
            else:
                break

        return undelivered_insured_shipments

    except easypost.errors.api.api_error.ApiError as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    undelivered_shipments = get_undelivered_insured_shipments()

    if undelivered_shipments:
        print("Found undelivered and insured shipments:")
        for shipment in undelivered_shipments:
            print(f"  - Shipment ID: {shipment.id}, Status: {shipment.tracker.status}")
    else:
        print("No undelivered and insured shipments found.")
