import unittest
from pathlib import Path

from delivery_system import load_delivery_data, simulate_deliveries


ROOT = Path(__file__).parent
ASSIGNMENT_DIR = ROOT / "Python Assignment -2026"
CASE_DIR = ASSIGNMENT_DIR / "Python Assignment(Delivery System Test Cases)"


class DeliverySystemTests(unittest.TestCase):

    def check_case(self, file_path):
        data = load_delivery_data(file_path)
        report = simulate_deliveries(data)

        total_packages = len(data["packages"])
        delivered_count = 0
        delivered_ids = []

        for key in report:
            if key != "best_agent":
                delivered_count = delivered_count + report[key]["packages_delivered"]

                for package_id in report[key]["delivered_package_ids"]:
                    delivered_ids.append(package_id)

                self.assertGreaterEqual(report[key]["total_distance"], 0)
                self.assertGreaterEqual(report[key]["efficiency"], 0)

        expected_ids = []
        for package in data["packages"]:
            expected_ids.append(package["id"])

        self.assertEqual(delivered_count, total_packages)
        self.assertEqual(sorted(delivered_ids), sorted(expected_ids))
        self.assertEqual(len(delivered_ids), len(set(delivered_ids)))

        if total_packages > 0:
            self.assertIn("best_agent", report)

    def test_base_case(self):
        self.check_case(ASSIGNMENT_DIR / "base_case.json")

    def test_provided_cases(self):
        for file_path in sorted(CASE_DIR.glob("test_case_*.json")):
            with self.subTest(case=file_path.name):
                self.check_case(file_path)

    def test_missing_packages_key(self):
        data = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [1, 1]}
        }

        with self.assertRaises(ValueError):
            simulate_deliveries(data)

    def test_unknown_warehouse(self):
        data = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [1, 1]},
            "packages": [
                {"id": "P1", "warehouse": "W9", "destination": [5, 5]}
            ]
        }

        with self.assertRaises(ValueError):
            simulate_deliveries(data)

    def test_empty_agents(self):
        data = {
            "warehouses": {"W1": [0, 0]},
            "agents": {},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": [5, 5]}
            ]
        }

        with self.assertRaises(ValueError):
            simulate_deliveries(data)


if __name__ == "__main__":
    unittest.main()
