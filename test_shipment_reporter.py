import unittest
from unittest.mock import patch, MagicMock
import os
import json
from shipment_reporter import filter_undelivered_insured_shipments, generate_md_report

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
        }
        self.mock_shipment_undelivered_insured = {
            "easyship_shipment_id": "ES456",
            "created_at": "2023-01-02T12:00:00Z",
            "shipment_state": "in_transit",
            "label_state": "printed",
            "courier_tracking_number": "0987654321",
            "insurance": {"is_insured": True},
            "selected_courier": {"name": "UPS"},
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

    def test_generate_md_report(self):
        test_filename = "test_report.md"
        shipments = [self.mock_shipment_undelivered_insured]

        generate_md_report(shipments, test_filename)

        self.assertTrue(os.path.exists(test_filename))

        with open(test_filename, 'r') as f:
            content = f.read()
            self.assertIn("# Undelivered and Insured Shipments Report", content)
            self.assertIn("## Shipment ID: `ES456`", content)
            self.assertIn("- **Status:** in_transit", content)
            self.assertIn("```json", content)

        os.remove(test_filename)

if __name__ == '__main__':
    unittest.main()
