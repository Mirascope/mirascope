from inline_snapshot import snapshot

sync_snapshot = snapshot({"response": "28657", "logging": []})
async_snapshot = snapshot({"response": "28657.", "logging": []})
stream_snapshot = snapshot({"response": "28657.", "logging": []})
async_stream_snapshot = snapshot({"response": "28657", "logging": []})
