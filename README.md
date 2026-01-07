# Norconsult Bæreevneberegning

**Geoteknisk bæreevneanalyse iht. NS-EN 1997-1 (Eurokode 7)**

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-Norconsult-green)

## 📋 Oversikt

Dette programmet beregner bæreevne for fundamenter basert på klassisk plastisitetsteori og Brinch Hansen's metode. Programmet støtter både effektivspenningsanalyse (drenert) og totalspenningsanalyse (udrenert).

### Funksjoner

- ✅ Effektivspenningsanalyse (drenert jord)
- ✅ Totalspenningsanalyse (udrenert jord)
- ✅ Stripefundamenter og rektangulære fundamenter
- ✅ Eksentrisitet og effektivt areal
- ✅ Bæreevnefaktorer Nq, Nγ, Nc med ruhet
- ✅ Skråningsreduksjon
- ✅ Interaktive visualiseringer
- ✅ PDF/HTML rapportgenerering
- ✅ Profesjonelt Norconsult-design

## 🚀 Installasjon

### Lokalt

```bash
# Klon eller kopier prosjektet
cd baereevne_app

# Installer avhengigheter
pip install -r requirements.txt

# Start applikasjonen
streamlit run app.py
```

### Streamlit Cloud

1. Push koden til GitHub
2. Gå til [share.streamlit.io](https://share.streamlit.io)
3. Koble til GitHub-repositoriet
4. Deploy!

## 📁 Filstruktur

```
baereevne_app/
├── app.py              # Hovedapplikasjon (Streamlit UI)
├── models.py           # Dataklasser
├── calculator.py       # Beregningsmotor (EC7-formler)
├── visualizations.py   # Plotly-figurer
├── report.py           # Rapportgenerator
├── requirements.txt    # Python-avhengigheter
├── README.md           # Dokumentasjon
└── .streamlit/
    └── config.toml     # Streamlit-konfigurasjon
```

## 📐 Beregningsgrunnlag

### Bæreevneformel (Effektivspenning)

```
s = fβ · sq · Nq · (γ'·D + q₀ + a) + fβ · sγ · 0.5 · Nγ · γ' · Bo - a
```

### Bæreevneformel (Totalspenning)

```
s = fβ · sc · Nc · su/γM + (γ·D + q₀) · cos²(β)
```

### Bæreevnefaktorer

- **Nq**: Beregnes fra mobiliseringsgrad og ruhet
- **Nγ**: Interpoleres fra tabell (Brinch Hansen)
- **Nc**: π + 2 + √(1-r²) - arcsin(r)

### Effektivt areal

```
Bo = B - 2·|eB|
Lo = L - 2·|eL|
```

## 🎨 Tilpasning

### Farger

Norconsult-farger er definert i CSS:
- Primær: `#006341` (Norconsult grønn)
- Sekundær: `#004d32` (Mørk grønn)
- Aksent: `#ff6b35` (Oransje)

### Formler

Beregningslogikken kan tilpasses i `calculator.py`:
- `beregn_Nq_effektiv()` - Nq-beregning
- `interpoler_Ny()` - Nγ fra tabell
- `beregn_Nc_udrenert()` - Nc for udrenert

## 📚 Referanser

- NS-EN 1997-1:2004+NA:2008 (Eurokode 7)
- Brinch Hansen, J. (1970): A revised and extended formula for bearing capacity
- Statens vegvesen Håndbok V220
- NGF Melding nr. 5: Veiledning for bæreevneberegninger

## 👥 Bidragsytere

Utviklet for geoteknikere i Norconsult Haugesund.

## 📄 Lisens

Norconsult - Internt bruk

---

*Versjon 1.0 - Januar 2026*
