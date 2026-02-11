"""Config flow for Alerte Nowcasting integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
import xml.etree.ElementTree as ET

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_COUNTIES,
    DEFAULT_API_URL,
    DEFAULT_NAME,
    ROMANIAN_COUNTIES,
)

_LOGGER = logging.getLogger(__name__)

# Schema doar cu județe (URL e constant)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_COUNTIES, default=[]): cv.multi_select(
            {county: county for county in sorted(ROMANIAN_COUNTIES)}
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api_url = data[CONF_API_URL]
    
    try:
        async with asyncio.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        raise CannotConnect(f"HTTP {response.status}")
                    
                    xml_data = await response.text()
                    # Verifică dacă XML-ul este valid (poate fi gol, e ok)
                    try:
                        root = ET.fromstring(xml_data)
                        # XML-ul este valid, chiar dacă nu conține alerte
                        _LOGGER.debug(
                            "API connection successful. Root element: %s, children: %d",
                            root.tag,
                            len(list(root))
                        )
                    except ET.ParseError as err:
                        raise InvalidXML(f"Invalid XML: {err}") from err
                    
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Connection error: {err}") from err
    except TimeoutError as err:
        raise CannotConnect("Connection timeout") from err
    except (InvalidXML, CannotConnect):
        raise
    except Exception as err:
        _LOGGER.exception("Unexpected error during validation")
        raise CannotConnect(f"Unexpected error: {err}") from err
    
    return {"title": DEFAULT_NAME}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alerte Nowcasting."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - Selectare județe."""
        if user_input is not None:
            # Verifica unicitate basata pe URL (constant)
            await self.async_set_unique_id(DEFAULT_API_URL)
            self._abort_if_unique_id_configured()
            
            # Creaza entry cu URL default și județele selectate
            config_data = {
                CONF_API_URL: DEFAULT_API_URL,
                CONF_COUNTIES: user_input.get(CONF_COUNTIES, []),
            }
            return self.async_create_entry(title="Alerte Nowcasting", data=config_data)
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )
    
    @staticmethod
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options for Alerte Nowcasting."""
    
    def __init__(self, config_entry):
        """Inițializează options flow."""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """Handle options step."""
        if user_input is not None:
            # Actualizează opțiunile cu județele selectate
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options={
                    CONF_COUNTIES: user_input.get(CONF_COUNTIES, []),
                }
            )
            # Reload integrarea cu noile opțiuni
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")
        
        # Preiau județele curente din opțiuni sau din data
        current_counties = self.config_entry.options.get(
            CONF_COUNTIES,
            self.config_entry.data.get(CONF_COUNTIES, [])
        )
        
        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_COUNTIES,
                    default=current_counties
                ): cv.multi_select(
                    {county: county for county in sorted(ROMANIAN_COUNTIES)}
                ),
            }
        )
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidXML(HomeAssistantError):
    """Error to indicate the XML is invalid."""
