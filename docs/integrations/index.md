# Integrations

This section covers various integrations and extensions that enhance Mirascope's functionality, allowing you to seamlessly connect your LLM-powered applications with popular tools, observability platforms, and custom solutions.

Whether you're looking to improve observability, implement robust error handling, or create custom middleware, our integrations offer powerful solutions to common challenges in LLM application development.

!!! note "Background"

    The documentation in this section has been written under the assumption that you already have a grasp on Mirascope's available functionality. If you haven't already, we recommend reading through the [Learn](../learn/index.md) documentation first.

## Available Integrations

Here's an overview of the integrations covered in this section:

- [Custom LLM Provider](./custom_provider.md): Implement support for custom LLM providers not natively supported by Mirascope.
- [HyperDX](./hyperdx.md): Easily integrate HyperDX for powerful observability and debugging features.
- [Langfuse](./langfuse.md): Connect your Mirascope applications with Langfuse for advanced LLM observability and analytics.
- [Logfire](./logfire.md): Integrate with Pydantic's logging tool for enhanced logging capabilities.
- [Middleware](./middleware.md): Learn how to create your own middleware to extend Mirascope's functionality.
- [OpenTelemetry (OTEL)](./otel.md): Implement comprehensive tracing and monitoring for your Mirascope applications.
- [Tenacity](./tenacity.md): Implement robust retry mechanisms and error handling in your Mirascope calls.

## Why Use Integrations?

Integrations play a crucial role in building production-ready LLM applications:

- **Enhanced Observability**: Integrations like OpenTelemetry, Logfire, Langfuse, and HyperDX provide deep insights into your application's performance and behavior.
- **Improved Reliability**: The Tenacity integration helps you build more resilient applications by implementing intelligent retry mechanisms.
- **Extensibility**: Custom middleware and provider integrations allow you to tailor Mirascope to your specific needs and workflows.
- **Ecosystem Compatibility**: These integrations ensure that Mirascope works seamlessly with popular tools and platforms in the AI and software development ecosystem.
