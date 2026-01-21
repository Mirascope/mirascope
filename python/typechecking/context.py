from mirascope import llm


def test_cannot_instantiate_ctx_without_required_deps():
    # The following must type error: ctx should have deps of type int,
    # but is instantiated with None
    ctx: llm.Context[int] = llm.Context()  # pyright: ignore[reportCallIssue]  # noqa: F841
