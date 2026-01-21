from mirascope import ops


def fetch_and_transform(url: str) -> dict[str, int | str | bool]:
    with ops.span("fetch_and_transform", url=url) as s:
        # Log different event types
        s.info("Starting fetch operation")

        # Simulate fetch
        data = {"status": "ok", "value": 42}
        s.debug("Received response", response_size=len(str(data)))

        # Check for issues
        status = data.get("status", "No Status Found")
        if status != "ok":
            s.warning("Unexpected status", status=status)

        # Transform
        s.info("Transforming data")
        result = {"transformed": True, **data}

        s.set(success=True)
        return result


result = fetch_and_transform("https://api.example.com/data")
print(result)
