"""Tests for message helper functions."""

from mirascope import llm


class TestSystemMessage:
    """Test system message creation."""

    def test_system_with_string(self) -> None:
        """Test creating a system message with a string."""
        msg = llm.messages.system("You are a helpful assistant")

        assert isinstance(msg, llm.messages.SystemMessage)
        assert msg.role == "system"
        assert isinstance(msg.content, llm.Text)
        assert msg.content.text == "You are a helpful assistant"

    def test_system_with_text_object(self) -> None:
        """Test creating a system message with a Text object."""
        text_obj = llm.Text(text="You are a helpful assistant")
        msg = llm.messages.system(text_obj)

        assert isinstance(msg, llm.messages.SystemMessage)
        assert msg.role == "system"
        assert msg.content is text_obj
        assert msg.content.text == "You are a helpful assistant"


class TestUserMessage:
    """Test user message creation."""

    def test_user_with_string(self) -> None:
        """Test creating a user message with a string."""
        msg = llm.messages.user("Hello world")

        assert isinstance(msg, llm.UserMessage)
        assert msg.role == "user"
        assert msg.name is None
        assert len(msg.content) == 1
        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello world"

    def test_user_with_name(self) -> None:
        """Test creating a user message with a name."""
        msg = llm.messages.user("Hello world", name="Alice")

        assert isinstance(msg, llm.UserMessage)
        assert msg.role == "user"
        assert msg.name == "Alice"
        assert len(msg.content) == 1
        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello world"

    def test_user_with_content_part(self) -> None:
        """Test creating a user message with a single content part."""
        text_obj = llm.Text(text="Hello world")
        msg = llm.messages.user(text_obj)

        assert isinstance(msg, llm.UserMessage)
        assert msg.role == "user"
        assert msg.name is None
        assert len(msg.content) == 1
        assert msg.content[0] is text_obj

    def test_user_with_mixed_sequence(self) -> None:
        """Test creating a user message with a sequence of mixed content."""
        text_obj = llm.Text(text="Look at this:")
        content_list = ["Hello", text_obj, "World"]
        msg = llm.messages.user(content_list)

        assert isinstance(msg, llm.UserMessage)
        assert msg.role == "user"
        assert msg.name is None
        assert len(msg.content) == 3

        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello"

        assert msg.content[1] is text_obj

        assert isinstance(msg.content[2], llm.Text)
        assert msg.content[2].text == "World"

    def test_user_with_empty_sequence(self) -> None:
        """Test creating a user message with an empty sequence."""
        msg = llm.messages.user([])

        assert isinstance(msg, llm.UserMessage)
        assert msg.role == "user"
        assert msg.name is None
        assert len(msg.content) == 0


class TestAssistantMessage:
    """Test assistant message creation."""

    def test_assistant_with_string(self) -> None:
        """Test creating an assistant message with a string."""
        msg = llm.messages.assistant(
            "Hello! How can I help you?", model_id="openai/gpt-5", provider_id="openai"
        )

        assert isinstance(msg, llm.AssistantMessage)
        assert msg.role == "assistant"
        assert msg.name is None
        assert len(msg.content) == 1
        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello! How can I help you?"

    def test_assistant_with_name(self) -> None:
        """Test creating an assistant message with a name."""
        msg = llm.messages.assistant(
            "Hello! How can I help you?",
            name="Claude",
            model_id="openai/gpt-5",
            provider_id="openai",
        )

        assert isinstance(msg, llm.AssistantMessage)
        assert msg.role == "assistant"
        assert msg.name == "Claude"
        assert len(msg.content) == 1
        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello! How can I help you?"

    def test_assistant_with_content_part(self) -> None:
        """Test creating an assistant message with a single content part."""
        text_obj = llm.Text(text="Hello! How can I help you?")
        msg = llm.messages.assistant(
            text_obj, model_id="openai/gpt-5", provider_id="openai"
        )

        assert isinstance(msg, llm.AssistantMessage)
        assert msg.role == "assistant"
        assert msg.name is None
        assert len(msg.content) == 1
        assert msg.content[0] is text_obj

    def test_assistant_with_mixed_sequence(self) -> None:
        """Test creating an assistant message with a sequence of mixed content."""
        text_obj = llm.Text(text="Here's my response:")
        content_list = ["Hello", text_obj, "World"]
        msg = llm.messages.assistant(
            content_list, model_id="openai/gpt-5", provider_id="openai"
        )

        assert isinstance(msg, llm.AssistantMessage)
        assert msg.role == "assistant"
        assert msg.name is None
        assert len(msg.content) == 3

        assert isinstance(msg.content[0], llm.Text)
        assert msg.content[0].text == "Hello"

        assert msg.content[1] is text_obj

        assert isinstance(msg.content[2], llm.Text)
        assert msg.content[2].text == "World"

    def test_assistant_with_empty_sequence(self) -> None:
        """Test creating an assistant message with an empty sequence."""
        msg = llm.messages.assistant([], model_id="openai/gpt-5", provider_id="openai")

        assert isinstance(msg, llm.AssistantMessage)
        assert msg.role == "assistant"
        assert msg.name is None
        assert len(msg.content) == 0
