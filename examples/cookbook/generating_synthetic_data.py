from typing import Any, Literal

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

load_dotenv()


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Generate {num_datapoints} random but realistic datapoints of items which could
    be in a home appliances warehouse. Output the datapoints as a csv, and your
    response should only be the CSV.

    Format:
    Name, Price, Inventory

    Name - the name of the home appliance product
    Price - the price of an individual product, in dollars (include cents)
    Inventory - how many are left in stock
    """
)
def generate_csv_data(num_datapoints: int): ...


print(generate_csv_data(5))
# Output:
"""
 ```csv
  Name,Price,Inventory
  Stainless Steel Microwave,149.99,25
  Cordless Vacuum Cleaner,199.99,15
  4-Slice Toaster,39.99,50
  Energy Star Dishwasher,699.00,10
  Smart Air Purifier,249.50,8
  ```
"""


class HomeAppliance(BaseModel):
    name: str = Field(description="The name of the home appliance product")
    price: float = Field(
        description="The price of an individual product, in dollars (include cents)"
    )
    inventory: int = Field(description="How many of the items are left in stock")


@openai.call(model="gpt-4o-mini", response_model=list[HomeAppliance])
@prompt_template(
    """
    Generate {num_datapoints} random but realistic datapoints of items which could
    be in a home appliances warehouse. Output the datapoints as a list of instances
    of HomeAppliance.
    """
)
def generate_home_appliance_data(num_datapoints: int): ...


print(generate_home_appliance_data(5))
# Output:
"""
  name='Refrigerator' price=799.99 inventory=15
  name='Microwave Oven' price=129.99 inventory=30
  name='Washing Machine' price=499.99 inventory=10
  name='Air Conditioner' price=349.99 inventory=5
  name='Dishwasher' price=599.99 inventory=8
"""


class DataFrameGenerator(BaseModel):
    data: list[list[Any]] = Field(
        description="the data to be inserted into the dataframe"
    )
    column_names: list[str] = Field(description="The names of the columns in data")

    def append_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([df, self.generate_dataframe()], ignore_index=True)

    def generate_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(dict(zip(self.column_names, self.data, strict=False)))


@openai.call(model="gpt-4o-mini", response_model=DataFrameGenerator)
@prompt_template(
    """
    Generate {num_datapoints} random but realistic datapoints of items which could
    be in a home appliances warehouse. Generate your response as `data` and
    `column_names`, so that a pandas DataFrame may be generated with:
    `pd.DataFrame(data, columns=column_names)`.

    Format:
    Name, Price, Inventory

    Name - the name of the home appliance product
    Price - the price of an individual product, in dollars (include cents)
    Inventory - how many are left in stock
    """
)
def generate_df_data(num_datapoints: int): ...


df_data = generate_df_data(5)
df = df_data.generate_dataframe()
print(df)
# Output:
"""
               Name   Price  Inventory
  0  Microwave Oven   79.99         25
  1         Blender   49.95         18
  2       Air Fryer  129.99         30
  3         Toaster   29.99         50
  4    Coffee Maker   59.99         15
"""


@openai.call(model="gpt-4o-mini", response_model=DataFrameGenerator)
@prompt_template(
    """
    Generate {num_datapoints} random but realistic datapoints of items which would
    make sense to the following dataset:
    {df}
    Generate your response as `data` and
    `column_names`, so that a pandas DataFrame may be generated with:
    `pd.DataFrame(data, columns=column_names)` then appended to the existing data.
    """
)
def generate_additional_df_data(num_datapoints: int, df: pd.DataFrame): ...


df_data = generate_additional_df_data(5, df)
df = df_data.append_dataframe(df)
print(df)
# Output:
"""
                 Name   Price  Inventory
  0    Microwave Oven   79.99         25
  1           Blender   49.95         18
  2         Air Fryer  129.99         30
  3           Toaster   29.99         50
  4      Coffee Maker   59.99         15
  5   Electric Kettle   39.99         20
  6    Food Processor   89.99         12
  7       Rice Cooker   59.99         27
  8       Slow Cooker   49.99         22
  9  Electric Griddle   69.99         15
"""


class TV(BaseModel):
    size: int = Field(description="The size of the TV")
    price: float = Field(description="The price of the TV in dollars (include cents)")
    tv_type: Literal["OLED", "QLED"]


@openai.call(model="gpt-4o-mini", response_model=list[TV])
@prompt_template(
    """
    Generate {num_datapoints} random but realistic datapoints of TVs.
    Output the datapoints as a list of instances of TV.

    Make sure to abide by the following constraints:
    QLEDS should be roughly (not exactly) 2x the price of an OLED of the same size
    for both OLEDs and QLEDS, price should increase roughly proportionately to size
    """
)
def generate_tv_data(num_datapoints: int): ...


for tv in generate_tv_data(10):
    print(tv)
# Output:
"""
  size=32 price=399.99 tv_type='OLED'
  size=32 price=799.99 tv_type='QLED'
  size=42 price=599.99 tv_type='OLED'
  size=42 price=1199.99 tv_type='QLED'
  size=50 price=699.99 tv_type='OLED'
  size=50 price=1399.99 tv_type='QLED'
  size=55 price=899.99 tv_type='OLED'
  size=55 price=1799.99 tv_type='QLED'
  size=65 price=1099.99 tv_type='OLED'
  size=65 price=2199.99 tv_type='QLED'
"""
