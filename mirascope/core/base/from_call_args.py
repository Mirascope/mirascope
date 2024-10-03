class FromCallArgs:
    """
    If you want to pass the function arguments to the response model, you can use this metadata.

    example:
    ```python
    class Emotions(BaseModel):
    sentences: Annotated[list[str], FromCallArgs()]
    emotions: list[str]

    @model_validator(mode="after")
    def validate_output_length(self) -> Self:
        if len(self.sentences) != len(self.emotions):
            raise ValueError("length mismatch...")
        return self

    @openai.call(... same as before ..., response_model=Emotions)
    @prompt_template(... same as before ...)
    def classify_emotions(sentences: list[str]): ...
    ```
    """

    pass
