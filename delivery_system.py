# FastBox Delivery System Assignment
# Author : Pratik Nanaso Raut
# Date   : 23/9/2026

import csv
import json
import math
import sys


DEFAULT_INPUT = "Python Assignment -2026/base_case.json"
DEFAULT_OUTPUT = "report.json"


class DeliverySystem:

    # ---------------------------------------------------------
    # Function Name : __init__
    # Description   : It stores input and output file names
    # Input         : Input JSON file path, output report file path
    # Output        : None
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def __init__(self, input_file=DEFAULT_INPUT, output_file=DEFAULT_OUTPUT):
        self.input_file = input_file
        self.output_file = output_file

    # ---------------------------------------------------------
    # Function Name : load_data
    # Description   : It reads delivery data from JSON file
    # Input         : JSON file path
    # Output        : Dictionary containing delivery data
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def load_data(self, file_name=None):
        if file_name is None:
            file_name = self.input_file

        try:
            file = open(file_name, "r")
            data = json.load(file)
            file.close()
        except FileNotFoundError:
            raise ValueError("Input file not found")
        except json.JSONDecodeError:
            raise ValueError("Input file is not a valid JSON file")

        if type(data) != dict:
            raise ValueError("Input data should be a JSON object")

        return data

    # ---------------------------------------------------------
    # Function Name : check_point
    # Description   : It checks whether location has valid x and y values
    # Input         : Location value and field name
    # Output        : Validated location
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def check_point(self, point, name):
        if type(point) != list:
            raise ValueError(name + " should be a list")

        if len(point) != 2:
            raise ValueError(name + " should contain x and y values")

        if type(point[0]) not in [int, float] or type(point[1]) not in [int, float]:
            raise ValueError(name + " should contain numeric values")

        return point

    # ---------------------------------------------------------
    # Function Name : check_main_data
    # Description   : It checks required keys from input JSON data
    # Input         : Complete delivery data
    # Output        : None
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def check_main_data(self, data):
        if type(data) != dict:
            raise ValueError("Input data should be a dictionary")

        if "warehouses" not in data:
            raise ValueError("warehouses key is missing")

        if "agents" not in data:
            raise ValueError("agents key is missing")

        if "packages" not in data:
            raise ValueError("packages key is missing")

        if type(data["packages"]) != list:
            raise ValueError("packages should be a list")

    # ---------------------------------------------------------
    # Function Name : prepare_locations
    # Description   : It converts warehouse or agent locations into simple format
    # Input         : Warehouse or agent data from JSON file
    # Output        : Dictionary of id and location
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def prepare_locations(self, data, title):
        locations = {}

        # Most test cases store data like: "W1": [0, 0]
        if type(data) == dict:
            for name in data:
                if type(name) != str:
                    raise ValueError(title + " id should be a string")

                locations[name] = self.check_point(data[name], title + " " + name)

        # base_case.json stores data like: {"id": "W1", "location": [0, 0]}
        elif type(data) == list:
            for item in data:
                if type(item) != dict:
                    raise ValueError(title + " item should be a dictionary")

                if "id" not in item or "location" not in item:
                    raise ValueError(title + " item should contain id and location")

                if type(item["id"]) != str:
                    raise ValueError(title + " id should be a string")

                locations[item["id"]] = self.check_point(item["location"], title + " " + item["id"])

        else:
            raise ValueError(title + " should be a dictionary or list")

        return locations

    # ---------------------------------------------------------
    # Function Name : prepare_packages
    # Description   : It converts package details into one common format
    # Input         : Package data from JSON file
    # Output        : List of packages with id, warehouse and destination
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def prepare_packages(self, data):
        packages = []
        ids = []

        for package in data:
            if type(package) != dict:
                raise ValueError("package should be a dictionary")

            if "id" not in package:
                raise ValueError("package id is missing")

            if type(package["id"]) != str:
                raise ValueError("package id should be a string")

            if package["id"] in ids:
                raise ValueError("duplicate package id found")

            ids.append(package["id"])

            item = {}
            item["id"] = package["id"]

            # Some files use warehouse and base_case.json uses warehouse_id.
            if "warehouse" in package:
                item["warehouse"] = package["warehouse"]
            elif "warehouse_id" in package:
                item["warehouse"] = package["warehouse_id"]
            else:
                raise ValueError("warehouse is missing for package " + package["id"])

            if type(item["warehouse"]) != str:
                raise ValueError("warehouse id should be a string")

            if "destination" not in package:
                raise ValueError("destination is missing for package " + package["id"])

            item["destination"] = self.check_point(package["destination"], "destination of " + package["id"])
            packages.append(item)

        return packages

    # ---------------------------------------------------------
    # Function Name : calculate_distance
    # Description   : It calculates Euclidean distance between two points
    # Input         : Start location and end location
    # Output        : Distance between both points
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def calculate_distance(self, start, end):
        x = end[0] - start[0]
        y = end[1] - start[1]

        distance = math.sqrt((x * x) + (y * y))
        return distance

    # ---------------------------------------------------------
    # Function Name : find_nearest_agent
    # Description   : It finds nearest agent from given warehouse location
    # Input         : Warehouse location and all agent locations
    # Output        : Agent id of nearest agent
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def find_nearest_agent(self, warehouse, agents):
        if len(agents) == 0:
            raise ValueError("No agents available")

        nearest_agent = None
        nearest_distance = None

        for agent in agents:
            distance = self.calculate_distance(agents[agent], warehouse)

            if nearest_distance is None:
                nearest_distance = distance
                nearest_agent = agent
            elif distance < nearest_distance:
                nearest_distance = distance
                nearest_agent = agent
            elif distance == nearest_distance and agent < nearest_agent:
                nearest_agent = agent

        return nearest_agent

    # ---------------------------------------------------------
    # Function Name : create_empty_report
    # Description   : It creates blank report data for all agents
    # Input         : Agents dictionary
    # Output        : Report dictionary with default values
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def create_empty_report(self, agents):
        report = {}

        for agent in agents:
            report[agent] = {}
            report[agent]["packages_delivered"] = 0
            report[agent]["delivered_package_ids"] = []
            report[agent]["total_distance"] = 0.0
            report[agent]["efficiency"] = 0.0

        return report

    # ---------------------------------------------------------
    # Function Name : find_best_agent
    # Description   : It finds agent with lowest average distance per package
    # Input         : Final report dictionary
    # Output        : Best agent id
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def find_best_agent(self, report):
        best_agent = None
        best_average = None
        best_distance = None

        for agent in report:
            count = report[agent]["packages_delivered"]

            if count > 0:
                average = report[agent]["efficiency"]
                distance = report[agent]["total_distance"]

                if best_agent is None:
                    best_agent = agent
                    best_average = average
                    best_distance = distance
                elif average < best_average:
                    best_agent = agent
                    best_average = average
                    best_distance = distance
                elif average == best_average:
                    if distance < best_distance:
                        best_agent = agent
                        best_distance = distance
                    elif distance == best_distance and agent < best_agent:
                        best_agent = agent

        return best_agent

    # ---------------------------------------------------------
    # Function Name : simulate_deliveries
    # Description   : It assigns packages, calculates distance and prepares report
    # Input         : Delivery data dictionary
    # Output        : Final report dictionary
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def simulate_deliveries(self, data):
        self.check_main_data(data)

        warehouses = self.prepare_locations(data["warehouses"], "warehouse")
        agents = self.prepare_locations(data["agents"], "agent")
        packages = self.prepare_packages(data["packages"])

        if len(agents) == 0 and len(packages) > 0:
            raise ValueError("No agents available for delivery")

        # Current position changes after each delivery.
        positions = {}
        for agent in agents:
            positions[agent] = agents[agent]

        report = self.create_empty_report(agents)

        for package in packages:
            package_id = package["id"]
            warehouse_id = package["warehouse"]

            if warehouse_id not in warehouses:
                raise ValueError("warehouse " + warehouse_id + " not found")

            warehouse = warehouses[warehouse_id]
            destination = package["destination"]

            # Package is assigned to the nearest agent from the warehouse.
            agent = self.find_nearest_agent(warehouse, agents)

            # Total trip = current agent position to warehouse plus warehouse to destination.
            pickup_distance = self.calculate_distance(positions[agent], warehouse)
            delivery_distance = self.calculate_distance(warehouse, destination)
            total_distance = pickup_distance + delivery_distance

            report[agent]["packages_delivered"] = report[agent]["packages_delivered"] + 1
            report[agent]["delivered_package_ids"].append(package_id)
            report[agent]["total_distance"] = report[agent]["total_distance"] + total_distance

            # Agent reaches destination after delivering the package.
            positions[agent] = destination

        for agent in report:
            count = report[agent]["packages_delivered"]
            total_distance = round(report[agent]["total_distance"], 2)
            report[agent]["total_distance"] = total_distance

            if count > 0:
                report[agent]["efficiency"] = round(total_distance / count, 2)
            else:
                report[agent]["efficiency"] = 0.0

        report["best_agent"] = self.find_best_agent(report)
        return report

    # ---------------------------------------------------------
    # Function Name : save_report
    # Description   : It saves final delivery report into report.json file
    # Input         : Report dictionary and output file name
    # Output        : report.json file
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def save_report(self, report, file_name=None):
        if file_name is None:
            file_name = self.output_file

        try:
            file = open(file_name, "w")
            json.dump(report, file, indent=2)
            file.write("\n")
            file.close()
        except OSError:
            raise ValueError("Unable to write report file")

    # ---------------------------------------------------------
    # Function Name : export_top_performer
    # Description   : It exports best agent details into CSV file
    # Input         : Report dictionary and CSV file name
    # Output        : CSV file with best agent details
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def export_top_performer(self, report, file_name):
        best_agent = report["best_agent"]

        if best_agent is None:
            return

        try:
            file = open(file_name, "w", newline="")
            writer = csv.writer(file)

            writer.writerow(["agent_id", "packages_delivered", "total_distance", "efficiency"])
            writer.writerow([
                best_agent,
                report[best_agent]["packages_delivered"],
                report[best_agent]["total_distance"],
                report[best_agent]["efficiency"]
            ])

            file.close()
        except OSError:
            raise ValueError("Unable to write CSV file")

    # ---------------------------------------------------------
    # Function Name : run
    # Description   : It executes the complete delivery system flow
    # Input         : None
    # Output        : Creates report.json file
    # Author        : Pratik Nanaso Raut
    # Date          : 23/9/2026
    # ---------------------------------------------------------
    def run(self):
        data = self.load_data()
        report = self.simulate_deliveries(data)
        self.save_report(report)

        print("Report saved to", self.output_file)
        print("Best agent:", report["best_agent"])


# ---------------------------------------------------------
# Function Name : load_delivery_data
# Description   : It loads JSON data, used by test cases
# Input         : JSON file path
# Output        : Dictionary containing delivery data
# Author        : Pratik Nanaso Raut
# Date          : 23/9/2026
# ---------------------------------------------------------
def load_delivery_data(file_name):
    app = DeliverySystem(file_name)
    return app.load_data(file_name)


# ---------------------------------------------------------
# Function Name : simulate_deliveries
# Description   : It simulates deliveries, used by test cases
# Input         : Delivery data dictionary
# Output        : Final report dictionary
# Author        : Pratik Nanaso Raut
# Date          : 23/9/2026
# ---------------------------------------------------------
def simulate_deliveries(data):
    app = DeliverySystem()
    return app.simulate_deliveries(data)


# ---------------------------------------------------------
# Function Name : main
# Description   : It starts the program and handles command line input
# Input         : Optional input file, output file and CSV file from terminal
# Output        : Creates report.json and optional CSV file
# Author        : Pratik Nanaso Raut
# Date          : 23/9/2026
# ---------------------------------------------------------
def main():
    input_file = DEFAULT_INPUT
    output_file = DEFAULT_OUTPUT
    csv_file = None

    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    if len(sys.argv) > 3:
        csv_file = sys.argv[3]

    try:
        app = DeliverySystem(input_file, output_file)
        data = app.load_data()
        report = app.simulate_deliveries(data)
        app.save_report(report)

        if csv_file is not None:
            app.export_top_performer(report, csv_file)

        print("Report saved to", output_file)
        print("Best agent:", report["best_agent"])
    except ValueError as error:
        print("Error:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
