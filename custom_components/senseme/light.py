"""Support for Big Ass Fans SenseME lights."""

from typing import Any

from aiosenseme import SensemeDevice

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SensemeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SenseME lights."""
    device = entry.runtime_data
    if device.has_light:
        async_add_entities([HASensemeLight(device)])


class HASensemeLight(SensemeEntity, LightEntity):
    """Representation of a SenseME light."""

    def __init__(self, device: SensemeDevice) -> None:
        """Initialize the entity."""
        name = device.name if device.is_light else f"{device.name} Light"
        super().__init__(device, name)
        self._attr_unique_id = f"{device.uuid}-LIGHT"
        if device.is_light:
            self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_min_color_temp_kelvin = device.light_color_temp_min
            self._attr_max_color_temp_kelvin = device.light_color_temp_max
        else:
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def is_on(self) -> bool:
        """Return whether the light is on."""
        return self._device.light_on

    @property
    def brightness(self) -> int:
        """Return the light brightness on Home Assistant's 0-255 scale."""
        return min(self._device.light_brightness * 16, 255)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the light color temperature in Kelvin."""
        if not self._device.is_light:
            return None
        return self._device.light_color_temp

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light and apply supplied attributes."""
        if (color_temp := kwargs.get(ATTR_COLOR_TEMP_KELVIN)) is not None:
            self._device.light_color_temp = color_temp

        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is None:
            self._device.light_on = True
        else:
            self._device.light_brightness = max(round(brightness / 255 * 16), 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        self._device.light_on = False
