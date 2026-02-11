"""Constants for Alerte Nowcasting integration."""

DOMAIN = "alerta_nowcasting"
NAME = "Alerte Nowcasting Meteo"

# Configuration
CONF_API_URL = "api_url"
CONF_COUNTIES = "counties"
DEFAULT_API_URL = "https://www.meteoromania.ro/xml/avertizari-nowcasting.xml"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minute
DEFAULT_NAME = "Alerta Nowcasting"

# Atribute senzor
ATTR_ALERTS = "alerts"
ATTR_ACTIVE_ALERTS = "active_alerts"
ATTR_COUNTIES = "counties"
ATTR_PHENOMENA = "phenomena"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_SEVERITY = "severity"
ATTR_DESCRIPTION = "description"
ATTR_LAST_UPDATE = "last_update"

# Tipuri fenomene
PHENOMENA_TYPES = {
    "ceata": "Ceață",
    "polei": "Polei",
    "ninsoare": "Ninsoare abundentă",
    "viscol": "Viscol",
    "ploi_torentiale": "Ploi torențiale",
    "grindina": "Grindină",
    "vijelie": "Vijelie",
    "fulger": "Descărcări electrice frecvente",
    "vant_puternic": "Vânt puternic",
    "instabilitate": "Instabilitate atmosferică",
}

# Niveluri severitate
SEVERITY_LEVELS = {
    "galben": "yellow",
    "portocaliu": "orange",
    "rosu": "red",
}

# Iconițe pentru diferite fenomene
PHENOMENA_ICONS = {
    "ceata": "mdi:weather-fog",
    "polei": "mdi:snowflake-melt",
    "ninsoare": "mdi:weather-snowy-heavy",
    "viscol": "mdi:weather-snowy",
    "ploi_torentiale": "mdi:weather-pouring",
    "grindina": "mdi:weather-hail",
    "vijelie": "mdi:weather-hurricane",
    "fulger": "mdi:weather-lightning",
    "vant_puternic": "mdi:weather-windy",
    "instabilitate": "mdi:alert-circle",
    "default": "mdi:weather-cloudy-alert",
}

# Lista județelor din România
ROMANIAN_COUNTIES = [
    "Alba",
    "Arad",
    "Argeș",
    "Bacău",
    "Bihor",
    "Bistrița-Năsăud",
    "Botoșani",
    "Brașov",
    "Brăila",
    "București",
    "Buzău",
    "Caraș-Severin",
    "Călărași",
    "Cluj",
    "Constanța",
    "Covasna",
    "Dâmbovița",
    "Dolj",
    "Galați",
    "Giurgiu",
    "Gorj",
    "Harghita",
    "Hunedoara",
    "Ialomița",
    "Iași",
    "Ilfov",
    "Maramureș",
    "Mehedinți",
    "Mureș",
    "Neamț",
    "Olt",
    "Prahova",
    "Satu Mare",
    "Sălaj",
    "Sibiu",
    "Suceava",
    "Teleorman",
    "Timiș",
    "Tulcea",
    "Vaslui",
    "Vâlcea",
    "Vrancea",
]
