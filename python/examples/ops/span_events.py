from mirascope import ops


def fetch_and_transform(url: str) -> dict:
    with ops.span("fetch_and_transform", url=url) as s:
        # Log different event types
        s.info("Starting fetch operation")

        # Simulate fetch
        data = {"status": "ok", "value": 42}
        s.debug("Received response", response_size=len(str(data)))

        # Check for issues
        if data.get("status") != "ok":
            s.warning("Unexpected status", status=data.get("status"))

        # Transform
        s.info("Transforming data")
        result = {"transformed": True, **data}

        s.set(success=True)
        return result


result = fetch_and_transform("https://api.example.com/data")
print(result)
