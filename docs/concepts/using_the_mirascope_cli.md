# Using the Mirascope CLI

One of the main frustrations of dealing with prompts is keeping track of all the various revisions. Taking inspiration from alembic and git, the Mirascope CLI provides a couple of key commands to make managing prompts easier.

## The prompt management environment

The first step to using the Mirascope CLI is to use the `init` command in your project's root directory.

```
mirascope init
```

This will create the directories and files to help manage prompts.
Here is a sample structure created by the `init` function:

```
|
|-- mirascope.ini
|-- mirascope
|   |-- prompt_template.j2
|   |-- versions/
|   |   |-- <directory_name>/
|   |   |   |-- version.txt
|   |   |   |-- <revision_id>_<directory_name>.py
|-- prompts/
```

Here is a rundown of each directory and file:

- `mirascope.ini` - The INI file that can be customized for your project
- `mirascope` - The default name of the directory that is home to the prompt management environment
- `prompt_template.j2` - The Jinja2 template file that is used to generate prompt versions
- `versions` - The directory that holds the various prompt versions
- `versions/<directory_name` - The sub-directory that is created for each prompt file in the `prompts` directory
- `version.txt` - A file system method of keeping track of current and latest revisions. Coming soon is revision tracking using a database instead
- `<revision_id>_<directory_name>.py` - A prompt version that is created by the `mirascope add` command, more on this later.
- `prompts` - The user's prompt directory that stores all prompt files

The directory names can be changed anytime by modifying the `mirascope.ini` file or when running the `init` command.

```
mirascope init --mirascope_location my_mirascope --prompts_location my_prompts
```

## Saving your first prompt

After creating the prompt management directory, you are now ready to build and iterate on some prompts. Begin by adding a Mirascope Prompt to the prompts directory.

```python
# prompts/my_prompt.py
from mirascope.openai import OpenAIPrompt, OpenAICallParams


class BookRecommendation(OpenAIPrompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo")

```

Once you are happy with the first iteration of this prompt, you can run:

```
mirascope add my_prompt
```

This will commit `my_prompt.py` to your `versions/` directory, creating a `my_prompt` sub-directory and a `0001_my_prompt.py`.

Here is what `0001_my_prompt.py` will look like:

```python
# versions/my_prompt/0001_my_prompt.py
from mirascope.openai import OpenAIPrompt, OpenAICallParams

prev_revision_id = "None"
revision_id = "0001"


class BookRecommendation(OpenAIPrompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo")
```

The prompt inside the versions directory is almost identical to the prompt inside the prompts directory with a few differences.

The variables `prev_revision_id` and `revision_id` will be used for features coming soon, so stay tuned for updates.

## Colocate

**Everything that affects the quality of a prompt lives in the prompt.** This is why `call_params` exists in Prompt and why `OpenAI` and other provider wrappers are combined with `BasePrompt`.

## Iterating on the prompt

Now that this version of `my_prompt` has been saved, you are now free to modify the original `my_prompt.py` and iterate. Maybe, you want to switch to a different provider and compare results.

Here is what the next iteration of `my_prompt.py` will look like:

```python
# prompts/my_prompt.py
from google.generativeai import configure
from mirasope.gemini import GeminiPrompt, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class BookRecommendation(GeminiPrompt):
	"""
	Can you recommend some books on {topic} in a list format?
	"""

	ingredient: str

	call_params = GeminiCallParams(model="gemini-1.0-pro")

```

Before adding the next revision of `my_prompt`, you may want to check the status of your prompt.

```
# You can specify a specific prompt
mirascope status my_prompt

# or, you can check the status of all prompts
mirascope status
```

Note that status will also be checked before the `add` or `use` command is run.
Now we can run the same `add` command in the previous section to commit another version `0002_my_prompt.py`

## Switching between versions

You can now freely switch different providers or use the same provider with a different model to iterate to the best results.

You can use the `use` command to quickly switch between the prompts:

```
mirascope use my_prompt 0001
```

Here you specify which prompt and also which version you want to use. This will update your `prompts/my_prompt.py` with the contents of `versions/0001_my_prompt.py` (minus the variables used internally).

This will let you quickly swap prompts or providers with **no code change**, the exception being when prompts have different attributes. In that case, your **linter will detect missing or additional attributes** that need to be addressed.

## Removing prompts

Often times when experimenting with prompts, a lot of experimental prompts will need to be cleaned up in your project.

You can use the `remove` command to delete any version:

```
mirascope remove my_prompt 0001
```

Here you specify which prompt and version you want to remove. Removal will delete the file but also update any versions that have the deleted version in their `prev_revision_id` to `None`.

!!! note

    `mirascope remove` will not remove the prompt if `current_revision` is the same as the prompt you are trying to remove. You can use `mirascope add` if you have incoming changes or `mirascope use` to swap `current_revision`.

## Mirascope INI

The Mirascope INI provides some customization for you. Feel free to update any field.

```python
[mirascope]

# path to mirascope directory
mirascope_location = .mirascope

# path to versions directory
versions_location = %(mirascope_location)s/versions

# path to prompts directory
prompts_location = prompts

# name of versions text file
version_file_name = version.txt

# formats the version file
# leave blank to not format 
format_command = ruff check --select I --fix; ruff format

# auto tag prompts with version
auto_tag = True
```

- `auto_tag` - Adds `@tags(["version:0001"])` to Mirascope Prompts. This will auto increment the version number if a new version is added.

## Future updates

There is a lot more to be added to the Mirascope CLI. Here is a list in no order of things we are thinking about adding next:

- prompt comparison - A way to compare two different versions with a golden test
- history - View the revision history of a version
- testing - Adding input and outputs to the revision for CI testing

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
