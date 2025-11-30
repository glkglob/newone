import unittest
from unittest.mock import patch, MagicMock
import os
import csv
from shipment_reporter import filter_undelivered_insured_shipments, generate_csv_report

class TestShipmentReporter(unittest.TestCase):

    def setUp(self):
        self.mock_shipment_delivered_insured = {
            "easyship_shipment_id": "ES123",
            "created_at": "2023-01-01T12:00:00Z",
            "shipment_state": "delivered",
            "label_state": "printed",
            "courier_tracking_number": "1234567890",
            "insurance": {"is_insured": True},
            "selected_courier": {"name": "USPS"},
            "destination_address": {
                "contact_name": "Dr. Steve Brule",
                "line_1": "179 N Harbor Dr",
                "city": "Redondo Beach",
                "state": "CA",
                "postal_code": "90277",
                "country_alpha2": "US",
            },
            "origin_address": {
                "contact_name": "Sender Name",
                "company_name": "Sender Company",
                "line_1": "118 2nd Street",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "country_alpha2": "US",
            },
            "parcels": [{
                "length": 10,
                "width": 8,
                "height": 4,
                "actual_weight": {"value": 12.5},
            }]
        }
        self.mock_shipment_undelivered_insured = {
            "easyship_shipment_id": "ES456",
            "created_at": "2023-01-02T12:00:00Z",
            "shipment_state": "in_transit",
            "label_state": "printed",
            "courier_tracking_number": "0987654321",
            "insurance": {"is_insured": True},
            "selected_courier": {"name": "UPS"},
            "destination_address": {
                "contact_name": "John Smith",
                "line_1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country_alpha2": "US",
            },
            "origin_address": {
                "contact_name": "ACME Inc.",
                "company_name": "ACME Inc.",
                "line_1": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "postal_code": "90001",
                "country_alpha2": "US",
            },
            "parcels": [{
                "length": 12,
                "width": 10,
                "height": 6,
                "actual_weight": {"value": 15.0},
            }]
        }
        self.mock_shipment_undelivered_uninsured = {
            "easyship_shipment_id": "ES789",
            "shipment_state": "in_transit",
            "insurance": {"is_insured": False},
        }

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
                'shipment_id', 'created_at', 'shipment_state', 'label_state', 'tracking_number', 'is_insured', 'courier',
                'destination_name', 'destination_address_line_1', 'destination_city', 'destination_state', 'destination_postal_code', 'destination_country_alpha2',
                'origin_name', 'origin_company_name', 'origin_address_line_1', 'origin_city', 'origin_state', 'origin_postal_code', 'origin_country_alpha2',
                'parcel_length', 'parcel_width', 'parcel_height', 'parcel_weight'
            ])

            row = next(reader)
            self.assertEqual(row[0], "ES456")
            self.assertEqual(row[1], "2023-01-02T12:00:00Z")
            self.assertEqual(row[3], "printed")


        os.remove(test_filename)

if __name__ == '__main__':
    unittest.main()
