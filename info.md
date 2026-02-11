# Alerte Nowcasting Meteo

Integrare pentru Home Assistant care monitorizează alertele meteo nowcasting din România.

## Caracteristici

- ✅ Monitorizare automată a alertelor meteo
- 🔔 Notificări pentru fenomene extreme
- 📍 Filtrare inteligentă pe județe (selectează doar ce te interesează)
- 🎨 Iconițe dinamice
- 📊 Atribute detaliate pentru Lovelace
- 🔄 Actualizare la 5 minute

## Instalare

1. Instalează prin HACS sau copiază manual
2. Restart Home Assistant
3. Adaugă integrarea prin UI: Settings → Devices & Services → Add Integration
4. Caută "Alerte Nowcasting"
5. Configurează URL-ul API

## Utilizare

### Senzor creat

- `sensor.alerta_nowcasting` - Număr alerte active

### Exemple automatizare

Vezi `examples/automations.yaml` pentru:
- Notificare la început de alertă
- Notificare la sfârșit de alertă
- Reminder-uri periodice

### Exemple carduri Lovelace

Vezi `examples/lovelace_cards.yaml` pentru:
- Card simplu
- Card detaliat
- Card Markdown
- Card condiționat
- Grafic istoric

## Configurare avansată

Senzorul include atribute detaliate:
- `alert_title` - Titlul alertei
- `alert_description` - Descriere detaliată
- `counties` - Județe afectate
- `phenomena` - Tip fenomen
- `severity` - Nivel severitate
- `alert_start` / `alert_end` - Interval

## Support

Pentru probleme și întrebări: [GitHub Issues](https://github.com/dan/alerta-nowcasting/issues)
