"""The Alerte Nowcasting integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alerte Nowcasting from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Adaug listener pentru schimbări de opțiuni
    entry.async_on_change_listener(
        _async_options_update_listener
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return unload_ok


@callback
def _async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ascultă schimbări de opțiuni și reînnodește entry-ul."""
    hass.async_create_task(
        hass.config_entries.async_reload(entry.entry_id)
    )
