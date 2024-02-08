"""A script for setting up oxen so we can push data to the repo."""
import os

import oxen  # type: ignore
from oxen.auth import config_auth  # type: ignore
from oxen.user import config_user  # type: ignore
from squad_config import Settings

settings = Settings()

if not os.path.exists("geology-squad"):
    oxen.clone("Mirascope/geology-squad")

if not os.path.exists("~/.config/oxen"):
    os.makedirs("~/.config/oxen")

config_user(settings.full_name, settings.email)
config_auth(settings.oxen_api_key)
