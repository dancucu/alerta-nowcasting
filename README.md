# Alerte Nowcasting Meteo - Integrare Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/dan/alerta-nowcasting.svg)](https://github.com/dan/alerta-nowcasting/releases)
[![License](https://img.shields.io/github/license/dan/alerta-nowcasting.svg)](LICENSE)

Integrare personalizată pentru Home Assistant care monitorizează alertele meteo nowcasting din România și crează un senzor cu notificări pentru fenomene meteo extreme.

## 🌟 Caracteristici

- ✅ Monitorizare automată a alertelor meteo nowcasting
- 🔔 Notificări când încep și se termină fenomenele meteo extreme
- 📍 Filtrare pe județe afectate (selectează doar județele care te interesează)
- 🎨 Iconițe dinamice în funcție de tipul fenomenului
- 📊 Atribute detaliate pentru carduri Lovelace
- 🔄 Actualizare automată la fiecare 5 minute
- 🇷🇴 Suport limba română și engleză

## 📦 Instalare

### Metoda 1: Prin HACS (Recomandat)

1. Deschide HACS în Home Assistant
2. Click pe "Integrations"
3. Click pe cele 3 puncte din colțul dreapta sus
4. Selectează "Custom repositories"
5. Adaugă URL-ul: `https://github.com/dan/alerta-nowcasting`
6. Categoria: `Integration`
7. Click pe "Add"
8. Caută "Alerte Nowcasting" în HACS
9. Click pe "Download"
10. Restart Home Assistant

### Metoda 2: Manual

1. Copiază folderul `custom_components/alerta_nowcasting` în directorul `config/custom_components/` din Home Assistant
2. Restart Home Assistant

## ⚙️ Configurare

### Prin UI (Recomandat)

1. Mergi la **Settings** → **Devices & Services**
2. Click pe butonul **"+ Add Integration"**
3. Caută **"Alerte Nowcasting"**
4. Introdu URL-ul API XML (implicit: `https://www.meteoromania.ro/xml/avertizari-nowcasting.xml`)
5. **(Opțional)** Selectează județele pentru care dorești să primești alerte:
   - Poți selecta unul sau mai multe județe din listă
   - Dacă nu selectezi niciun județ, vei primi alerte pentru toată țara
   - Lista include toate cele 42 de județe din România
6. Click pe **"Submit"**

### Alegerea județelor

Pentru exemple de configurări populare și ghiduri de selectare județe, consultă [COUNTIES_EXAMPLES.md](COUNTIES_EXAMPLES.md).

### Prin configuration.yaml (Opțional)

Integrarea suportă Config Flow, deci nu este necesară configurarea manuală în `configuration.yaml`.

## 📊 Senzor

Integrarea creează un senzor cu ID-ul: `sensor.alerta_nowcasting`

### Stare

Valoarea senzorului reprezintă **numărul de alerte meteo active** (filtrate după județele selectate).

### Filtrare județe

Dacă ai selectat județe specifice în configurare, senzorul va afișa **doar alertele care afectează acele județe**. Acest lucru este util pentru:
- Evitarea notificărilor irelevante pentru alte zone ale țării
- Focusare pe alertele care te afectează direct
- Reducerea zgomotului informațional

**Exemplu:** Dacă ai selectat doar "București" și "Ilfov", vei primi doar alerte care menționează aceste județe, ignorând alertele pentru alte regiuni.

### Atribute

| Atribut | Descriere |
|---------|-----------|
| `active_alerts` | Numărul de alerte active |
| `alerts` | Lista completă cu toate alertele (active + viitoare) |
| `configured_counties` | Județele configurate pentru monitorizare ("toate" dacă nu e specificat) |
| `alert_title` | Titlul primei alerte active |
| `alert_description` | Descrierea detaliată a alertei |
| `alert_start` | Data și ora de început a alertei |
| `alert_end` | Data și ora de sfârșit a alertei |
| `counties` | Lista județelor afectate de alerta curentă |
| `phenomena` | Tipul fenomenului meteo |
| `severity` | Nivelul de severitate (yellow/orange/red) |
| `last_update` | Data ultimei actualizări |

## 🎨 Carduri Lovelace

Vezi fișierul [examples/lovelace_cards.yaml](examples/lovelace_cards.yaml) pentru exemple complete de carduri:

### Card simplu

```yaml
type: entity
entity: sensor.alerta_nowcasting
name: Alerte Meteo
icon: mdi:weather-cloudy-alert
```

### Card detaliat cu Markdown

```yaml
type: markdown
title: 🌩️ Alerta Meteo
content: >
  {% set alerts = state_attr('sensor.alerta_nowcasting', 'active_alerts') %}
  {% if alerts > 0 %}
    ## ⚠️ {{ alerts }} alertă(e) activă(e)!
    
    **{{ state_attr('sensor.alerta_nowcasting', 'alert_title') }}**
    
    📍 **Județe:** {{ state_attr('sensor.alerta_nowcasting', 'counties') | join(', ') }}
    
    🌪️ **Fenomen:** {{ state_attr('sensor.alerta_nowcasting', 'phenomena') }}
  {% else %}
    ## ✅ Nicio alertă activă
  {% endif %}
```

## 🤖 Automatizări

Vezi fișierul [examples/automations.yaml](examples/automations.yaml) pentru exemple complete.

### Notificare la începutul unei alerte

```yaml
automation:
  - alias: "Alerta Meteo - Început"
    trigger:
      - platform: state
        entity_id: sensor.alerta_nowcasting
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > 0 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "🌩️ ALERTĂ METEO"
          message: >
            {{ state_attr('sensor.alerta_nowcasting', 'alert_title') }}
```

### Notificare la sfârșitul unei alerte

```yaml
automation:
  - alias: "Alerta Meteo - Sfârșit"
    trigger:
      - platform: state
        entity_id: sensor.alerta_nowcasting
        to: "0"
    action:
      - service: notify.mobile_app
        data:
          title: "✅ Alertă meteo încheiată"
          message: "Fenomenul meteo s-a încheiat."
```

## 🌪️ Tipuri de fenomene suportate

| Fenomen | Iconiță |
|---------|---------|
| Ceață | `mdi:weather-fog` |
| Polei | `mdi:snowflake-melt` |
| Ninsoare abundentă | `mdi:weather-snowy-heavy` |
| Viscol | `mdi:weather-snowy` |
| Ploi torențiale | `mdi:weather-pouring` |
| Grindină | `mdi:weather-hail` |
| Vijelie | `mdi:weather-hurricane` |
| Fulger | `mdi:weather-lightning` |
| Vânt puternic | `mdi:weather-windy` |
| Instabilitate | `mdi:alert-circle` |

## 🔧 Depanare

### Reconfigurare județe

Poți schimba oricând județele monitorizate:

1. Mergi la **Settings** → **Devices & Services**
2. Găsește **"Alerte Nowcasting Meteo"**
3. Click pe **"Configure"** (sau pe cele 3 puncte → **"Configure"**)
4. Modifică lista de județe
5. Click pe **"Submit"**

Senzorul se va actualiza automat la următoarea verificare.

### Verificare log-uri

Adaugă în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.alerta_nowcasting: debug
```

### Erori comune

**"Cannot connect to API"**
- Verifică conexiunea la internet
- Verifică că URL-ul API este corect
- Verifică că API-ul este disponibil

**"Invalid XML"**
- API-ul poate returna date invalide
- Verifică manual URL-ul în browser

### Întrebări frecvente (FAQ)

**Pot selecta multiple județe?**
- Da! Selectorul permite alegerea mai multor județe simultan.

**Ce se întâmplă dacă nu selectez niciun județ?**
- Vei primi alerte pentru toată România, similar cu comportamentul inițial.

**Pot avea mai multe instanțe cu județe diferite?**
- Da! Poți adăuga integrarea de mai multe ori, de exemplu una pentru București și alta pentru zona de munte.

**Alertele se filtrează automat?**
- Da, senzorul va afișa doar alertele care menționează județele tale selectate.

**Pot schimba județele după configurare?**
- Da, vezi secțiunea "Reconfigurare județe" de mai sus.

## 🤝 Contribuții

Contribuțiile sunt binevenite! Te rugăm să:

1. Faci fork la repository
2. Creezi un branch pentru feature-ul tău
3. Commit cu modificările
4. Push pe branch
5. Deschizi un Pull Request

## 📝 Licență

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 🙏 Mulțumiri

- [Home Assistant](https://www.home-assistant.io/) pentru platforma excelentă
- [ANM](https://www.meteoromania.ro/) pentru datele meteo

## 📧 Contact

Pentru probleme și întrebări, deschide un [issue pe GitHub](https://github.com/dan/alerta-nowcasting/issues).

---

**⚠️ Disclaimer:** Această integrare nu este afiliată cu Administrația Națională de Meteorologie (ANM). Este un proiect comunitar independent.
