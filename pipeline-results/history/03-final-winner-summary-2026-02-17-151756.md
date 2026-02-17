# Senior Developer Technical Assessment (Recovery Pass)
Datum: 2026-02-17
Run: RECOVERY
Input: latest/02-business-analysis.md

## Top Candidates (Business + Tech)
1. **SMS-kosten transparantie-assistent** — 24/35 (business), Tech Feasibility **8/10**
2. **Pakketvertraging predictor + claim assistent** — 22/35 (business), Tech Feasibility **7/10**
3. **Garantie dossierbouwer** — 21/35 (business), Tech Feasibility **8/10**

## Combined Winner
**SMS-kosten transparantie-assistent**
- Business Value: 8/10
- Viability: 7/10
- Payment: 6/10
- Tech Feasibility: 8/10

## Why this one now
- Concreet geldpijnpunt (onverwachte kosten) met duidelijke gebruikerswaarde.
- MVP kan snel live zonder zware enterprise-integraties.
- Heldere upsell-route: alerts, automatische classificatie, klachten/claim-assistent.

## MVP (max 6 weken)
- Week 1–2: account, provider/factuur import (CSV/PDF), kosten-overzicht
- Week 3–4: drempelalerts, afwijkingsdetectie, premium-SMS detectie
- Week 5–6: klachtgenerator, export, basis analytics + betalingen

## Suggested Stack
- Frontend: Next.js
- Backend: Supabase (Postgres + auth + storage)
- Parsing: eenvoudige OCR + regelgebaseerde extractie
- Jobs: cron/queue voor periodieke checks

## Infra Cost (indicatie)
- MVP (0–1K users): ~€80–€180 / maand
- 10K users: ~€350–€700 / maand

## Main Technical Risks + Mitigation
1. Factuurformat-variatie  
   → mitigatie: provider-specifieke parsers + fallback handmatige mapping
2. Onjuiste classificatie premium-berichten  
   → mitigatie: confidence score + user review flow
3. Privacy/compliance  
   → mitigatie: dataminimalisatie, encryptie-at-rest, heldere bewaartermijnen
