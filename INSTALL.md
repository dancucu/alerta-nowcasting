# Ghid de Instalare și Utilizare Alerte Nowcasting

## 📋 Cuprins

1. [Instalare](#instalare)
2. [Configurare](#configurare)
3. [Utilizare](#utilizare)
4. [Troubleshooting](#troubleshooting)

## 🔧 Instalare

### Pas 1: Instalare prin HACS

#### Adăugare repository custom

1. Deschide Home Assistant
2. Navighează la **HACS** (din meniul lateral)
3. Click pe **Integrations**
4. Click pe cele **3 puncte** (⋮) din colțul dreapta sus
5. Selectează **Custom repositories**
6. În câmpul **Repository**, introdu:
   ```
   https://github.com/dan/alerta-nowcasting
   ```
7. În câmpul **Category**, selectează: `Integration`
8. Click pe **ADD**

#### Instalare integrare

1. În HACS, caută **"Alerte Nowcasting"**
2. Click pe integrare
3. Click pe **Download**
4. Selectează versiunea dorită (sau ultimă)
5. Click pe **Download** pentru confirmare
6. **Restart Home Assistant**

### Pas 2: Instalare manuală (alternativă)

1. Descarcă ultimul release de pe GitHub
2. Dezarhivează și copiază folderul `custom_components/alerta_nowcasting` în:
   ```
   /config/custom_components/alerta_nowcasting
   ```
3. Structura finală ar trebui să fie:
   ```
   /config/custom_components/alerta_nowcasting/
   ├── __init__.py
   ├── manifest.json
   ├── sensor.py
   ├── const.py
   ├── config_flow.py
   ├── strings.json
   └── translations/
       ├── en.json
       └── ro.json
   ```
4. **Restart Home Assistant**

## ⚙️ Configurare

### Adăugare integrare

1. Navighează la **Settings** → **Devices & Services**
2. Click pe butonul **+ ADD INTEGRATION** (colț dreapta jos)
3. Caută **"Alerte Nowcasting"**
4. Selectează integrarea

### Configurare URL API

1. În fereastra de configurare, introdu URL-ul API:
   - **Implicit (recomandat):**
     ```
     https://www.meteoromania.ro/xml/avertizari-nowcasting.xml
     ```
   - **Sau URL personalizat** dacă ai alt sursă de date

2. **(Opțional) Selectează județele de monitorizat:**
   - Click pe câmpul **"Județe de monitorizat"**
   - Selectează unul sau mai multe județe din listă (dropdown cu căutare)
   - Poți selecta multiple județe ținând apăsat Ctrl/Cmd
   - **Dacă nu selectezi niciun județ, vei primi alerte pentru toată țara**
   
   **Exemple de configurare:**
   - **Pentru București:** Selectează "București" și "Ilfov"
   - **Pentru Transilvania:** Selectează "Cluj", "Brașov", "Sibiu", "Mureș"
   - **Pentru Moldova:** Selectează "Iași", "Suceava", "Bacău", "Vaslui"
   - **Pentru toată țara:** Nu selecta niciun județ

3. Click pe **SUBMIT**

4. Integrarea va verifica conexiunea și va crea senzorul

### Verificare instalare

1. Navighează la **Developer Tools** → **States**
2. Caută entitatea: `sensor.alerta_nowcasting`
3. Verifică că apare în listă

## 🎯 Utilizare

### Senzorul creat

| Entitate | Descriere | Valori posibile |
|----------|-----------|-----------------|
| `sensor.alerta_nowcasting` | Număr de alerte active | 0, 1, 2, ... |

### Atribute senzor

Accesează atributele în automatizări folosind:
```yaml
{{ state_attr('sensor.alerta_nowcasting', 'NUME_ATRIBUT') }}
```

| Atribut | Tip | Descriere |
|---------|-----|-----------|
| `active_alerts` | număr | Număr alerte active |
| `alerts` | listă | Toate alertele (JSON) |
| `alert_title` | text | Titlul primei alerte |
| `alert_description` | text | Descriere detaliată |
| `alert_start` | datetime | Data/ora început |
| `alert_end` | datetime | Data/ora sfârșit |
| `counties` | listă | Județe afectate |
| `phenomena` | text | Tip fenomen |
| `severity` | text | yellow/orange/red |
| `last_update` | datetime | Ultima actualizare |

### Adăugare card în Lovelace

#### Card simplu

1. În dashboard, click pe **Edit Dashboard**
2. Click pe **+ ADD CARD**
3. Caută **Entity**
4. Selectează `sensor.alerta_nowcasting`
5. Opțional: Personalizează numele și iconița
6. Click pe **SAVE**

#### Card detaliat (Markdown)

1. Click pe **+ ADD CARD**
2. Selectează **Markdown**
3. Copiază codul din `examples/lovelace_cards.yaml`
4. Lipește în câmpul Content
5. Click pe **SAVE**

### Creare automatizări

#### Automatizare pentru notificare la alertă nouă

1. Navighează la **Settings** → **Automations & Scenes**
2. Click pe **+ CREATE AUTOMATION**
3. Click pe **Start with an empty automation**
4. Setează:
   - **Name:** "Notificare alertă meteo"
   - **Trigger:**
     - Type: **State**
     - Entity: `sensor.alerta_nowcasting`
   - **Condition:**
     - Type: **Template**
     - Value template:
       ```yaml
       {{ trigger.to_state.state | int > 0 }}
       ```
   - **Action:**
     - Type: **Call service**
     - Service: `notify.mobile_app_<DEVICE>`
     - Service data:
       ```yaml
       title: "🌩️ ALERTĂ METEO"
       message: >
         {{ state_attr('sensor.alerta_nowcasting', 'alert_title') }}
         
         Județe: {{ state_attr('sensor.alerta_nowcasting', 'counties') | join(', ') }}
       ```

5. Click pe **SAVE**

#### Automatizare pentru notificare când se termină alerta

Similar cu cea de mai sus, dar:
- **Trigger:** State to `0`
- **Message:** "✅ Alerta meteo s-a încheiat"

### Exemple avansate

Pentru mai multe exemple, consultă:
- `examples/automations.yaml` - Automatizări complete
- `examples/lovelace_cards.yaml` - 9 tipuri de carduri diferite

## 🔍 Troubleshooting

### Senzorul nu apare

**Soluție:**
1. Verifică log-urile: **Settings** → **System** → **Logs**
2. Caută erori legate de `alerta_nowcasting`
3. Verifică că ai făcut restart după instalare
4. Șterge și readaugă integrarea

### Nu primesc date

**Verificări:**
1. Testează URL-ul API în browser
2. Verifică conexiunea la internet
3. Verifică că API-ul returnează XML valid
4. Vezi log-urile pentru erori de parsing

### Activare log-uri detaliate

Adaugă în `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.alerta_nowcasting: debug
```

Apoi restart Home Assistant și verifică log-urile.

### Eroare "Cannot connect"

**Cauze posibile:**
- URL API greșit
- Firewall blochează conexiunea
- API-ul nu este disponibil temporar

**Soluție:**
1. Verifică URL-ul în browser
2. Verifică setările de rețea Home Assistant
3. Încearcă din nou mai târziu

### Alerte nu se actualizează

**Verificări:**
1. Verifică că intervalul de actualizare este 5 minute
2. Forțează actualizare: **Developer Tools** → **Services**
   - Service: `homeassistant.update_entity`
   - Entity: `sensor.alerta_nowcasting`
3. Verifică log-urile pentru erori

### Notificările nu funcționează

**Verificări:**
1. Verifică că ai configurat notify service
2. Testează notify service manual
3. Verifică că automation este activată
4. Verifică log-urile pentru erori

## 📞 Suport suplimentar

- **GitHub Issues:** [Raportează o problemă](https://github.com/dan/alerta-nowcasting/issues)
- **Discussions:** [Forum comunitate](https://github.com/dan/alerta-nowcasting/discussions)
- **Wiki:** [Documentație extinsă](https://github.com/dan/alerta-nowcasting/wiki)

## 🔄 Actualizări

### Prin HACS

1. HACS va notifica când există actualizări
2. Click pe notificare
3. Click pe **Update**
4. Restart Home Assistant

### Manual

1. Descarcă noul release
2. Înlocuiește folderul `custom_components/alerta_nowcasting`
3. Restart Home Assistant

---

**Versiune ghid:** 1.0.0  
**Data ultimei actualizări:** 11 februarie 2026
