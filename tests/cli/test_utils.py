from configparser import ConfigParser
from unittest.mock import MagicMock, patch

from mirascope.cli.utils import get_user_mirascope_settings


@patch("mirascope.cli.utils.ConfigParser")
def test_get_user_mirascope_settings(mock_config_parser: MagicMock):
    """Tests that the user"s mirascope settings are loaded correctly."""
    # Setup the mock
    mock_config = MagicMock(spec=ConfigParser)
    mock_config.__getitem__.return_value = {
        "mirascope_location": "mirascope", 
        "prompts_location": "prompts", 
        "versions_location": "versions", 
        "version_file_name": "version.txt",
    }
    mock_config_parser.return_value = mock_config

    # Call the function
    settings = get_user_mirascope_settings()

    # Assert that the settings are loaded correctly
    assert settings.mirascope_location == "mirascope"
    assert settings.prompts_location == "prompts"
