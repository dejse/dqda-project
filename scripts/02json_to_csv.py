import json
import csv
from pathlib import Path
import gc

data_path = Path("./data")

schema = [
    "id",
    "description",
    "PRODUCT_ID",
    "HEADING",
    "BODY_DYN",
    "PRICE",
    "YEAR_MODEL",
    "MILEAGE",
    "CAR_MODEL/MAKE",
    "CAR_MODEL/MODEL",
    "CAR_TYPE",
    "NO_OF_OWNERS",
    "NOOFSEATS",
    "ENGINE/EFFECT",
    "ENGINE/FUEL_RESOLVED",
    "TRANSMISSION_RESOLVED",
    "CONDITION_RESOLVED",
    "WARRANTY_RESOLVED",
    "PUBLISHED_String",
    "COUNTRY",
    "COORDINATES",
    "POSTCODE",
    "STATE",
    "DISTRICT",
    "ADDRESS",
    "LOCATION",
    "ORGNAME",
    "fnmmocount",
    "UPSELLING_AD_SEARCHRESULT",
    "ISPRIVATE",
    "EQUIPMENT_RESOLVED",
]
clean_names = schema[:]
clean_names[8] = "brand"
clean_names[9] = "model"
clean_names[13] = "engine_effect"
clean_names[14] = "engine_fuel_resolved"
clean_names = [item.lower() for item in clean_names]


def extract_dict_from_json(entry: dict) -> dict:
    """
    Extract and format relevant data from Willhaben JSON
    """
    record = {"id": entry["id"], "description": entry["description"]}
    for e in entry["attributes"]["attribute"]:
        if e["name"] in schema:
            name = e["name"]
            value = e["values"][0]
            if name in "EQUIPMENT_RESOLVED":
                value = "|".join(e["values"])
            record.update({name: value})
    return record


if __name__ == "__main__":
    # Open CSV File and prep it
    csv_file = open("data_.csv", "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, dialect="excel", delimiter=";", fieldnames=schema)
    writer.writeheader()

    # Go through data folder and iterate through all json files
    for file in data_path.iterdir():
        with open(file.resolve(), "r", encoding="utf-8") as f:
            print(f"File: {file.stem}")
            data = json.load(f)["advertSummary"]

            for entry in data:
                record = extract_dict_from_json(entry)
                writer.writerow(record)

        gc.collect()
    csv_file.close()

    # Rewrite header with clean names
    with open("data_.csv", "r", newline="", encoding="utf-8") as input, open(
        "data.csv", "w", newline="", encoding="utf-8"
    ) as output:
        reader = csv.reader(input, delimiter=";")
        writer = csv.writer(output, delimiter=";")

        header = next(reader)
        writer.writerow(clean_names)

        for row in reader:
            writer.writerow(row)

    Path("data_.csv").unlink()