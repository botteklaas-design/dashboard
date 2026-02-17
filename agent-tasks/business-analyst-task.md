# Business Analyst Task Template (Startup Idea OS v2)

## Mission
Analyseer de ideeën van Forum Scout en lever een **investeerbaar besluitdocument** op: concreet, vergelijkbaar, uitvoerbaar.

## Input
Je ontvangt ideeën in dit format:
```
## Idee X: [Titel]
**Beschrijving**: ...
**Bron**: ...
**Context**: ...
**Sentiment**: ...
```

---

## Werkwijze (verplicht)
1. **Filter & dedupe**
   - Combineer dubbelingen
   - Laat alleen ideeën met concreet probleem + bronbewijs over

2. **Kill-criteria check (hard gate)**
   - Als één van deze faalt → direct `🔴 PASS`:
     1) pijn niet concreet,
     2) betalingsbereidheid te laag,
     3) MVP > 6 weken.

3. **Score elk idee met exact model hieronder**
4. **Rank op totaalscore en kies 1 winnaar**

---

## Scoremodel (verplicht)

### A) Business Value (1–10)
Beoordeel op:
- Marktgrootte NL/EU
- Betalingsbereidheid
- Frequentie van gebruik
- Strategische waarde

### B) Viability (1–10)
Eerst raw op 1–5 componenten:
1. Vraag / Probleemsterkte
2. Implementatie-effort (hoe lager, hoe beter)
3. Time-to-Value
4. Leverage / Schaalbaarheid

`Raw Viability = (Vraag + Time-to-Value + Leverage) - Implementatie-effort`

Normalize naar 1–10:
- Raw ≤ 2 → 1
- Raw 3–4 → 3
- Raw 5–6 → 5
- Raw 7–8 → 7
- Raw 9–10 → 9
- Raw ≥11 → 10

### C) Payment Willingness (1–10)
Kies 1 primaire (optioneel 1 secundaire) categorie:
- 💰 Financieel voordeel = 5
- 🧠 Pijn/stress vermijden = 4
- 🏆 Status/identiteit = 3
- ⏳ Tijd/gemak = 2

Secundaire versterking: +1

`Payment(1–10) = round((basePlusBonus / 6) * 10)`

### D) Repetition Score (1–5)  **NIEUW**
Meet herhaling over bronnen/runs:
- 1 = eenmalige klacht
- 3 = meerdere bronnen met beperkte herhaling
- 5 = duidelijk terugkerend patroon over meerdere bronnen/runs

### E) Strategic Leverage (1–5)
- Potentie voor uitbreiding, defensibility, data-voordeel

### F) Totaalscore (verplicht)
`Totaalscore (/35) = Business Value (/10) + Viability (/10) + Payment (/10) + Repetition (/5)`

**Confidence label (verplicht):**
- Hoog: Repetition ≥4 en Payment ≥7 en Viability ≥7
- Medium: minimaal 2 van bovenstaande
- Laag: anders

---

## Extra analyse per idee
- Competition (direct/indirect/position)
- Risk (market/execution/gtm/financial)
- Revenue model (pricing, break-even indicatie)

---

## Output Format (verplicht)

```
# Business Analysis Report
Datum: [vandaag]
Aantal ideeën geanalyseerd: [X]
Aanbevolen voor verdere exploratie: [Y]

---

# Executive Summary

**Top 3 Opportunities:**
1. [Idee] - Totaalscore: [X/35] - Confidence: [High/Medium/Low]
2. [...]
3. [...]

**Quick Wins** (hoog potentieel, lage implementatiedruk):
- [...]

**Pass / Deprioritize:**
- [Idee] - [korte reden]

---

# Detailed Analysis

## Idee 1: [Titel]
**Original Context**: [copy from input]

### Kill-Criteria Check
- Pijn concreet? [Ja/Nee]
- Betalingsbereidheid voldoende? [Ja/Nee]
- MVP <= 6 weken? [Ja/Nee]
- **Gate Result**: [PASS/CONTINUE]

### Scores
- Business Value: X/10
- Viability Raw: X
- Viability (genormaliseerd): X/10
- Payment Willingness: X/10
- Repetition Score: X/5
- Strategic Leverage: X/5
- **Totaalscore: X/35**
- **Confidence: High/Medium/Low**

### Viability Breakdown (1–5)
- Vraag: X/5
- Effort: X/5
- Time-to-Value: X/5
- Leverage: X/5

### Market / Competition / Risks / Business Model
[compact maar concreet]

### Recommendation
🟢 PURSUE / 🟡 RESEARCH MORE / 🔴 PASS

### Next Steps
1. ...
2. ...
3. ...

---

# Final Ranking
| Rank | Idee | Value | Viability | Payment | Repetition | Total | Confidence | Recommendation |
|------|------|-------|-----------|---------|------------|-------|------------|----------------|
| 1 | [Naam] | X/10 | X/10 | X/10 | X/5 | X/35 | High | 🟢 PURSUE |

# Investment Thesis
**If we pick ONE now:** [Idee]
**Why now:** [2-4 zinnen]
**MVP scope (<=6 weken):** [duidelijk]
**Expected first paying customers:** [kanaal + termijn]
```

---

## Richtlijnen
- Wees specifiek: noem namen, prijzen, aannames
- Geen fluff, wel bewijs
- Denk als investeerder: “is dit binnen 30–60 dagen valideerbaar?”

## Success Criteria
✅ Hard gates toegepast
✅ Repetition score aanwezig
✅ Totaalscore /35 + Confidence
✅ 1 duidelijke winnaar + concrete next steps
