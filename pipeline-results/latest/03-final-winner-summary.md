# Senior Developer Technical Assessment
Datum: 2026-02-17
Aantal ideeën geëvalueerd: 3 (top candidates)
Technisch haalbaar: 3
Niet aanbevolen: 0

## Most Feasible
1. Pakketconflict claimbuilder — Tech 9/10
2. Juridische briefgenerator — Tech 8/10
3. Huurgebreken dossierbouwer — Tech 8/10

## Combined Winner
**Huurgebreken dossierbouwer**
- Business Value: 8/10
- Viability: 9/10
- Payment: 8/10
- Tech Feasibility: 8/10

## Why this one now
- Sterke en terugkerende pijn in NL huurmarkt.
- MVP is haalbaar met standaard stack (Next.js + Supabase + object storage).
- Duidelijke 90-dagen route naar betalende gebruikers via tenant unions, legal aid partners en B2C self-serve.

## MVP (6 weken)
- Week 1-2: account, dossierstructuur, upload + tijdlijn
- Week 3-4: bewijslabels, templatebrieven, export PDF
- Week 5-6: intakeflow, basic triage, deploy + analytics

## Infra cost
- MVP (0-1K users): ~€120/maand
- 10K users: ~€450/maand

## Main technical risks
- Juridische actualiteit van sjablonen
- PII/security voor bewijsuploads
- Mitigatie: versiebeheer templates, legal review loop, encrypted storage + audit logs
