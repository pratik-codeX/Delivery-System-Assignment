"""FastBox delivery system simulator.

Usage:
    python3 delivery_system.py [input_json] [-o report.json] [--top-csv top_agent.csv]

The simulator reads a JSON input file, assigns each package to the nearest
agent by warehouse distance, simulates pickup and delivery, and writes a JSON
report.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


Point = tuple[float, float]


DEFAULT_INPUT = Path("Python Assignment -2026/base_case.json")
DEFAULT_OUTPUT = Path("report.json")


def parse_point(value: Any, label: str) -> Point:
    """Validate and normalize a two-number coordinate."""
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a [x, y] coordinate")

    x, y = value
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError(f"{label} must contain numeric x and y values")

    return float(x), float(y)


def load_delivery_data(path: str | Path) -> dict[str, Any]:
    """Read a JSON input file from disk."""
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input JSON must contain an object at the top level")

    return data


def normalize_locations(raw_locations: Any, section_name: str) -> dict[str, Point]:
    """Support both {'W1': [0, 0]} and [{'id': 'W1', 'location': [0, 0]}]."""
    locations: dict[str, Point] = {}

    if isinstance(raw_locations, dict):
        items = raw_locations.items()
        for location_id, coordinates in items:
            if not isinstance(location_id, str):
                raise ValueError(f"{section_name} ids must be strings")
            locations[location_id] = parse_point(
                coordinates,
                f"{section_name}.{location_id}",
            )
        return locations

    if isinstance(raw_locations, list):
        for index, item in enumerate(raw_locations):
            if not isinstance(item, dict):
                raise ValueError(f"{section_name}[{index}] must be an object")

            location_id = item.get("id")
            if not isinstance(location_id, str):
                raise ValueError(f"{section_name}[{index}].id must be a string")

            locations[location_id] = parse_point(
                item.get("location"),
                f"{section_name}.{location_id}.location",
            )
        return locations

    raise ValueError(f"{section_name} must be an object or a list")


def normalize_packages(raw_packages: Any) -> list[dict[str, Any]]:
    """Normalize package objects from either warehouse or warehouse_id inputs."""
    if not isinstance(raw_packages, list):
        raise ValueError("packages must be a list")

    packages: list[dict[str, Any]] = []
    seen_package_ids: set[str] = set()

    for index, item in enumerate(raw_packages):
        if not isinstance(item, dict):
            raise ValueError(f"packages[{index}] must be an object")

        package_id = item.get("id")
        if not isinstance(package_id, str):
            raise ValueError(f"packages[{index}].id must be a string")
        if package_id in seen_package_ids:
            raise ValueError(f"Duplicate package id: {package_id}")
        seen_package_ids.add(package_id)

        warehouse_id = item.get("warehouse", item.get("warehouse_id"))
        if not isinstance(warehouse_id, str):
            raise ValueError(f"{package_id} must include warehouse or warehouse_id")

        packages.append(
            {
                "id": package_id,
                "warehouse_id": warehouse_id,
                "destination": parse_point(item.get("destination"), f"{package_id}.destination"),
            }
        )

    return packages


def distance(start: Point, end: Point) -> float:
    """Return Euclidean distance between two points."""
    return math.hypot(end[0] - start[0], end[1] - start[1])


def nearest_agent(warehouse_location: Point, agent_locations: dict[str, Point]) -> str:
    """Pick the closest agent to a warehouse, using agent id as a tie-breaker."""
    if not agent_locations:
        raise ValueError("At least one agent is required")

    return min(
        agent_locations,
        key=lambda agent_id: (distance(agent_locations[agent_id], warehouse_location), agent_id),
    )


def simulate_deliveries(data: dict[str, Any]) -> dict[str, Any]:
    """Assign packages, simulate travel, and build the final report."""
    warehouses = normalize_locations(data.get("warehouses"), "warehouses")
    agents = normalize_locations(data.get("agents"), "agents")
    packages = normalize_packages(data.get("packages"))

    agent_positions = dict(agents)
    agent_reports: dict[str, dict[str, Any]] = {
        agent_id: {
            "packages_delivered": 0,
            "delivered_package_ids": [],
            "total_distance": 0.0,
            "efficiency": 0.0,
        }
        for agent_id in agents
    }

    for package in packages:
        warehouse_id = package["warehouse_id"]
        if warehouse_id not in warehouses:
            raise ValueError(f"Unknown warehouse '{warehouse_id}' for package {package['id']}")

        warehouse_location = warehouses[warehouse_id]
        agent_id = nearest_agent(warehouse_location, agents)
        pickup_distance = distance(agent_positions[agent_id], warehouse_location)
        delivery_distance = distance(warehouse_location, package["destination"])
        trip_distance = pickup_distance + delivery_distance

        report_entry = agent_reports[agent_id]
        report_entry["packages_delivered"] += 1
        report_entry["delivered_package_ids"].append(package["id"])
        report_entry["total_distance"] += trip_distance
        agent_positions[agent_id] = package["destination"]

    for report_entry in agent_reports.values():
        delivered_count = report_entry["packages_delivered"]
        report_entry["total_distance"] = round(report_entry["total_distance"], 2)
        report_entry["efficiency"] = (
            round(report_entry["total_distance"] / delivered_count, 2)
            if delivered_count
            else 0.0
        )

    active_agents = [
        agent_id
        for agent_id, report_entry in agent_reports.items()
        if report_entry["packages_delivered"] > 0
    ]
    best_agent = (
        min(
            active_agents,
            key=lambda agent_id: (
                agent_reports[agent_id]["efficiency"],
                agent_reports[agent_id]["total_distance"],
                agent_id,
            ),
        )
        if active_agents
        else None
    )

    return {**agent_reports, "best_agent": best_agent}


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Write the report JSON."""
    destination = Path(output_path)
    with destination.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")


def export_top_performer(report: dict[str, Any], output_path: str | Path) -> None:
    """Optional bonus: export the most efficient agent to a CSV file."""
    best_agent = report.get("best_agent")
    if best_agent is None:
        return

    best_agent_report = report[best_agent]
    with Path(output_path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["agent_id", "packages_delivered", "total_distance", "efficiency"])
        writer.writerow(
            [
                best_agent,
                best_agent_report["packages_delivered"],
                best_agent_report["total_distance"],
                best_agent_report["efficiency"],
            ]
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate one day of FastBox deliveries.")
    parser.add_argument(
        "input_json",
        nargs="?",
        default=DEFAULT_INPUT,
        help=f"Input JSON file. Defaults to {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Report output path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--top-csv",
        help="Optional bonus CSV path for exporting the top performer.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data = load_delivery_data(args.input_json)
    report = simulate_deliveries(data)
    write_report(report, args.output)

    if args.top_csv:
        export_top_performer(report, args.top_csv)

    print(f"Report saved to {args.output}")
    if report["best_agent"] is not None:
        print(f"Best agent: {report['best_agent']}")


if __name__ == "__main__":
    main()
