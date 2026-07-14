"""Config flow for SenseME."""

import ipaddress

from aiosenseme import SensemeDevice, async_get_device_by_ip_address, discover_all
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HOST_MANUAL, CONF_INFO, DOMAIN

DISCOVER_TIMEOUT = 5


class SensemeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SenseME discovery config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: list[SensemeDevice] | None = None

    async def _async_entry_for_device(self, device: SensemeDevice) -> FlowResult:
        """Create a config entry for a device."""
        await self.async_set_unique_id(device.uuid)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=device.name,
            data={CONF_INFO: device.get_device_info},
        )

    async def async_step_manual(self, user_input=None) -> FlowResult:
        """Handle manual entry of an IP address."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                ipaddress.ip_address(host)
            except ValueError:
                errors[CONF_HOST] = "invalid_host"
            else:
                device = await async_get_device_by_ip_address(host)
                if device is not None:
                    return await self._async_entry_for_device(device)
                errors[CONF_HOST] = "cannot_connect"

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._discovered_devices is None:
            self._discovered_devices = await discover_all(DISCOVER_TIMEOUT)

        current_ids = {
            config_entry.unique_id
            for config_entry in self._async_current_entries()
            if config_entry.unique_id is not None
        }
        devices = {
            device.uuid: device
            for device in self._discovered_devices
            if device.uuid not in current_ids
        }

        if not devices:
            return await self.async_step_manual(user_input=None)

        choices = {uuid: device.name for uuid, device in devices.items()}
        choices[CONF_HOST_MANUAL] = CONF_HOST_MANUAL

        if user_input is not None:
            selection = user_input[CONF_HOST]
            if selection == CONF_HOST_MANUAL:
                return await self.async_step_manual()
            return await self._async_entry_for_device(devices[selection])

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=next(iter(choices))): vol.In(choices)}
            ),
        )
