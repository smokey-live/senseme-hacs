"""Support for Big Ass Fans SenseME switches."""

from typing import Any

from aiosenseme import SensemeFan

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SensemeEntity

FAN_SWITCHES = (
    ("sleep_mode", "sleep_mode", "Sleep Mode"),
    ("motion_fan_auto", "motion_fan_auto", "Motion"),
)

FAN_LIGHT_SWITCHES = (("motion_light_auto", "motion_light_auto", "Light Motion"),)

LIGHT_SWITCHES = (
    ("sleep_mode", "sleep_mode", "Sleep Mode"),
    ("motion_light_auto", "motion_light_auto", "Motion"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SenseME switches."""
    device = entry.runtime_data
    switches: list[HASensemeSwitch] = []

    if device.is_fan:
        switches.extend(HASensemeSwitch(device, *args) for args in FAN_SWITCHES)
        if device.has_light:
            switches.extend(
                HASensemeSwitch(device, *args) for args in FAN_LIGHT_SWITCHES
            )
    elif device.is_light:
        switches.extend(HASensemeSwitch(device, *args) for args in LIGHT_SWITCHES)

    async_add_entities(switches)


class HASensemeSwitch(SensemeEntity, SwitchEntity):
    """Representation of a SenseME switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, device: SensemeFan, switch_type: str, attr: str, switch_name: str
    ) -> None:
        """Initialize the entity."""
        self._device_attr = attr
        super().__init__(device, f"{device.name} {switch_name}")
        self._attr_unique_id = f"{device.uuid}-SWITCH-{switch_type}"

    @property
    def is_on(self) -> bool:
        """Return whether the switch is on."""
        return getattr(self._device, self._device_attr)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        setattr(self._device, self._device_attr, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        setattr(self._device, self._device_attr, False)
