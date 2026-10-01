import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from framework.config import load_config, resolve  # noqa: E402


def before_all(context):
    context.config_data = load_config()
    os.makedirs(resolve(context.config_data["reports"]["behave_html_dir"]), exist_ok=True)


def before_scenario(context, scenario):
    context.last_check_result = None