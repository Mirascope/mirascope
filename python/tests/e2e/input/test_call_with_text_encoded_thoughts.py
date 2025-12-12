"""End-to-end tests for a LLM call without tools or structured outputs."""

import inspect

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    E2E_MODEL_IDS,
)
from tests.utils import Snapshot, snapshot_test


def messages(model_id: llm.ModelId) -> list[llm.Message]:
    return [
        llm.messages.system(
            "Always answer with extreme concision, giving the answer and no added context."
        ),
        llm.messages.user(
            "Is the first fibonacci number to end with the digits 57 prime?"
        ),
        llm.messages.assistant(
            content=[
                llm.Thought(
                    thought=inspect.cleandoc(
                        """
                        Let me see... I have instantenously remembered this table of fibonacci
                        numbers with their prime factorizations. That's sure convenient! Let
                        me see if it has the answer:
                        0 : 0
                        1 : 1
                        2 : 1
                        3 : 2
                        4 : 3
                        5 : 5
                        6 : 8 = 23
                        7 : 13
                        8 : 21 = 3 x 7
                        9 : 34 = 2 x 17
                        10 : 55 = 5 x 11
                        11 : 89
                        12 : 144 = 24 x 32
                        13 : 233
                        14 : 377 = 13 x 29
                        15 : 610 = 2 x 5 x 61
                        16 : 987 = 3 x 7 x 47
                        17 : 1597
                        18 : 2584 = 23 x 17 x 19
                        19 : 4181 = 37 x 113
                        20 : 6765 = 3 x 5 x 11 x 41
                        21 : 10946 = 2 x 13 x 421
                        22 : 17711 = 89 x 199
                        23 : 28657

                        There we have it! 28657 is the first fibonacci number ending in 57,
                        and it is prime. I'm supposed to answer with extreme concision, so I'll
                        just say 'Yes.'
                        """
                    )
                ),
                llm.Text(text="Yes."),
            ],
            model_id=model_id,
            provider_id="openai",
            raw_message={"is_dummy_for_testing_purposes": True},
        ),
        llm.messages.user("Please tell me what the number is."),
    ]


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_text_encoded_thoughts(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test call using thought-as-text encoding."""

    @llm.call(model_id, encode_thoughts_as_text=True)
    def call() -> list[llm.Message]:
        return messages(model_id)

    with snapshot_test(snapshot, caplog) as snap:
        response = call()
        pretty = response.pretty()
        snap["response"] = pretty
        assert "28657" in pretty
