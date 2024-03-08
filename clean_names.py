import os

for filename in os.listdir("docs/concepts"):
    new_filename = f"{'_'.join([word.lower() for word in filename.split(' ')[:-1]])}.md"
    with open(f"docs/concepts/{filename}", "r") as file:
        content = file.read()
    with open(f"docs/concepts/{new_filename}", "w") as file:
        file.write(content)
    os.remove(f"docs/concepts/{filename}")
