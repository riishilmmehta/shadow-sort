import os
import platform
from pathlib import Path


def get_downloads_path() -> Path:
    """Returns the path to the current user's Downloads directory across OSes."""
    system = platform.system()
    if system == "Windows":
        return Path(os.environ["USERPROFILE"]) / "Downloads"
    return Path.home() / "Downloads"

def get_documents_path() -> Path:
    """Returns the path to the current user's Documents directory."""
    system = platform.system()
    if system == "Windows":
        return Path(os.environ["USERPROFILE"]) / "Documents"
    return Path.home() / "Documents"

def get_home_path() -> Path:
    """Returns the path to the user's home directory."""
    return Path.home()
