try:
    from openai.types.chat import ChatCompletionAudio
except ImportError:
    ChatCompletionAudio = None
