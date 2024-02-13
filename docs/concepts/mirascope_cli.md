# Mirascope CLI

One of the main frustrations of dealing with prompts is keeping track of all the various versions. Taking inspiration from alembic and git, the mirascope cli provides a couple of key pieces of functionality to make managing prompts easier.

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

* `mirascope.ini` - The INI file that can be customized for your project
* `mirascope` - The default name of the directory that is home to the prompt management environment
* `prompt_template.j2` - The Jinja2 template file that is used to generate prompt versions
* `versions` - The directory that holds the various prompt versions
* `versions/<directory_name` - The sub-directory that is created for each prompt file in the `prompts` directory
* `version.txt` - A file system method of keeping track of current and latest revisions. Coming soon is revision tracking using a database instead
* `<revision_id>_<directory_name>.py` - A prompt version that is created by the `mirascope add` command, more on this later.
* `prompts` - The user's prompt directory that stores all prompt files

The directory names can be changed anytime by modifying the `mirascope.ini` file or when running the `init` command.

```shell
mirascope init --mirascope_location my_mirascope --prompts_location my_prompts
```

### Saving your first prompt

After creating the prompt management directory, you are now ready to build and iterate on some prompts. Begin by adding a Mirascope Prompt to the prompts directory.

```python
# prompts/my_prompt.py
from mirascope import Prompt

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str
```

Once you are happy with the first iteration of this prompt, you can run:

```
mirascope add my_prompt
```

This will commit `my_prompt.py` to your `versions/` directory, creating a `my_prompt` sub-directory and a `0001_my_prompt.py`.

Here is what `0001_my_prompt.py` will look like:

```python
# versions/my_prompt/0001_my_prompt.py
from mirascope import Prompt

prev_revision_id = "None"
revision_id = "0001"

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str
```

The prompt inside the versions directory is almost identical to the prompt inside the prompts directory with a few differences.

The variables `prev_revision_id` and `revision_id` will be used for features coming soon, so stay tuned for updates.

### Iterating on the prompt

Now that this version of `my_prompt` has been saved, you are now free to modify the original `my_prompt.py` and iterate. Maybe, you want to add a system message to obtain advice from a professional.

Here is what the next iteration of `my_prompt.py` will look like:

```python
# prompts/my_prompt.py
from mirascope.prompts import Prompt, messages

@messages
class BookRecommendationPrompt(Prompt):
    """
	SYSTEM:
	You are an expert in your field giving advice

	USER:
    Can you recommend some books on {topic} in a list format?
    """

    topic: str
```

Before adding the next revision of `my_prompt`, you may want to check the status of your prompt.

```shell
# You can specify a specific prompt
mirascope status my_prompt

# or, you can check the status of all prompts
mirascope status
```

Note that status will be checked before the `add` or `use` command is run.
Now we can run the same `add` command in the previous section to commit another version `0002_my_prompt.py`

### Switching between versions

Often times when prompt engineering, you will want to try out different models with different prompts to obtain the best results.

You can use the `use` command to quickly switch between the prompts:

```shell
mirascope use my_prompt 0001
```

Here you specify which prompt and also which version you want to use. This will update your `prompts/my_prompt.py` with the contents of `versions/0001_my_prompt.py` (minus the variables used internally).

This will let you quickly swap prompts with no code change, the exception being when prompts have different properties.

### Removing prompts

Often times when experimenting with prompts, lots of unused versions will need to be cleaned up in your project.

You can use the `remove` command to delete any version:

```shell
mirascope remove my_prompt 0001
```

Here you specify which prompt and version you want to remove. Removal will delete the file but also update any versions that have the deleted version in their `prev_revision_id` to `None`.

!!!note

`mirascope remove` will not remove the prompt if `current_revision` is the same as the prompt you are trying to remove. You can use `mirascope add` if you have incoming changes or `mirascope use` to swap `current_revision`.

## Future updates

There is a lot more to be added to the Mirascope CLI. Here is a list in no order of things we are thinking about adding next: 

* prompt comparison - A way to compare two different versions with a golden test
* history - View the revision history of a version

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
