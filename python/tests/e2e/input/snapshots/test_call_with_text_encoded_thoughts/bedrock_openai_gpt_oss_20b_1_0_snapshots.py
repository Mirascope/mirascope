from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response": '<reasoning>User says: "Please tell me what the number is." They want the number. The earlier answer said 28657. That is the first fib number ending with 57. The user wants the number. So answer: 28657. Ensure concision.</reasoning>28657'
    }
)
