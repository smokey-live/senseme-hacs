"""Support for Big Ass Fans SenseME occupancy sensors."""

from aiosenseme import SensemeDevice

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
    """Set up SenseME occupancy sensors."""
    device = entry.runtime_data
    if device.has_sensor:
        async_add_entities([HASensemeOccupancySensor(device)])


class HASensemeOccupancySensor(SensemeEntity, BinarySensorEntity):
    """Representation of a SenseME occupancy sensor."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, device: SensemeDevice) -> None:
        """Initialize the entity."""
        super().__init__(device, f"{device.name} Occupancy")
        self._attr_unique_id = f"{device.uuid}-SENSOR"

    @property
    def is_on(self) -> bool:
        """Return whether occupancy is detected."""
        return self._device.motion_detected
