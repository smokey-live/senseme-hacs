"""Tests for aiosenseme compatibility helpers."""

import asyncio
import importlib.util
from pathlib import Path

from aiosenseme import SensemeDevice
import pytest

COMPAT_PATH = Path(__file__).parents[1] / "custom_components" / "senseme" / "compat.py"
SPEC = importlib.util.spec_from_file_location("senseme_compat", COMPAT_PATH)
assert SPEC is not None and SPEC.loader is not None
COMPAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPAT)
_async_update = COMPAT._async_update


@pytest.mark.asyncio
async def test_async_update_accepts_python_311_and_newer() -> None:
    """The compatibility method passes tasks, rather than coroutines, to wait."""
    device = SensemeDevice()
    device._is_running = True
    device._first_update.set()
    device._is_connected.set()

    assert await _async_update(device) is True


@pytest.mark.asyncio
async def test_async_update_reports_timeout_and_cleans_up_tasks() -> None:
    """A timed-out update reports failure without leaking pending tasks."""
    device = SensemeDevice()
    device._is_running = True

    before = asyncio.all_tasks()
    assert await _async_update(device, timeout_seconds=0) is False
    assert asyncio.all_tasks() == before
