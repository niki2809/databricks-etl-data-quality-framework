import os
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "config.yaml")

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def resolve(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)