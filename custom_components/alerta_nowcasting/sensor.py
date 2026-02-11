"""Sensor platform for Alerte Nowcasting integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any
import xml.etree.ElementTree as ET

import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_COUNTIES,
    DEFAULT_SCAN_INTERVAL,
    ATTR_ALERTS,
    ATTR_ACTIVE_ALERTS,
    ATTR_COUNTIES,
    ATTR_PHENOMENA,
    ATTR_SEVERITY,
    ATTR_LAST_UPDATE,
    PHENOMENA_ICONS,
    PHENOMENA_TYPES,
    SEVERITY_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Alerte Nowcasting sensor."""
    api_url = entry.data.get(CONF_API_URL)
    selected_counties = entry.data.get(CONF_COUNTIES, [])
    
    coordinator = AlerteNowcastingCoordinator(hass, api_url, selected_counties)
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([AlerteNowcastingSensor(coordinator, entry)], True)


class AlerteNowcastingCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api_url: str, selected_counties: list[str]) -> None:
        """Initialize."""
        self.api_url = api_url
        self.selected_counties = selected_counties
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(30):
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.api_url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        
                        xml_data = await response.text()
                        return self._parse_xml(xml_data)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def _parse_xml(self, xml_data: str) -> dict[str, Any]:
        """Parse XML data and extract alerts."""
        try:
            root = ET.fromstring(xml_data)
            alerts = []
            
            # Parsare diferite structuri XML posibile
            for alert_elem in root.findall(".//avertizare") or root.findall(".//alert") or root.findall(".//warning"):
                alert = self._parse_alert_element(alert_elem)
                if alert:
                    alerts.append(alert)
            
            # Dacă nu sunt alerte în structura de mai sus, încearcă alte variante
            if not alerts:
                for item in root.findall(".//item"):
                    alert = self._parse_item_element(item)
                    if alert:
                        alerts.append(alert)
            
            # Filtrare după județele selectate
            if self.selected_counties:
                alerts = self._filter_alerts_by_counties(alerts)
            
            # Filtrare alerte active
            now = dt_util.now()
            active_alerts = [
                alert for alert in alerts
                if alert.get("start_time") and alert.get("end_time")
                and alert["start_time"] <= now <= alert["end_time"]
            ]
            
            return {
                "alerts": alerts,
                "active_alerts": active_alerts,
                "last_update": dt_util.now().isoformat(),
            }
            
        except ET.ParseError as err:
            _LOGGER.error("Error parsing XML: %s", err)
            return {"alerts": [], "active_alerts": [], "last_update": dt_util.now().isoformat()}

    def _filter_alerts_by_counties(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter alerts to include only those affecting selected counties."""
        filtered_alerts = []
        
        for alert in alerts:
            alert_counties = alert.get("counties", [])
            # Verifică dacă vreun județ din alertă se potrivește cu județele selectate
            # Folosim verificare case-insensitive și eliminăm diacritice pentru flexibilitate
            if any(
                self._normalize_county(county) in [self._normalize_county(c) for c in self.selected_counties]
                for county in alert_counties
            ):
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def _normalize_county(self, county: str) -> str:
        """Normalize county name for comparison (lowercase, strip whitespace)."""
        return county.strip().lower()

    def _parse_alert_element(self, element: ET.Element) -> dict[str, Any] | None:
        """Parse an alert/avertizare XML element."""
        try:
            alert = {}
            
            # Extragere date standard
            for field in ["id", "title", "description", "severity", "phenomena"]:
                value = element.findtext(field) or element.findtext(field.upper())
                if value:
                    alert[field] = value
            
            # Județe afectate
            counties = []
            for county_elem in element.findall(".//county") or element.findall(".//judet"):
                county = county_elem.text or county_elem.get("name")
                if county:
                    counties.append(county)
            alert["counties"] = counties
            
            # Timp start/end
            start_time = element.findtext("start_time") or element.findtext("startTime") or element.findtext("onset")
            end_time = element.findtext("end_time") or element.findtext("endTime") or element.findtext("expires")
            
            if start_time:
                alert["start_time"] = dt_util.parse_datetime(start_time)
            if end_time:
                alert["end_time"] = dt_util.parse_datetime(end_time)
            
            # Severitate
            severity = alert.get("severity", "").lower()
            alert["severity_level"] = SEVERITY_LEVELS.get(severity, "unknown")
            
            return alert if alert else None
            
        except Exception as err:
            _LOGGER.error("Error parsing alert element: %s", err)
            return None

    def _parse_item_element(self, element: ET.Element) -> dict[str, Any] | None:
        """Parse an item XML element (RSS-style feed)."""
        try:
            alert = {
                "title": element.findtext("title", ""),
                "description": element.findtext("description", ""),
                "link": element.findtext("link", ""),
                "pubDate": element.findtext("pubDate", ""),
            }
            
            # Încearcă să extragi data
            if alert["pubDate"]:
                try:
                    alert["start_time"] = dt_util.parse_datetime(alert["pubDate"])
                except:
                    pass
            
            return alert if alert.get("title") else None
            
        except Exception as err:
            _LOGGER.error("Error parsing item element: %s", err)
            return None


class AlerteNowcastingSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Alerte Nowcasting sensor."""

    def __init__(
        self,
        coordinator: AlerteNowcastingCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Alerta Nowcasting"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"
        self._attr_icon = "mdi:weather-cloudy-alert"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return len(self.coordinator.data.get("active_alerts", []))
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        active_alerts = data.get("active_alerts", [])
        
        attributes = {
            ATTR_ACTIVE_ALERTS: len(active_alerts),
            ATTR_ALERTS: data.get("alerts", []),
            ATTR_LAST_UPDATE: data.get("last_update"),
            "configured_counties": self.coordinator.selected_counties if self.coordinator.selected_counties else "toate",
        }
        
        # Adaugă detalii despre prima alertă activă
        if active_alerts:
            first_alert = active_alerts[0]
            attributes[ATTR_COUNTIES] = first_alert.get("counties", [])
            attributes[ATTR_PHENOMENA] = first_alert.get("phenomena", "")
            attributes[ATTR_SEVERITY] = first_alert.get("severity_level", "unknown")
            attributes["alert_title"] = first_alert.get("title", "")
            attributes["alert_description"] = first_alert.get("description", "")
            
            if first_alert.get("start_time"):
                attributes["alert_start"] = first_alert["start_time"].isoformat()
            if first_alert.get("end_time"):
                attributes["alert_end"] = first_alert["end_time"].isoformat()
            
            # Setează iconița în funcție de fenomen
            phenomena = first_alert.get("phenomena", "").lower()
            for key in PHENOMENA_ICONS:
                if key in phenomena:
                    self._attr_icon = PHENOMENA_ICONS[key]
                    break
        else:
            self._attr_icon = "mdi:weather-cloudy"
        
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
