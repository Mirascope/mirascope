# From Call Args

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Response Models](./response_models.md)
    </div>


`FromCallArgs` is a useful feature in Mirascope that allows you to directly incorporate function arguments into your response models. This enables a seamless integration between LLM outputs and function inputs, providing more flexibility in response generation.

## How FromCallArgs Works

When you use `FromCallArgs` with a field in your response model, you're essentially telling Mirascope to populate that field with the corresponding argument from the function call, rather than expecting it in the LLM's response. Here's a step-by-step explanation:

1. You define a response model with certain fields annotated with `FromCallArgs()`.
2. When you call a function decorated with `@openai.call` (or similar) and specify this response model, Mirascope processes the function call.
3. For fields marked with `FromCallArgs()`, Mirascope takes the values directly from the function arguments, not from the LLM's response.
4. The LLM generates content for the other fields in the response model.
5. Mirascope combines the function arguments (for `FromCallArgs()` fields) with the LLM-generated content to create the final response model instance.

This process ensures that certain fields in your response always match the function inputs, while allowing the LLM to generate content for the rest.

## Basic Usage and Syntax

To use `FromCallArgs`, apply it to a Pydantic model field using `Annotated`. Here's a basic example:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="7 14"
            {% else %}
            ```python hl_lines="7 13"
            {% endif %}
            --8<-- "examples/learn/from_call_args/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}



In this example, we apply `FromCallArgs()` to the `genre` field. This ensures that the `genre` argument passed to the `recommend_book` function is automatically set in the response model's `genre` field, regardless of the LLM's output.

## Benefits of FromCallArgs

1. **Input Preservation**: Retain values from function arguments alongside LLM outputs.
2. **Consistency**: Maintain consistency between inputs and outputs, enhancing data integrity.
3. **Code Simplification**: Eliminate the need to manually add input values to response models.
4. **Type Safety**: When combined with Pydantic's type checking, ensure type safety from input to output.

## Important Notes

- Field names using `FromCallArgs()` must match the function argument names.
- You don't need to mark all function arguments with `FromCallArgs()`; you can selectively use it for required fields.
- `FromCallArgs()` is currently supported only for top-level fields and not within nested models.
- Fields marked with `FromCallArgs()` are populated from function arguments, not from the LLM's response.

## Conclusion

`FromCallArgs` is a practical Mirascope feature that allows for easy integration of function inputs with LLM outputs. It enables more flexible response generation while improving code readability and maintainability. When used appropriately, it can enhance the efficiency of developing LLM-powered applications by ensuring certain fields always reflect the function inputs.

By understanding and utilizing `FromCallArgs` in Mirascope, you can create more sophisticated LLM applications that seamlessly combine user inputs with AI-generated content, maintaining consistency between your function arguments and the final response model.
