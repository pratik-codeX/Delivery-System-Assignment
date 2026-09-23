import unittest
from pathlib import Path

from delivery_system import load_delivery_data, simulate_deliveries


ROOT = Path(__file__).parent
ASSIGNMENT_DIR = ROOT / "Python Assignment -2026"
CASE_DIR = ASSIGNMENT_DIR / "Python Assignment(Delivery System Test Cases)"


class DeliverySystemTests(unittest.TestCase):
    def check_case(self, path: Path) -> None:
        data = load_delivery_data(path)
        report = simulate_deliveries(data)

        agent_entries = {
            agent_id: entry
            for agent_id, entry in report.items()
            if agent_id != "best_agent"
        }

        delivered_count = sum(entry["packages_delivered"] for entry in agent_entries.values())
        delivered_ids = [
            package_id
            for entry in agent_entries.values()
            for package_id in entry["delivered_package_ids"]
        ]

        self.assertEqual(delivered_count, len(data["packages"]), path)
        self.assertEqual(sorted(delivered_ids), sorted(package["id"] for package in data["packages"]))
        self.assertEqual(len(delivered_ids), len(set(delivered_ids)))

        for entry in agent_entries.values():
            self.assertGreaterEqual(entry["total_distance"], 0)
            self.assertGreaterEqual(entry["efficiency"], 0)
            if entry["packages_delivered"]:
                self.assertAlmostEqual(
                    entry["efficiency"],
                    round(entry["total_distance"] / entry["packages_delivered"], 2),
                )

        active_agents = [
            agent_id
            for agent_id, entry in agent_entries.items()
            if entry["packages_delivered"] > 0
        ]
        self.assertIn(report["best_agent"], active_agents)

    def test_base_case(self) -> None:
        self.check_case(ASSIGNMENT_DIR / "base_case.json")

    def test_provided_cases(self) -> None:
        for path in sorted(CASE_DIR.glob("test_case_*.json")):
            with self.subTest(case=path.name):
                self.check_case(path)


if __name__ == "__main__":
    unittest.main()
