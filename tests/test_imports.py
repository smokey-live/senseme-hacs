"""Import tests against the installed Home Assistant version."""

import importlib

import pytest

MODULES = (
    "custom_components.senseme",
    "custom_components.senseme.config_flow",
    "custom_components.senseme.fan",
    "custom_components.senseme.light",
    "custom_components.senseme.binary_sensor",
    "custom_components.senseme.switch",
)


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    """Integration modules import with current Home Assistant APIs."""
    importlib.import_module(module)
