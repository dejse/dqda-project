import json
import csv
from pathlib import Path
from typing import Dict
import gc

SCHEMA = [
    "id", "description", "PRODUCT_ID", "HEADING", "BODY_DYN", "PRICE", "YEAR_MODEL",
    "MILEAGE", "CAR_MODEL/MAKE", "CAR_MODEL/MODEL", "CAR_TYPE", "NO_OF_OWNERS",
    "NOOFSEATS", "ENGINE/EFFECT", "ENGINE/FUEL_RESOLVED", "TRANSMISSION_RESOLVED",
    "CONDITION_RESOLVED", "WARRANTY_RESOLVED", "PUBLISHED_String", "COUNTRY",
    "COORDINATES", "POSTCODE", "STATE", "DISTRICT", "ADDRESS", "LOCATION",
    "ORGNAME", "fnmmocount", "UPSELLING_AD_SEARCHRESULT", "ISPRIVATE", "EQUIPMENT_RESOLVED",
]
clean_names = SCHEMA[:]
clean_names[8] = "brand"
clean_names[9] = "model"
clean_names[13] = "engine_effect"
clean_names[14] = "engine_fuel_resolved"
clean_names = [item.lower() for item in clean_names]


def get_row_from_json_item(item: Dict) -> Dict:
    """
    Extract relevant data from Willhaben JSON element and return a row dict
    """
    row = {"id": item["id"], "description": item["description"]}
    for el in item["attributes"]["attribute"]:
        if el["name"] in SCHEMA:
            name = el["name"]
            value = el["values"][0]
            if name in "EQUIPMENT_RESOLVED":
                value = "|".join(el["values"])
            row.update({name: value})
    return row


if __name__ == "__main__":
    # Open CSV File and prep it
    csv_file = open("./data/data_.csv", "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, dialect="excel", delimiter=";", fieldnames=SCHEMA)
    writer.writeheader()

    # Go through data folder and iterate through all json files
    for file in Path("./json").iterdir():
        with open(file.resolve(), "r", encoding="utf-8") as f:
            print(f"File: {file.stem}")
            data = json.load(f)["advertSummary"]

            for item in data:
                row = get_row_from_json_item(item)
                writer.writerow(row)

        gc.collect()

    # Close CSV File
    csv_file.close()

    # Rewrite header with clean names
    with open("./data/data_.csv", "r", newline="", encoding="utf-8") as input, open(
        "./data/data.csv", "w", newline="", encoding="utf-8") as output:
        reader = csv.reader(input, delimiter=";")
        writer = csv.writer(output, delimiter=";")

        header = next(reader)
        writer.writerow(clean_names)

        for row in reader:
            writer.writerow(row)

    # Delete first csv file
    Path("./data/data_.csv").unlink()
