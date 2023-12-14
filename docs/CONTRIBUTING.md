# Contributing

## Setting Up Development Environment

First, [install pyenv](https://github.com/pyenv/pyenv#installation) so you can run the code under all of the supported environments. Also make sure to [install pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) so you can create python environments with the correct versions.

To install a specific version of python, you can run e.g. `pyenv install 3.10.9`. You can then create a virtual environment to run and test code locally during development by running the following code from the base directory:

```sh
pyenv virtualenv {python_version} env-name
pyenv activate env-name
pip install poetry
poetry install
```

If you'd prefer, you can also use conda to manage your python versions and environments. For installing conda, see their [installation guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

The following code is an example of how to set up such an environment:

```sh
conda create -n env-name pip poetry python={python_version}
conda activate env-name
poetry install
```

Make sure to replace `{python_version}` in the above snippets with the version you want the environment to use (e.g. 3.10.9) and name the environment accordingly (e.g. env-name-3.10).

## Development Workflow

1.  Search through existing [GitHub Issues](https://github.com/Mirascope/mirascope/issues) to see if what you want to work on has already been added.

    - If not, please create a new issue. This will help to reduce duplicated work.

2.  For first-time contributors, visit [https://github.com/Mirascope/mirascope](https://github.com/Mirascope/mirascope) and "Fork" the repository (see the button in the top right corner).

    - You'll need to set up [SSH authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

    - Clone the forked project and point it to the main project:

    ```shell
    git clone https://github.com/<your-username>/mirascope.git
    git remote add upstream https://github.com/Mirascope/mirascope.git
    ```

3.  Development.

    - Make sure you are in sync with the main repo:

    ```shell
    git checkout dev
    git pull upstream dev
    ```

    - Create a `git` feature branch with a meaningful name where you will add your contributions.

    ```shell
    git checkout -b meaningful-branch-name
    ```

    - Start coding! commit your changes locally as you work:

    ```shell
    git add mirascope/modified_file.py tests/test_modified_file.py
    git commit -m "feat: specific description of changes contained in commit"
    ```

    - Format your code!

    ```shell
    poetry run ruff format .
    ```

    - Lint and test your code! From the base directory, run:

    ```shell
    poetry run ruff check .
    poetry run mypy .
    ```

4.  Contributions are submitted through [GitHub Pull Requests](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)

    - When you are ready to submit your contribution for review, push your branch:

    ```shell
    git push origin meaningful-branch-name
    ```

    - Open the printed URL to open a PR. Make sure to fill in a detailed title and description. Submit your PR for review.

    - Link the issue you selected or created under "Development"

    - We will review your contribution and add any comments to the PR. Commit any updates you make in response to comments and push them to the branch (they will be automatically included in the PR)

### Pull Requests

Please conform to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all PR titles and commits.

## Testing

All changes to the codebase must be properly unit tested. If a change requires updating an existing unit test, make sure to think through if the change is breaking.

We use `pytest` as our testing framework. If you haven't worked with it before, take a look at [their docs](https://docs.pytest.org/).

## Formatting and Linting

In an effort to keep the codebase clean and easy to work with, we use `ruff` for formatting and both `ruff` and `mypy` for linting. Before sending any PR for review, make sure to run both `ruff` and `mypy`.

If you are using VS Code, then install the extensions in `.vscode/extensions.json` and the workspace settings should automatically run `ruff` formatting on save and show `ruff` and `mypy` errors.
