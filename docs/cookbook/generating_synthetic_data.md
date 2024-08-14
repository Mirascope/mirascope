# Generate Synthetic Data

In this cookbook recipe, we go over how to generate synthetic data for LLMs, in this case, OpenAI’s `gpt-4o-mini`. When using LLMs to synthetically generate data, it is most useful to generate non-numerical data which isn’t strictly dependent on a defined probability distribution - in those cases, it will be far easier to define a distribution and generate these points directly from the distribution.

However, for:

- data that needs general intelligence to be realistic
- data that lists many items within a broad category
- data which is language related

and more, LLMs are far easier to use and yield better (or the only feasible) results.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Large Language Models (LLMs) have emerged as powerful tools for generating synthetic data, particularly for text-based applications. Compared to traditional synthetic data generation methods, LLMs can produce more diverse, contextually rich, and human-like textual data, often with less need for domain-specific rules or statistical modeling.
    
## Generate Data as CSV

To generate realistic, synthetic data as a csv, you can accomplish this in a single call by requesting a csv format in the prompt and describing the kind of data you would like generated.

```python
from mirascope.core import openai, prompt_template

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
# > ```csv
#   Name,Price,Inventory
#   Stainless Steel Microwave,149.99,25
#   Cordless Vacuum Cleaner,199.99,15
#   4-Slice Toaster,39.99,50
#   Energy Star Dishwasher,699.00,10
#   Smart Air Purifier,249.50,8
#   ```
```

Note that the prices and inventory of each item are somewhat realistic for their corresponding item, something which would be otherwise difficult to accomplish.

## Generate Data with `response_model`

Sometimes, it will be easier to integrate your datapoints into your code if they are defined as some schema, namely a Pydantic `BaseModel`. In this case, describe each column as the `description` of a `Field` in the `BaseModel` instead of the prompt, and set `response_model` to your defined schema:

```python
from pydantic import BaseModel, Field

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
# > name='Refrigerator' price=799.99 inventory=15
#   name='Microwave Oven' price=129.99 inventory=30
#   name='Washing Machine' price=499.99 inventory=10
#   name='Air Conditioner' price=349.99 inventory=5
#   name='Dishwasher' price=599.99 inventory=8
```

## Generate Data into a pandas `DataFrame`

Since pandas is a common library for working with data, it’s also worth knowing how to directly create and append to a dataframe with LLMs.

### Create a New `DataFrame`

To create a new `DataFrame`, we define a `BaseModel` schema with a simple function to generate  `DataFrame` via a list of list of data and the column names:

```python
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from mirascope.core import openai

class DataFrameGenerator(BaseModel):
    data: list[list[Any]] = Field(
        description="the data to be inserted into the dataframe"
    )
    column_names: list[str] = Field(description="The names of the columns in data")

    def generate_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {name: column for name, column in zip(self.column_names, self.data)}
        )

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
# >              Name   Price  Inventory
#   0  Microwave Oven   79.99         25
#   1         Blender   49.95         18
#   2       Air Fryer  129.99         30
#   3         Toaster   29.99         50
#   4    Coffee Maker   59.99         15
```

### Appending to a `DataFrame`

To append to a `DataFrame`, we can modify the prompt so that instead of describing the data we want to generate, we ask the LLM to match the type of data it already sees. Furthermore, we add a `append_dataframe()` function to append to an existing `DataFrame`. Finally, note that we use the generated `df` from above as the `DataFrame` to append to in the following example:

```python
class DataFrameGenerator(BaseModel):
    ...

    def append_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([df, self.generate_dataframe()], ignore_index=True)
        
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
# >                Name   Price  Inventory
#   0    Microwave Oven   79.99         25
#   1           Blender   49.95         18
#   2         Air Fryer  129.99         30
#   3           Toaster   29.99         50
#   4      Coffee Maker   59.99         15
#   5   Electric Kettle   39.99         20
#   6    Food Processor   89.99         12
#   7       Rice Cooker   59.99         27
#   8       Slow Cooker   49.99         22
#   9  Electric Griddle   69.99         15
```

## Adding Constraints

While you cannot successfully add complex mathematical constraints to generated data (think statistics, such as distributions and covariances), asking LLMs to abide by basic constraints will (generally) prove successful, especially with newer models. Let’s look at an example where we generate TVs where the TV price should roughly linearly correlate with TV size, and QLEDs are 2-3x more expensive than OLEDs of the same size:

```python
from typing import Literal

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
# > size=32 price=399.99 tv_type='OLED'
#   size=32 price=799.99 tv_type='QLED'
#   size=42 price=599.99 tv_type='OLED'
#   size=42 price=1199.99 tv_type='QLED'
#   size=50 price=699.99 tv_type='OLED'
#   size=50 price=1399.99 tv_type='QLED'
#   size=55 price=899.99 tv_type='OLED'
#   size=55 price=1799.99 tv_type='QLED'
#   size=65 price=1099.99 tv_type='OLED'
#   size=65 price=2199.99 tv_type='QLED'
```

To demonstrate the constraints’ being followed, you can graph the data using matplotlib, which shows the linear relationships between size and price, and QLEDs costing roughly twice as much as OLED:

![generating-synthetic-data-chart](../assets/generating-synthetic-data-chart.png)

!!! tip "Additional Real-World Examples"
    - **Healthcare and Medical Research**: Generating synthetic patient records for training machine learning models without compromising patient privacy
    - **Environmental Science**: Generating synthetic climate data for modeling long-term environmental changes
    - **Fraud Detection Systems**: Generating synthetic data of fraudulent and legitimate transactions for training fraud detection models.

When adapting this recipe to your specific use-case, consider the following:
    - Add Pydantic `AfterValidators` to constrain your synthetic data generation
    - Verify that the synthetic data generated actually matches real-world data.
    - Make sure no biases are present in the generated data, this can be prompt engineered.
    - Experiment with different model providers and versions for quality.
