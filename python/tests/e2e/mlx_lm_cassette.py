from __future__ import annotations

import hashlib
import struct
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, TypeAlias, cast
from unittest.mock import Mock, patch

import mlx.nn as nn
import pytest
import yaml
from mlx_lm.generate import stream_generate
from mlx_lm.tokenizer_utils import TokenizerWrapper, load
from mlx_lm.utils import hf_repo_to_path

from mirascope import llm

RecordMode = Literal["once", "new_episodes", "all", "none"]


@dataclass
class MLXCassetteResponse:
    """A single response from an MLX model generation."""

    text: str
    token: int
    prompt_tokens: int
    generation_tokens: int
    finish_reason: str | None = None


MLXRecording: TypeAlias = dict[str, list[MLXCassetteResponse]]
"""Dictionary of prompt hashes to list of responses."""


class MLXRecorder:
    """Records MLX model interactions for cassette storage."""

    def __init__(self, mode: RecordMode) -> None:
        """Initialize the recorder.

        Args:
            mode: The recording mode to use.
        """
        self.mode = mode
        self.interactions: MLXRecording = {}

    def record(self, prompt_hash: str, responses: list[MLXCassetteResponse]) -> None:
        """Record an interaction.

        Args:
            prompt_hash: Hash of the prompt tokens.
            responses: List of responses for this prompt.
        """
        self.interactions[prompt_hash] = responses


class MLXCassette:
    """Manages recording and playback of MLX model interactions."""

    def __init__(self, path: Path, record_mode: RecordMode) -> None:
        """Initialize the cassette.

        Args:
            path: Path to the cassette file.
            record_mode: The recording mode to use.

        Raises:
            FileNotFoundError: If mode is 'none' and file doesn't exist.
        """
        self.path = path
        self.record_mode: RecordMode = record_mode

        self.file_recording: MLXRecording = {}
        self.new_recording: MLXRecording = {}

        if path.is_file():
            with open(path) as f:
                data = yaml.safe_load(f)
                for hash, responses in data.get("interactions", {}).items():
                    mlx_responses = [
                        MLXCassetteResponse(**response) for response in responses
                    ]
                    self.file_recording[hash] = mlx_responses
        elif self.record_mode == "none":
            raise FileNotFoundError(f"Cassette file not found: {path}")

    def record(self, prompt_hash: str, responses: list[MLXCassetteResponse]) -> None:
        """Record a new interaction.

        Args:
            prompt_hash: Hash of the prompt tokens.
            responses: List of responses for this prompt.
        """
        self.new_recording[prompt_hash] = responses

    def _save_file(self, interactions: MLXRecording) -> None:
        """Save interactions to the cassette file.

        Args:
            interactions: The interactions to save.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            data = {
                "interactions": {
                    hash: [asdict(response) for response in responses]
                    for hash, responses in interactions.items()
                }
            }
            yaml.safe_dump(data, f)

    def save(self) -> None:
        """Save the cassette based on the recording mode.

        Raises:
            FileExistsError: If mode is 'once' and file already exists.
        """
        if self.record_mode == "once":
            if self.path.is_file():
                raise FileExistsError(f"Cassette file already exists: {self.path}")
            self._save_file(self.new_recording)
        elif self.record_mode == "all":
            self._save_file(self.new_recording)
        elif self.record_mode == "new_episodes":
            recording = self.file_recording
            for hash, responses in self.new_recording.items():
                if hash not in recording:
                    recording[hash] = responses
            self._save_file(recording)
        elif self.record_mode == "none":
            pass


def _hash_prompt(prompt: list[int]) -> str:
    """Hash a tokenized prompt for cassette lookup.

    Args:
        prompt: The tokenized prompt.

    Returns:
        SHA256 hex digest of the prompt tokens.
    """
    hasher = hashlib.sha256()
    for token in prompt:
        hasher.update(struct.pack(">I", token))

    return hasher.hexdigest()


def _patched_stream_generate(
    cassette: MLXCassette,
    model: nn.Module,
    tokenizer: TokenizerWrapper,
    prompt: list[int],
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> Generator[MLXCassetteResponse, None, None]:
    """Patched stream_generate that records/replays from cassette.

    Args:
        cassette: The cassette to use for recording/playback.
        model: The MLX model (may be mocked).
        tokenizer: The tokenizer.
        prompt: The tokenized prompt.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Yields:
        MLXCassetteResponse objects from cache or live generation.

    Raises:
        ValueError: If no cached response and recording is disabled.
    """
    prompt_hash = _hash_prompt(prompt)
    cached_response = cassette.file_recording.get(prompt_hash)

    if cached_response is not None and cassette.record_mode in ("none", "new_episodes"):
        yield from cached_response
        return

    if cassette.record_mode == "none":
        raise ValueError("No cached response found and recording is disabled.")

    interaction: list[MLXCassetteResponse] = []
    for response in stream_generate(model, tokenizer, prompt, *args, **kwargs):
        cassette_response = MLXCassetteResponse(
            text=response.text,
            token=response.token,
            finish_reason=response.finish_reason,
            prompt_tokens=response.prompt_tokens,
            generation_tokens=response.generation_tokens,
        )
        interaction.append(cassette_response)
        yield cassette_response

    cassette.record(prompt_hash, interaction)


def _patched_mlx_lm_load(
    path_or_hf_repo: str,
    tokenizer_config: dict[str, Any] = {},  # noqa: B006
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> tuple[Mock, TokenizerWrapper]:
    """Patched mlx_load that returns a mock model with real tokenizer.

    Args:
        path_or_hf_repo: Path or HuggingFace repo ID.
        tokenizer_config: Tokenizer configuration.
        *args: Additional positional arguments (ignored).
        **kwargs: Additional keyword arguments (ignored).

    Returns:
        Tuple of mock model and real tokenizer.
    """
    path = hf_repo_to_path(path_or_hf_repo)
    tokenizer = load(path, tokenizer_config)
    return Mock(), tokenizer


@contextmanager
def record_mlx_lm(cassette_path: Path, mode: RecordMode) -> Generator[None, None, None]:
    """Context manager for recording/replaying MLX model interactions.

    Args:
        cassette_path: Path to the cassette file.
        mode: The recording mode to use.

    Yields:
        None - use within a with block to record/replay interactions.
    """
    # TODO: Right now, we only patch the MLX client. However, at some point we'll
    # need to generalize it to other clients as well, such as Grok which uses gRPC.
    with ExitStack() as stack:
        cassette = MLXCassette(cassette_path, mode)
        if cassette.record_mode == "none":
            stack.enter_context(
                patch(
                    "mirascope.llm.providers.mlx.provider.mlx_load",
                    new=_patched_mlx_lm_load,
                )
            )

        stack.enter_context(
            patch(
                "mirascope.llm.providers.mlx.mlx.stream_generate",
                new=lambda *args, **kwargs: _patched_stream_generate(
                    cassette, *args, **kwargs
                ),
            )
        )

        try:
            yield
        finally:
            cassette.save()


def _is_mlx_provider(request: pytest.FixtureRequest) -> bool:
    """Check if the current test is using the MLX provider.

    Args:
        request: The pytest fixture request object.

    Returns:
        True if the test is using the MLX provider, False otherwise.
    """
    model_id_param: llm.ModelId | None = None
    if "model_id" in request.fixturenames:
        try:
            model_id_fixture = request.getfixturevalue("model_id")
            if isinstance(model_id_fixture, str):
                model_id_param = model_id_fixture
        except Exception:
            pass

    if model_id_param is None:
        return False

    return model_id_param.startswith("mlx-community/")


def _get_mlx_cassette_path(request: pytest.FixtureRequest) -> Path:
    """Get the path to the MLX cassette for the current test."""
    test_file_path = Path(request.node.fspath)
    sanitized_test_name = (
        request.node.name.replace("/", "_")
        .replace(" ", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace(",", "_")
    )
    return test_file_path.parent / "mlx_lm_cassettes" / f"{sanitized_test_name}.yaml"


@pytest.fixture(autouse=True)
def mlx_cassette_fixture(
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    """Automatically mock MLX operations when testing MLX provider.

    TODO: Currently we have a dedicated cassette fixture for MLX because
      inference results can't be cached with VCR.py (as inference runs locally).
      In the future, we may want to generalize this solution to support new
      providers that require similar treatment, such as Grok which uses gRPC.

    This fixture:
    - Detects when a test is using the MLX provider
    - Mocks mlx_lm.load() to avoid downloading models
    - Patches MLX generation methods to use cassettes
    - Manages cassette lifecycle (load, record, save)
    """
    if not _is_mlx_provider(request):
        # If not using MLX provider, return an empty generator
        yield
        return

    cassette_path = _get_mlx_cassette_path(request)
    record_mode = request.config.getoption("--vcr-record-mode")
    record_mode = request.config.getoption("--vcr-record") or record_mode
    record_mode = record_mode or "none"

    if record_mode not in ["once", "new_episodes", "all", "none"]:
        raise ValueError(f"Invalid VCR record_mode: {record_mode}")

    with record_mlx_lm(cassette_path, cast(RecordMode, record_mode)):
        yield
