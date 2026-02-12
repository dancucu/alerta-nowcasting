"""Sensor platform for Alerte Nowcasting integration."""
from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any
import xml.etree.ElementTree as ET
from html import unescape

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
    COLOR_CODES,
    MESSAGE_TYPES,
    ROMANIAN_COUNTIES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Alerte Nowcasting sensor."""
    api_url = entry.data.get(CONF_API_URL)
    
    # Citesc județele din opțiuni (dacă există) sau din config data
    selected_counties = entry.options.get(CONF_COUNTIES) or entry.data.get(CONF_COUNTIES, [])
    
    # Dacă nu sunt selectate județe, creeaz un senzor pentru toată România
    if not selected_counties:
        selected_counties = ["România"]
    
    coordinator = AlerteNowcastingCoordinator(hass, api_url, selected_counties)
    await coordinator.async_config_entry_first_refresh()
    
    # Creez senzori separați pentru fiecare județ/regiune
    entities = []
    for county in selected_counties:
        entities.append(AlerteNowcastingSensor(coordinator, entry, county))
    
    async_add_entities(entities, True)


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
            
            # Log pentru debugging
            _LOGGER.debug("Parsing XML. Root tag: %s, children count: %d", root.tag, len(list(root)))
            
            # Parsare alerte din noul format API (cu atribute)
            for alert_elem in root.findall(".//avertizare"):
                alert_list = self._parse_alert_element(alert_elem)
                if alert_list:
                    # _parse_alert_element acum returnează lista de alerte (una per județ)
                    alerts.extend(alert_list)
            
            # Log pentru rezultate
            if not alerts:
                _LOGGER.debug("No alerts found in XML. This is normal when there are no active weather warnings.")
            else:
                _LOGGER.debug("Found %d alert(s) in XML (split by county)", len(alerts))
            
            # Filtrare după județele selectate
            if self.selected_counties:
                alerts = self._filter_alerts_by_counties(alerts)
                _LOGGER.debug("After county filtering: %d alert(s)", len(alerts))
            
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
        except Exception as err:
            _LOGGER.error("Unexpected error parsing XML: %s", err)
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

    def _parse_alert_element(self, element: ET.Element) -> list[dict[str, Any]] | None:
        """Parse an avertizare XML element with attributes and split by county."""
        try:
            # Extrage toate atributele din noul format API
            tip_mesaj = element.get("tipMesaj", "")
            nume_tip_mesaj = element.get("numeTipMesaj", "")
            data_inceput = element.get("dataInceput", "")
            data_sfarsit = element.get("dataSfarsit", "")
            zona = element.get("zona", "")
            semnalare = element.get("semnalare", "")
            culoare = element.get("culoare", "")
            nume_culoare = element.get("numeCuloare", "")
            modificat = element.get("modificat", "")
            creat = element.get("creat", "")
            
            # Decodare HTML entities (&#x21B; = ț, &#xE2; = â, etc.)
            zona = unescape(zona)
            semnalare = unescape(semnalare)
            nume_culoare = unescape(nume_culoare)
            
            # Extragere județe din câmpul zona
            counties = self._extract_counties_from_zona(zona)
            
            # Dacă nu s-au găsit județe, returnează o singură alertă cu zona completă
            if not counties:
                _LOGGER.debug("No counties extracted from zona: %s", zona)
                counties = ["Necunoscut"]
            
            # Parsare date și ore - se face o singură dată
            start_time = None
            end_time = None
            
            if data_inceput:
                try:
                    dt = dt_util.parse_datetime(data_inceput)
                    if dt and dt.tzinfo is None:
                        dt = dt.replace(tzinfo=dt_util.UTC).astimezone()
                    start_time = dt
                except Exception as err:
                    _LOGGER.warning("Could not parse start time '%s': %s", data_inceput, err)
            
            if data_sfarsit:
                try:
                    dt = dt_util.parse_datetime(data_sfarsit)
                    if dt and dt.tzinfo is None:
                        dt = dt.replace(tzinfo=dt_util.UTC).astimezone()
                    end_time = dt
                except Exception as err:
                    _LOGGER.warning("Could not parse end time '%s': %s", data_sfarsit, err)
            
            # Detectare fenomen din descriere
            phenomena = self._detect_phenomena(semnalare.lower())
            
            # Creează alerte separate pentru fiecare județ
            alerts = []
            for county in counties:
                # Construire zona specifică pentru acest județ
                county_zona = f"Județul {county}"
                
                # Construire dicționar alert specific județului
                alert = {
                    "id": f"{creat}_{culoare}_{tip_mesaj}_{county}",
                    "title": f"{nume_tip_mesaj} - Cod {nume_culoare}",
                    "description": semnalare,
                    "severity": nume_culoare.lower(),
                    "severity_level": SEVERITY_LEVELS.get(nume_culoare.lower(), "unknown"),
                    "color_code": culoare,
                    "message_type": tip_mesaj,
                    "message_type_name": nume_tip_mesaj,
                    "counties": [county],  # Doar acest județ
                    "zona": county_zona,    # Zona simplificată pentru acest județ
                    "zona_original": zona,  # Păstrează zona originală pentru referință
                    "created": creat,
                    "modified": modificat,
                    "start_time": start_time,
                    "end_time": end_time,
                    # Valori RAW din API pentru atribute
                    "dataInceput": data_inceput,
                    "dataSfarsit": data_sfarsit,
                    "numeCuloare": nume_culoare,
                    "semnalare": semnalare,
                    "zona_api": zona,
                }
                
                if phenomena:
                    alert["phenomena"] = phenomena
                
                alerts.append(alert)
            
            return alerts
            
        except Exception as err:
            _LOGGER.error("Error parsing alert element: %s", err)
            return None
    
    def _extract_counties_from_zona(self, zona: str) -> list[str]:
        """Extract county names from zona field."""
        counties = []
        
        # Elimină tag-uri HTML
        zona_clean = re.sub(r'<[^>]+>', '', zona)
        
        # Caută județe menționate în text
        # Exemplu: "Județul Cluj , zona de munte de peste 1800 m;"
        for county in ROMANIAN_COUNTIES:
            # Variantele posibile: "Județul X", "judetul X", "X"
            patterns = [
                rf'jude[țt]ul\s+{re.escape(county)}',
                rf'\b{re.escape(county)}\b',
            ]
            for pattern in patterns:
                if re.search(pattern, zona_clean, re.IGNORECASE):
                    if county not in counties:
                        counties.append(county)
                    break
        
        return counties
    
    def _detect_phenomena(self, description: str) -> str:
        """Detect phenomena type from description."""
        # Mapare cuvinte cheie la fenomene
        keywords_map = {
            "ceata": "ceata",
            "ceață": "ceata",
            "polei": "polei",
            "ninsoare": "ninsoare",
            "ninsori": "ninsoare",
            "viscol": "viscol",
            "plo": "ploi_torentiale",  # Matches: ploi, ploaie, ploi torențiale
            "torential": "ploi_torentiale",
            "grindina": "grindina",
            "grindină": "grindina",
            "vijelie": "vijelie",
            "furtuna": "vijelie",
            "furtună": "vijelie",
            "fulger": "fulger",
            "descarcari electrice": "fulger",
            "descărcări electrice": "fulger",
            "vant": "vant_puternic",  # Matches: vânt, vant
            "v[aâ]nt": "vant_puternic",
            "rafal": "vant_puternic",
            "rafalã": "vant_puternic",
            "instabilitate": "instabilitate",
        }
        
        for keyword, phenomena in keywords_map.items():
            if keyword in description:
                return phenomena
        
        return "default"


class AlerteNowcastingSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Alerte Nowcasting sensor."""

    def __init__(
        self,
        coordinator: AlerteNowcastingCoordinator,
        entry: ConfigEntry,
        county: str = "România",
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.county = county
        
        # Convertit județul în slug (Ex: "București" -> "bucuresti")
        county_slug = county.lower().replace(" ", "_").replace("ă", "a").replace("î", "i").replace("ț", "t").replace("ş", "s")
        
        self._attr_name = f"Alerta Nowcasting {county}"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{county_slug}"
        self._attr_icon = "mdi:weather-cloudy-alert"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor - alerta or liniste."""
        if self.coordinator.data:
            # Verifică dacă există alerte pentru acest județ (active sau viitoare)
            all_alerts = self.coordinator.data.get("alerts", [])
            county_alerts = self._get_county_alerts(all_alerts)
            if county_alerts:
                return "alerta"
        
        return "liniste"

    def _get_county_alerts(self, alerts: list[dict]) -> list[dict]:
        """Filter alerts for this county."""
        if self.county == "România":
            # Return all alerts
            return alerts
        
        # Filter alerts că conțin acest județ
        county_alerts = []
        for alert in alerts:
            if self.county in alert.get("counties", []):
                county_alerts.append(alert)
        return county_alerts
    
    def _filter_zona_for_county(self, zona_text: str, county: str) -> str:
        """Extract only the relevant part of zona text for the current county."""
        if not zona_text or county == "România":
            return zona_text
        
        # Split după <br> și alte variante
        lines = re.split(r'<br>|<br/>|<br />|;(?=\s*Jude)', zona_text, flags=re.IGNORECASE)
        
        # Caută linia care conține județul curent
        county_pattern = rf'Jude[țt]ul\s+{re.escape(county)}\s*:'
        for line in lines:
            if re.search(county_pattern, line, re.IGNORECASE):
                return line.strip()
        
        # Dacă nu găsește, returnează textul original
        return zona_text

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        all_alerts = data.get("alerts", [])
        active_alerts = self._get_county_alerts(data.get("active_alerts", []))
        
        # Get county-specific alerts for attributes
        county_alerts = self._get_county_alerts(all_alerts)
        
        attributes = {
            ATTR_ACTIVE_ALERTS: len(active_alerts),
            ATTR_ALERTS: county_alerts,
            ATTR_LAST_UPDATE: data.get("last_update"),
            "county": self.county,
        }
        
        # Adaugă detalii despre prima alertă disponibilă pentru acest județ
        # Preferă alertele active, dar dacă nu există, folosește orice alertă disponibilă
        first_alert = None
        if active_alerts:
            first_alert = active_alerts[0]
        elif county_alerts:
            first_alert = county_alerts[0]
        
        if first_alert:
            # Atribute RAW din API
            attributes["numeCuloare"] = first_alert.get("numeCuloare", "")
            attributes["dataInceput"] = first_alert.get("dataInceput", "")
            attributes["dataSfarsit"] = first_alert.get("dataSfarsit", "")
            attributes["semnalare"] = first_alert.get("semnalare", "")
            # Filtrează zona să conțină doar județul curent
            zona_full = first_alert.get("zona_api", "")
            attributes["zona"] = self._filter_zona_for_county(zona_full, self.county)
            
            # Alte informații utile
            attributes[ATTR_COUNTIES] = first_alert.get("counties", [])
            attributes[ATTR_PHENOMENA] = first_alert.get("phenomena", "default")
            attributes[ATTR_SEVERITY] = first_alert.get("severity_level", "unknown")
            attributes["titlu"] = first_alert.get("title", "")
            attributes["tip_mesaj"] = first_alert.get("message_type_name", "")
            
            # Setează iconița în funcție de fenomen
            phenomena = first_alert.get("phenomena", "default")
            self._attr_icon = PHENOMENA_ICONS.get(phenomena, PHENOMENA_ICONS["default"])
        else:
            # Când nu există deloc alerte pentru acest județ
            attributes["numeCuloare"] = None
            attributes["dataInceput"] = None
            attributes["dataSfarsit"] = None
            attributes["semnalare"] = None
            attributes["zona"] = None
            self._attr_icon = "mdi:weather-cloudy"
        
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
