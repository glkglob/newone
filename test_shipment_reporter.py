import unittest
from unittest.mock import MagicMock, patch
import os
import csv
from shipment_reporter import filter_undelivered_insured_shipments, generate_csv_report

class TestShipmentReporter(unittest.TestCase):

    def setUp(self):
        # Create a mock for the shipment object
        self.mock_shipment_delivered_insured = MagicMock()
        self.mock_shipment_delivered_insured.insurance = 100.00
        self.mock_shipment_delivered_insured.tracker.status = "delivered"
        self.mock_shipment_delivered_insured.id = "shp_123"
        self.mock_shipment_delivered_insured.tracking_code = "1234567890"
        self.mock_shipment_delivered_insured.selected_rate.carrier = "USPS"
        self.mock_shipment_delivered_insured.to_address.name = "Dr. Steve Brule"
        self.mock_shipment_delivered_insured.to_address.street1 = "179 N Harbor Dr"
        self.mock_shipment_delivered_insured.to_address.city = "Redondo Beach"
        self.mock_shipment_delivered_insured.to_address.state = "CA"
        self.mock_shipment_delivered_insured.to_address.zip = "90277"
        self.mock_shipment_delivered_insured.to_address.country = "US"
        self.mock_shipment_delivered_insured.from_address.name = "EasyPost"
        self.mock_shipment_delivered_insured.from_address.company = "EasyPost"
        self.mock_shipment_delivered_insured.from_address.street1 = "118 2nd Street"
        self.mock_shipment_delivered_insured.from_address.city = "San Francisco"
        self.mock_shipment_delivered_insured.from_address.state = "CA"
        self.mock_shipment_delivered_insured.from_address.zip = "94105"
        self.mock_shipment_delivered_insured.from_address.country = "US"
        self.mock_shipment_delivered_insured.parcel.length = 10
        self.mock_shipment_delivered_insured.parcel.width = 8
        self.mock_shipment_delivered_insured.parcel.height = 4
        self.mock_shipment_delivered_insured.parcel.weight = 12.5

        self.mock_shipment_undelivered_insured = MagicMock()
        self.mock_shipment_undelivered_insured.insurance = 100.00
        self.mock_shipment_undelivered_insured.tracker.status = "in_transit"
        self.mock_shipment_undelivered_insured.id = "shp_456"
        self.mock_shipment_undelivered_insured.tracking_code = "0987654321"
        self.mock_shipment_undelivered_insured.selected_rate.carrier = "UPS"
        self.mock_shipment_undelivered_insured.to_address.name = "John Smith"
        self.mock_shipment_undelivered_insured.to_address.street1 = "123 Main St"
        self.mock_shipment_undelivered_insured.to_address.city = "New York"
        self.mock_shipment_undelivered_insured.to_address.state = "NY"
        self.mock_shipment_undelivered_insured.to_address.zip = "10001"
        self.mock_shipment_undelivered_insured.to_address.country = "US"
        self.mock_shipment_undelivered_insured.from_address.name = "ACME Inc."
        self.mock_shipment_undelivered_insured.from_address.company = "ACME Inc."
        self.mock_shipment_undelivered_insured.from_address.street1 = "456 Oak Ave"
        self.mock_shipment_undelivered_insured.from_address.city = "Los Angeles"
        self.mock_shipment_undelivered_insured.from_address.state = "CA"
        self.mock_shipment_undelivered_insured.from_address.zip = "90001"
        self.mock_shipment_undelivered_insured.from_address.country = "US"
        self.mock_shipment_undelivered_insured.parcel.length = 12
        self.mock_shipment_undelivered_insured.parcel.width = 10
        self.mock_shipment_undelivered_insured.parcel.height = 6
        self.mock_shipment_undelivered_insured.parcel.weight = 15.0


        self.mock_shipment_undelivered_uninsured = MagicMock()
        self.mock_shipment_undelivered_uninsured.insurance = None
        self.mock_shipment_undelivered_uninsured.tracker.status = "in_transit"

        self.shipments = [
            self.mock_shipment_delivered_insured,
            self.mock_shipment_undelivered_insured,
            self.mock_shipment_undelivered_uninsured,
        ]

    def test_filter_undelivered_insured_shipments(self):
        filtered_shipments = filter_undelivered_insured_shipments(self.shipments)
        self.assertEqual(len(filtered_shipments), 1)
        self.assertIn(self.mock_shipment_undelivered_insured, filtered_shipments)
        self.assertNotIn(self.mock_shipment_delivered_insured, filtered_shipments)
        self.assertNotIn(self.mock_shipment_undelivered_uninsured, filtered_shipments)

    def test_generate_csv_report(self):
        test_filename = "test_report.csv"
        shipments = [self.mock_shipment_undelivered_insured]

        generate_csv_report(shipments, test_filename)

        self.assertTrue(os.path.exists(test_filename))

        with open(test_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.assertEqual(header, [
                'shipment_id', 'status', 'tracking_code', 'insurance', 'carrier',
                'to_name', 'to_street1', 'to_city', 'to_state', 'to_zip', 'to_country',
                'from_name', 'from_company', 'from_street1', 'from_city', 'from_state', 'from_zip', 'from_country',
                'parcel_length', 'parcel_width', 'parcel_height', 'parcel_weight'
            ])

            row = next(reader)
            self.assertEqual(row[0], "shp_456")

        os.remove(test_filename)

if __name__ == '__main__':
    unittest.main()
