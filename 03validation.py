from pydantic import BaseModel, Field, ValidationError, validator
from typing import Union
import csv


class Inserat(BaseModel):
    id: str = Field(len=9)
    description: Union[str, None]
    product_id: Union[int, None]
    heading: str
    body_dyn: Union[str, None]
    price: int = Field(ge=0)
    year_model: int = Field(ge=0)
    mileage: int = Field(ge=0)
    brand: Union[str, None]
    model: Union[str, None]
    car_type: Union[str, None]
    no_of_owners: Union[str, None]
    noofseats: Union[str, None]
    engine_effect: int = Field(ge=0)
    engine_fuel_resolved: Union[str, None]
    transmission_resolved: Union[str, None]
    condition_resolved: Union[str, None]
    warranty_resolved: Union[str, None]
    published_string: Union[str, None]
    country: Union[str, None]
    coordinates: Union[str, None]
    postcode: Union[str, None]
    state: Union[str, None]
    district: Union[str, None]
    address: Union[str, None]
    location: Union[str, None]
    orgname: Union[str, None]
    fnmmocount: Union[int, None]
    upselling_ad_searchresult: Union[str, None]
    isprivate: Union[int, None]
    equipment_resolved: Union[str, None]


    @validator("year_model", "mileage", "engine_effect", "price", pre=True, allow_reuse=True)
    def make_int(cls, v):
        return int(v)


if __name__ == "__main__":

    validated_data = []
    data = []
    with open("data.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        data = list(reader)
        for item in data:
            try:
                validated_data.append(Inserat(**item).dict())
            except ValidationError as e:
                print(item["id"], e)
            
    print(f"Rows of raw data {len(data)}")
    print(f"Rows of validated data {len(validated_data)}")

    with open("data-validated.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            dialect="excel",
            delimiter=";",
            fieldnames=list(validated_data[0].keys()),
        )
        writer.writeheader()
        for item in validated_data:
            writer.writerow(item)
