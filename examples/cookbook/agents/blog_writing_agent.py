import inspect
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, ValidationError
from tenacity import retry, wait_exponential

from mirascope.core import openai, prompt_template
from mirascope.integrations.tenacity import collect_errors


class OpenAIAgent(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @abstractmethod
    def _step(self, prompt: str) -> openai.OpenAIStream: ...

    def run(self, prompt: str) -> str:
        stream = self._step(prompt)
        result, tools_and_outputs = "", []

        for chunk, tool in stream:
            if tool:
                tools_and_outputs.append((tool, tool.call()))
            else:
                result += chunk.content
                print(chunk.content, end="", flush=True)
        if stream.user_message_param:
            self.history.append(stream.user_message_param)
        self.history.append(stream.message_param)
        if tools_and_outputs:
            self.history += stream.tool_message_params(tools_and_outputs)
            return self.run("")
        print("\n")
        return result


class Researcher(OpenAIAgent):
    max_results: int = 10

    def web_search(self, text: str) -> str:
        """Search the web for the given text.

        Args:
            text: The text to search for.

        Returns:
            The search results for the given text formatted as newline separated
            dictionaries with keys 'title', 'href', and 'body'.
        """
        try:
            results = DDGS(proxy=None).text(text, max_results=self.max_results)
            return "\n\n".join(
                [
                    inspect.cleandoc(
                        """
                        title: {title}
                        href: {href}
                        body: {body}
                        """
                    ).format(**result)
                    for result in results
                ]
            )
        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"

    def parse_webpage(self, link: str) -> str:
        """Parse the paragraphs of the webpage found at `link`.

        Args:
            link: The URL of the webpage.

        Returns:
            The parsed paragraphs of the webpage, separated by newlines.
        """
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            return "\n".join([p.text for p in soup.find_all("p")])
        except Exception as e:
            return f"{type(e)}: Failed to parse content from URL"

    @openai.call("gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        Your task is to research a topic and summarize the information you find.
        This information will be given to a writer (user) to create a blog post.

        You have access to the following tools:
        - `web_search`: Search the web for information. Limit to max {self.max_results}
            results.
        - `parse_webpage`: Parse the content of a webpage.

        When calling the `web_search` tool, the `body` is simply the body of the search
        result. You MUST then call the `parse_webpage` tool to get the actual content
        of the webpage. It is up to you to determine which search results to parse.

        Once you have gathered all of the information you need, generate a writeup that
        strikes the right balance between brevity and completeness. The goal is to
        provide as much information to the writer as possible without overwhelming them.

        MESSAGES: {self.history}
        USER: {prompt}
        """
    )
    def _step(self, prompt: str) -> openai.OpenAIDynamicConfig:
        return {"tools": [self.web_search, self.parse_webpage]}

    def research(self, prompt: str) -> str:
        """Research a topic and summarize the information found.

        Args:
            prompt: The user prompt to guide the research. The content of this prompt
                is directly responsible for the quality of the research, so it is
                crucial that the prompt be clear and concise.

        Returns:
            The results of the research.
        """
        print("RESEARCHING...")
        result = self.run(prompt)
        print("RESEARCH COMPLETE!")
        return result


class AgentExecutor(OpenAIAgent):
    researcher: Researcher = Researcher()
    num_paragraphs: int = 4

    class InitialDraft(BaseModel):
        draft: str
        critique: str

    @staticmethod
    def parse_initial_draft(response: InitialDraft) -> str:
        return f"Draft: {response.draft}\nCritique: {response.critique}"

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        after=collect_errors(ValidationError),
    )
    @openai.call(
        "gpt-4o-mini", response_model=InitialDraft, output_parser=parse_initial_draft
    )
    @prompt_template(
        """
        SYSTEM:
        Your task is to write the initial draft for a blog post based on the information
        provided to you by the researcher, which will be a summary of the information
        they found on the internet.

        Along with the draft, you will also write a critique of your own work. This
        critique is crucial for improving the quality of the draft in subsequent
        iterations. Ensure that the critique is thoughtful, constructive, and specific.
        It should strike the right balance between comprehensive and concise feedback.

        If for any reason you deem that the research is insufficient or unclear, you can
        request that additional research be conducted by the researcher. Make sure that
        your request is specific, clear, and concise.

        MESSAGES: {self.history}
        USER:
        {previous_errors}
        {prompt}
        """
    )
    def _write_initial_draft(
        self, prompt: str, *, errors: list[ValidationError] | None = None
    ) -> openai.OpenAIDynamicConfig:
        """Writes the initial draft of a blog post along with a self-critique.

        Args:
            prompt: The user prompt to guide the writing process. The content of this
                prompt is directly responsible for the quality of the blog post, so it
                is crucial that the prompt be clear and concise.

        Returns:
            The initial draft of the blog post along with a self-critique.
        """
        return {
            "computed_fields": {
                "previous_errors": f"Previous Errors: {errors}" if errors else None
            }
        }

    @openai.call("gpt-4o-mini", stream=True)
    @prompt_template(
        """
        SYSTEM:
        Your task is to facilitate the collaboration between the researcher and the
        blog writer. The researcher will provide the blog writer with the information
        they need to write a blog post, and the blog writer will draft and critique the
        blog post until they reach a final iteration they are satisfied with.

        To access the researcher and writer, you have the following tools:
        - `research`: Prompt the researcher to perform research.
        - `_write_initial_draft`: Write an initial draft with a self-critique

        You will need to manage the flow of information between the researcher and the
        blog writer, ensuring that the information provided is clear, concise, and
        relevant to the task at hand.

        The final blog post MUST have EXACTLY {self.num_paragraphs} paragraphs.

        MESSAGES: {self.history}
        USER: {prompt}
        """
    )
    def _step(self, prompt: str) -> openai.OpenAIDynamicConfig:
        return {"tools": [self.researcher.research, self._write_initial_draft]}


if __name__ == "__main__":
    agent = AgentExecutor()
    print("STARTING AGENT EXECUTION...")
    agent.run("Help me write a blog post about LLMs and structured outputs.")
