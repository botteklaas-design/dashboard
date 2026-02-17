# Strategy Agent Task (Daily EOD)

## Mission
Jij bent de strategy agent (mastermind). Je ontvangt dag-output van:
- Research agent (Forum Scout)
- Business Analyst
- Senior Dev (indien aanwezig)

Doel: scherpere probleemruimte kiezen voor morgen, zodat we naar concrete productkansen convergeren.

## Inputbronnen (lees altijd)
- `/Users/mcbot/.openclaw/workspace/pipeline-results/latest/01-forum-scout.md`
- `/Users/mcbot/.openclaw/workspace/pipeline-results/latest/02-business-analysis.md`
- `/Users/mcbot/.openclaw/workspace/pipeline-results/latest/03-final-winner-summary.md`
- `/Users/mcbot/.openclaw/workspace/pipeline-results/latest/04-log-scan.txt`

## Output (verplicht)
1) Schrijf een dagrapport naar:
- `/Users/mcbot/.openclaw/workspace/pipeline-results/strategy/strategy-daily-YYYY-MM-DD.md`

2) Schrijf de focus-opdracht voor de volgende dag naar:
- `/Users/mcbot/.openclaw/workspace/agent-tasks/research-focus-next-day.md`

3) Schrijf een wekelijkse product-bet snapshot (overschrijf) naar:
- `/Users/mcbot/.openclaw/workspace/pipeline-results/latest/weekly-product-bet-latest.md`

De focus-opdracht moet:
- 1 duidelijke problem space kiezen
- 5-10 concrete zoekrichtingen geven
- expliciete uitsluitingen bevatten (wat NIET te onderzoeken)
- concrete succescriteria bevatten voor morgen

De weekly product-bet snapshot moet bevatten:
- gekozen bet
- ICP
- trigger event
- MVP scope (<=6 weken)
- pricing hypothesis
- 1 validatie-experiment voor komende week

## Kwaliteit
- Concreet, kort, uitvoerbaar
- Geen abstracte visie-taal zonder actiepunten
- Altijd eindigen met: "Next-day scout focus locked."