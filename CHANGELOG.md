# Changelog

Toate modificările importante ale acestui proiect vor fi documentate în acest fișier.

Formatul este bazat pe [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
și acest proiect respectă [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-02-11

### 🐛 Bug Fixes
- **Eroare "Unexpected error" la instalare** - Rezolvată problema cu schema de configurare
- **Selector județe** - Folosește acum cv.multi_select în loc de selector custom
- **Validare îmbunătățită** - Schema corectă pentru voluptuous

## [1.1.1] - 2026-02-11

### 🐛 Bug Fixes
- **Instalare cu XML gol** - Integrarea poate fi acum instalată chiar dacă nu există alerte active
- **Validare îmbunătățită** - Config flow acceptă API-uri care returnează XML-uri goale dar valide
- **Logging îmbunătățit** - Mesaje de debug pentru parsarea XML-urilor goale
- **Gestionare erori** - Tratare mai robustă a timeout-urilor și erorilor de conexiune

### 📝 Modificări
- XML-urile fără alerte nu mai cauzează erori de validare la instalare
- Senzorul funcționează corect când nu există alerte meteo (afișează 0)
- Log-uri informative când XML-ul este gol (comportament normal, nu eroare)

## [1.1.0] - 2026-02-11

### ✨ Adăugat
- **Selector de județe în configurare** - Acum poți selecta specific județele pentru care dorești să primești alerte
- Lista completă cu toate cele 42 de județe din România
- Filtrare automată a alertelor bazată pe județele selectate
- Atribut nou `configured_counties` în senzor care afișează județele monitorizate
- Suport pentru configurații multiple (diferite județe per instanță)
- Documentație extinsă cu exemple de configurări pe județe (COUNTIES_EXAMPLES.md)
- Normalizare județe pentru comparații case-insensitive

### 🔧 Modificat
- Interfața de configurare include acum selector dropdown cu căutare pentru județe
- Cardurile Lovelace actualizate pentru a afișa județele configured
- README și documentația actualizate cu informații despre filtrarea pe județe

### 📚 Documentație
- Adăugat COUNTIES_EXAMPLES.md cu peste 10 exemple de configurări populare
- Actualizat INSTALL.md cu ghid pas-cu-pas pentru selectarea județelor
- Adăugat secțiune FAQ în README
- Adăugat secțiune despre reconfigurarea județelor

## [1.0.0] - 2026-02-11

### ✨ Prima versiune
- Monitorizare alerte meteo nowcasting din România
- Sensor cu atribute detaliate
- Parsare XML flexibilă pentru diferite formate
- Iconițe dinamice bazate pe fenomenul meteo
- Suport pentru Code Yellow, Orange și Red
- Traduceri în română și engleză
- Integrare cu notificări Home Assistant
- 9 tipuri diferite de carduri Lovelace
- 3 exemple de automatizări complete
- Documentație completă
- Suport HACS

### 🎯 Caracteristici principale
- Actualizare automată la 5 minute
- Atribute detaliate: titlu, descriere, județe, fenomen, severitate, timpi
- Config Flow pentru configurare prin UI
- Coordinator pentru gestionare eficientă a datelor
- Suport pentru multiple tipuri de fenomene meteo

[1.1.0]: https://github.com/dan/alerta-nowcasting/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dan/alerta-nowcasting/releases/tag/v1.0.0
