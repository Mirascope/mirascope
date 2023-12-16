import argparse
import ast

from jinja2 import Environment, FileSystemLoader

from .utils import PythonFileAnalyzer

base_directory = "../examples/project-with-cli"
version_directory = "../examples/project-with-cli/versions"
env_prefix = "MIRASCOPE"


def get_current_head(key_to_modify: str):
    """Returns the current head of the given template."""
    with open(f"{base_directory}/.env", "r", encoding="utf-8") as file:
        for line in file:
            # Check if the current line contains the key
            if line.startswith(key_to_modify + "="):
                return line.split("=")[1].strip()
        return None


def write_to_template(file):
    template_loader = FileSystemLoader(
        searchpath=base_directory
    )  # Set your template directory
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = PythonFileAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    data = {
        "comments": analyzer.comments,
        "variables": analyzer.variables,
        "imports": analyzer.imports,
        "from_imports": analyzer.from_imports,
        "classes": analyzer.classes,
    }
    return template.render(**data)


def add(args):
    # Implement the logic for 'add' command
    print(f"Adding {base_directory}/{args.item}")
    with open(f"{base_directory}/{args.item}", "r", encoding="utf-8") as file:
        key_to_modify: str = f'MIRASCOPE_{args.item.replace(".py", "").upper()}'
        current_head = get_current_head(key_to_modify)
        print(current_head)
        if current_head is None:
            # first revision
            revision_id = "0001"
        else:
            # default branch with incrementation
            last_rev_id = int(current_head)
            revision_id = f"{last_rev_id+1:04}"
        with open(
            f"{version_directory}/{revision_id}_{args.item}", "w+", encoding="utf-8"
        ) as file2:
            file2.write(write_to_template(file.read()))
        try:
            modified_lines = []
            key_found = False
            with open(f"{base_directory}/.env", "r", encoding="utf-8") as file:
                print(key_to_modify, revision_id)
                for line in file:
                    # Check if the current line contains the key
                    if line.startswith(key_to_modify + "="):
                        modified_lines.append(f"{key_to_modify}={revision_id}\n")
                        key_found = True
                    else:
                        modified_lines.append(line)

                # If the key was not found, add it to the end
                if not key_found:
                    modified_lines.append(f"{key_to_modify}={revision_id}\n")

            # Write the modified content back to the .env file
            with open(f"{base_directory}/.env", "w", encoding="utf-8") as file:
                file.writelines(modified_lines)

        except FileNotFoundError:
            print(f"The file {base_directory}/.env was not found.")
        except IOError as e:
            print(f"An I/O error occurred: {e}")


def status(args):
    # Implement the logic for 'status' command
    print(f"Using {args.resource}")


def use(args):
    # Implement the logic for 'use' command
    print(f"Using {args.resource}")


def main():
    parser = argparse.ArgumentParser(description="CLI Tool")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # Adding 'add' command
    parser_add = subparsers.add_parser("add", help="Add an item")
    parser_add.add_argument("item", help="Item to add")
    parser_add.set_defaults(func=add)

    # Adding 'status' command
    parser_commit = subparsers.add_parser("status", help="Check status of prompts")
    parser_commit.set_defaults(func=status)

    # Adding 'use' command
    parser_use = subparsers.add_parser("use", help="Use a resource")
    parser_use.add_argument("resource", help="Resource to use")
    parser_use.set_defaults(func=use)

    # Parse the arguments and call the respective function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
