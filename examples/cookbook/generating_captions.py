from mirascope.core import openai, prompt_template

url = "https://c02.purpledshub.com/uploads/sites/41/2023/01/How-to-see-the-Wolf-Moon-in-2023--4bb6bb7.jpg?w=940&webp=1"


@openai.call(model="gpt-4o-mini")
@prompt_template("Generate a short, descriptive caption for this image: {url:image}")
def generate_caption(url: str): ...


response = generate_caption(url)
print(response)
