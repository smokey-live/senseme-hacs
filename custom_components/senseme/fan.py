"""Support for Big Ass Fans SenseME fans."""

import math
from typing import Any

from aiosenseme import SensemeFan

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from . import SensemeEntity
from .const import (
    PRESET_MODE_WHOOSH,
    SENSEME_DIRECTION_FORWARD,
    SENSEME_DIRECTION_REVERSE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SenseME fans."""
    device = entry.runtime_data
    if device.is_fan:
        async_add_entities([HASensemeFan(device)])


class HASensemeFan(SensemeEntity, FanEntity):
    """Representation of a SenseME ceiling fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.DIRECTION
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_preset_modes = [PRESET_MODE_WHOOSH]

    def __init__(self, device: SensemeFan) -> None:
        """Initialize the entity."""
        super().__init__(device, device.name)
        self._attr_unique_id = f"{device.uuid}-FAN"
        self._attr_speed_count = device.fan_speed_max

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional fan state attributes."""
        return {
            "auto_comfort": self._device.fan_autocomfort.capitalize(),
            "smartmode": self._device.fan_smartmode.capitalize(),
            **super().extra_state_attributes,
        }

    @property
    def is_on(self) -> bool:
        """Return whether the fan is on."""
        return self._device.fan_on

    @property
    def current_direction(self) -> str:
        """Return the fan direction."""
        if self._device.fan_dir == SENSEME_DIRECTION_FORWARD:
            return DIRECTION_FORWARD
        return DIRECTION_REVERSE

    @property
    def percentage(self) -> int:
        """Return the current fan speed as a percentage."""
        return ranged_value_to_percentage(
            self._device.fan_speed_limits, self._device.fan_speed
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the active preset mode."""
        if self._device.fan_whoosh_mode:
            return PRESET_MODE_WHOOSH
        return None

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed as a percentage."""
        self._device.fan_speed = math.ceil(
            percentage_to_ranged_value(self._device.fan_speed_limits, percentage)
        )

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is None:
            self._device.fan_on = True
        else:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        self._device.fan_on = False

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the fan preset mode."""
        if preset_mode != PRESET_MODE_WHOOSH:
            raise ValueError(f"Invalid preset mode: {preset_mode}")
        if self._device.sleep_mode:
            self._device.sleep_mode = False
        self._device.fan_whoosh_mode = True

    async def async_set_direction(self, direction: str) -> None:
        """Set the fan direction."""
        if direction == DIRECTION_FORWARD:
            self._device.fan_dir = SENSEME_DIRECTION_FORWARD
        else:
            self._device.fan_dir = SENSEME_DIRECTION_REVERSE
