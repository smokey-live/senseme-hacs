"""The SenseME integration."""

import logging

from aiosenseme import SensemeDevice
from aiosenseme import __version__ as aiosenseme_version
from aiosenseme import async_get_device_by_device_info

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo, format_mac

from .compat import apply_aiosenseme_compatibility_patch
from .const import CONF_INFO, DOMAIN, UPDATE_RATE

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]

_LOGGER = logging.getLogger(__name__)

apply_aiosenseme_compatibility_patch()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SenseME from a config entry."""
    _LOGGER.debug("Using aiosenseme library version %s", aiosenseme_version)

    status, device = await async_get_device_by_device_info(
        info=entry.data[CONF_INFO], start_first=True, refresh_minutes=UPDATE_RATE
    )

    if not status or device is None:
        if device is not None:
            device.stop()
        raise ConfigEntryNotReady(
            f"Could not connect to SenseME device at {entry.data[CONF_INFO]['address']}"
        )

    await device.async_update(not status)
    entry.runtime_data = device
    entry.async_on_unload(device.stop)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class SensemeEntity:
    """Base class for SenseME entities."""

    _attr_should_poll = False

    def __init__(self, device: SensemeDevice, name: str) -> None:
        """Initialize the entity."""
        self._device = device
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, format_mac(self._device.mac))},
            identifiers={(DOMAIN, self._device.uuid)},
            name=self._device.name,
            manufacturer="Big Ass Fans",
            model=self._device.model,
            sw_version=self._device.fw_version,
            suggested_area=self._device.room_name,
        )

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional SenseME state attributes."""
        return {
            "room_name": self._device.room_name,
            "room_type": self._device.room_type,
        }

    @property
    def available(self) -> bool:
        """Return whether the device is available."""
        return self._device.available

    @callback
    def _async_update_from_device(self) -> None:
        """Process an update pushed by the device."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register the device update listener."""
        self._device.add_callback(self._async_update_from_device)

    async def async_will_remove_from_hass(self) -> None:
        """Remove the device update listener."""
        self._device.remove_callback(self._async_update_from_device)
