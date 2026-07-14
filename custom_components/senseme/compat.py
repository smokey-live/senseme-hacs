"""Compatibility helpers for the unmaintained aiosenseme library."""

import asyncio

from aiosenseme import SensemeDevice


async def _async_update(
    self: SensemeDevice,
    connection_lost: bool = False,
    timeout_seconds: float = 10,
) -> bool:
    """Wait for a device update using tasks as required by Python 3.11+."""
    if connection_lost:
        self._connection_lost = True
    if not self._is_running:
        self.start()

    tasks = {
        asyncio.create_task(self._first_update.wait()),
        asyncio.create_task(self._is_connected.wait()),
    }
    try:
        done, _ = await asyncio.wait(tasks, timeout=timeout_seconds)
        return len(done) == len(tasks)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def apply_aiosenseme_compatibility_patch() -> None:
    """Patch aiosenseme's Python 3.11-incompatible update method."""
    SensemeDevice.async_update = _async_update  # type: ignore[method-assign]
