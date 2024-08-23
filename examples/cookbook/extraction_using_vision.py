import base64

import httpx
from pydantic import BaseModel, Field

from mirascope.core import anthropic, openai, prompt_template

image_url = "https://www.receiptfont.com/wp-content/uploads/template-mcdonalds-1-screenshot-fit.png"

image_media_type = "image/png"
image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")


class Item(BaseModel):
    name: str = Field(..., description="The name of the item")
    quantity: int = Field(..., description="The quantity of the item")
    price: float = Field(..., description="The price of the item")


@openai.call(model="gpt-4o", response_model=list[Item])
@prompt_template(
    """
    SYSTEM:
    Extract the receipt information from the image.
    
    USER:
    {url:image}
    """
)
def extract_receipt_info_openai(url: str): ...


@anthropic.call(
    model="claude-3-5-sonnet-20240620", response_model=list[Item], json_mode=True
)
@prompt_template(
    """
    Extract the receipt information from the image.
    
    {url:image}
    """
)
def extract_receipt_info_anthropic(url: str): ...


print(extract_receipt_info_openai(image_url))
print(extract_receipt_info_anthropic(image_url))
