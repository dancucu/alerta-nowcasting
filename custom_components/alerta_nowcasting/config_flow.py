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

# Schema cu URL și județe
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_URL, default=DEFAULT_API_URL): cv.string,
    }
)

STEP_COUNTIES_DATA_SCHEMA = vol.Schema(
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
    
    def __init__(self):
        """Inițializează config flow."""
        super().__init__()
        self._api_url: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - API URL."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                await self.async_set_unique_id(user_input[CONF_API_URL])
                self._abort_if_unique_id_configured()
                
                # Salveaza URL-ul in variabila de instanta pentru pasul urmator
                self._api_url = user_input[CONF_API_URL]
                # Merge la pasul de selectare judete
                return await self.async_step_counties()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidXML:
                errors["base"] = "invalid_xml"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_counties(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle county selection step."""
        if user_input is not None:
            # Combina datele din ambii pasi
            config_data = {
                CONF_API_URL: self._api_url,
                CONF_COUNTIES: user_input.get(CONF_COUNTIES, []),
            }
            return self.async_create_entry(title="Alerte Nowcasting", data=config_data)
        
        return self.async_show_form(
            step_id="counties",
            data_schema=STEP_COUNTIES_DATA_SCHEMA,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidXML(HomeAssistantError):
    """Error to indicate the XML is invalid."""
