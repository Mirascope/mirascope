from mirascope import ops


def process_batch(items: list[str]) -> list[str]:
    results = []

    with ops.span("batch_processing", batch_size=len(items)) as s:
        for i, item in enumerate(items):
            s.event("item_processed", index=i, item=item)
            results.append(item.upper())

        s.set(processed_count=len(results))

    return results


result = process_batch(["apple", "banana", "cherry"])
print(result)  # ['APPLE', 'BANANA', 'CHERRY']
