# Ghid de Migrare

## Migrare la v2.0.0 (Februarie 2026)

### 🚨 SCHIMBARE MAJORĂ: API NOU

Versiunea 2.0.0 aduce o refactorizare completă pentru a utiliza noul endpoint oficial al API-ului Administrației Naționale de Meteorologie (ANM).

#### Ce s-a schimbat?

**API URL NOU:**
- ❌ VECHI: `https://www.meteoromania.ro/xml/avertizari-nowcasting.xml`
- ✅ NOU: `https://www.meteoromania.ro/avertizari-nowcasting-xml.php`

**Format XML diferit:**
- API-ul nou folosește atribute XML în loc de elemente copil
- Extractie automată a județelor din câmpul `zona`
- Suport pentru HTML entities și caractere speciale
- Noi câmpuri: `alert_zona`, `alert_message_type`

**Îmbunătățiri:**
- ✅ Parsare îmbunătățită cu decodare HTML entities
- ✅ Detectare automată a fenomenelor din descriere
- ✅ Suport pentru tipuri de mesaje (Avertizare, Atentionare, Informare)
- ✅ Mapare corectă a codurilor de culoare (0=galben, 1=portocaliu, 2=roșu)
- ✅ Extracție robustă a județelor cu regex

### 📦 Pași de actualizare

#### 1. Actualizează integrarea

**Prin HACS:**
1. Mergi la HACS → Integrations
2. Găsește "Alerte Nowcasting"
3. Click pe "Update" → v2.0.0
4. **Restart Home Assistant**

**Manual:**
1. Descarcă versiunea 2.0.0 de pe GitHub
2. Înlocuiește folderul `custom_components/alerta_nowcasting`
3. **Restart Home Assistant**

#### 2. Reconfigurare NECESARĂ

⚠️ **IMPORTANT:** După actualizare, trebuie să reconfigurezi integrarea cu noul URL!

1. Mergi la **Settings** → **Devices & Services**
2. Găsește "Alerte Nowcasting Meteo"
3. Click pe **"Configure"** sau șterge și re-adaugă integrarea
4. Introdu noul URL: `https://www.meteoromania.ro/avertizari-nowcasting-xml.php`
5. Selectează județele (opțional)
6. Click pe **"Submit"**

#### 3. Verificare funcționare

După reconfigurare, verifică că senzorul funcționează:
- Mergi la **Developer Tools** → **States**
- Caută `sensor.alerta_nowcasting`
- Verifică că are date și nu afișează erori în log

### 📊 Atribute noi

Versiunea 2.0.0 adaugă următoarele atribute:
- `alert_zona` - zona geografică detaliată afectată
- `alert_message_type` - tipul mesajului (Avertizare/Atentionare/Informare)

Cardurile Lovelace existente vor funcționa fără modificări.

### 🐛 Depanare

**Problemă: Senzorul nu afișează date**
- Verifică logs: **Settings** → **System** → **Logs**
- Caută erori legate de "alerta_nowcasting"
- Asigură-te că URL-ul este corect: `https://www.meteoromania.ro/avertizari-nowcasting-xml.php`

**Problemă: Județele nu sunt detectate corect**
- Noua versiune extrage automat județele din câmpul `zona`
- Dacă un județ lipsește, raportează problema pe GitHub

---

## Migrare la v1.1.0

Dacă ai deja instalată integrarea Alerte Nowcasting v1.0.0, acest ghid te va ajuta să actualizezi la v1.1.0 cu noua funcționalitate de filtrare pe județe.

## 🔄 Ce s-a schimbat?

Versiunea 1.1.0 adaugă posibilitatea de a **selecta specific județele** pentru care dorești să primești alerte meteo, reducând astfel notificările irelevante.

### Caracteristici noi:
- ✅ Selector de județe în configurare (42 județe disponibile)
- ✅ Filtrare automată a alertelor
- ✅ Atribut nou `configured_counties` în senzor
- ✅ Suport pentru multiple instanțe cu județe diferite

## 📦 Actualizare

### Pas 1: Actualizează integrarea

#### Prin HACS:
1. Mergi la HACS → Integrations
2. Găsește "Alerte Nowcasting"
3. Click pe "Update" (dacă e disponibil)
4. Restart Home Assistant

#### Manual:
1. Descarcă ultima versiune de pe GitHub
2. Înlocuiește folderul `custom_components/alerta_nowcasting`
3. Restart Home Assistant

### Pas 2: Reconfigurare (Opțional)

După actualizare, integrarea va funcționa **exact ca înainte** - va afișa toate alertele din România.

**Dacă dorești să filtrezi pe județe:**

1. Mergi la **Settings** → **Devices & Services**
2. Găsește "Alerte Nowcasting Meteo"
3. Click pe **"Configure"** (sau pe cele 3 puncte → "Configure")
4. Vei vedea noul câmp **"Județe de monitorizat"**
5. Selectează județele care te interesează
6. Click pe **"Submit"**

## 🔧 Compatibilitate

### Carduri Lovelace
Toate cardurile existente vor funcționa fără modificări. Dacă dorești să afișezi și județele configurate, actualizează cardurile conform exemplelor din `examples/lovelace_cards.yaml`.

**Exemplu de atribut nou:**
```yaml
- type: attribute
  entity: sensor.alerta_nowcasting
  attribute: configured_counties
  name: Județe monitorizate
```

### Automatizări
Toate automatizările existente vor funcționa fără modificări. Senzorul va filtra automat alertele în funcție de județele selectate.

**Nu trebuie să modifici nimic în automatizări pentru filtrare - se face automat!**

### Template-uri
Dacă folosești template-uri personalizate, poți accesa noul atribut:
```jinja
{{ state_attr('sensor.alerta_nowcasting', 'configured_counties') }}
```

## 📊 Exemple de Migrare

### Scenariu 1: Monitorizezi toată țara (comportament implicit)
**Înainte v1.1.0:**
- Primeai toate alertele din România

**După v1.1.0:**
- Nu faci nimic! Comportamentul rămâne identic
- Sau: Accesezi Configuration și lași câmpul județe gol

### Scenariu 2: Te interesează doar București
**Înainte v1.1.0:**
- Primeai toate alertele și le filtrai manual în automatizări

**După v1.1.0:**
1. Configuration → Selectează "București" și "Ilfov"
2. Șterge condition-urile de filtrare din automatizări
3. Senzorul va afișa automat doar alertele pentru București

### Scenariu 3: Multiple zone de interes
**Înainte v1.1.0:**
- Imposibil să ai configurări separate

**După v1.1.0:**
1. Adaugă integrarea de mai multe ori:
   - "Alerte București" → București, Ilfov
   - "Alerte Munte" → Brașov, Prahova
   - "Alerte Toată Țara" → fără selecție
2. Fiecare va crea un senzor separat
3. Creează automatizări separate pentru fiecare

## 🐛 Troubleshooting

### "Nu văd noul câmp pentru județe"
**Soluție:**
1. Verifică că ai actualizat la v1.1.0: **Settings** → **Info** → vezi versiunea în loguri
2. Șterge integrarea complet
3. Restart Home Assistant
4. Adaugă din nou integrarea

### "Senzorul afișează 0 alerte după configurare"
**Normal!** Acum senzorul afișează doar alertele pentru județele tale. Dacă nu sunt alerte active în acel moment, valoarea va fi 0.

**Verificare:**
1. Vezi atributul `configured_counties` - ar trebui să conțină județele tale
2. Dacă vrei să vezi toate alertele, șterge județele din configurare

### "Vreau să revin la comportamentul vechi"
**Soluție:**
1. Configuration → Șterge toate județele selectate
2. Submit
3. Vei primi din nou toate alertele din România

### "Cache-ul afișează alerte vechi"
**Soluție:**
1. Developer Tools → Services
2. Service: `homeassistant.update_entity`
3. Entity: `sensor.alerta_nowcasting`
4. Call Service

## 📝 Note importante

### Backwards Compatibility
Versiunea 1.1.0 este **100% compatibilă** cu v1.0.0. Nu trebuie să modifici nimic dacă nu vrei să folosești noua funcționalitate.

### Performance
Filtrarea se face la nivel de coordinator, înainte de a actualiza senzorul, deci nu afectează performanța.

### Multiple Instances
Poți avea multiple instanțe ale integrării, fiecare cu județe diferite. Fiecare va crea un senzor separat:
- `sensor.alerta_nowcasting`
- `sensor.alerta_nowcasting_2`
- `sensor.alerta_nowcasting_3`

## 🎯 Recomandări

### Pentru majoritatea utilizatorilor:
1. Configurează județele în care locuiești + județele învecinate
2. Lasă automatizările așa cum sunt

### Pentru utilizatori avansați:
1. Creează multiple instanțe pentru zone diferite
2. Vezi [automations_advanced.yaml](examples/automations_advanced.yaml) pentru exemple
3. Vezi [COUNTIES_EXAMPLES.md](COUNTIES_EXAMPLES.md) pentru configurări populare

## 📞 Suport

Dacă întâmpini probleme:
1. Verifică [CHANGELOG.md](CHANGELOG.md) pentru modificări complete
2. Consultă [README.md](README.md) pentru documentație actualizată
3. Deschide un [Issue pe GitHub](https://github.com/dan/alerta-nowcasting/issues)

---

**Data migrării:** 11 februarie 2026  
**Versiune țintă:** 1.1.0  
**Timp estimat:** 2-5 minute
