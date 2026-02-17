# Forum Scout Task Template

## Mission
Zoek op Nederlandse forums naar zakelijke ideeën en markt-opportuniteiten.

## Bronnen (verplicht gebruiken, zonder Brave/web_search)
Gebruik **geen** `web_search` tool en **geen** Brave API-afhankelijke zoekopdrachten.
Ga direct naar onderstaande prioriteitsbronnen en haal signalen daar vandaan.

### Prioriteit A (altijd meenemen)
1. Klacht.nl (nieuwe klachten): https://www.klacht.nl en https://www.klacht.nl/alle-klachten/
2. Kassa Vraag & Beantwoord: https://www.bnnvara.nl/kassa/vraag-beantwoord
3. Radar Forum (actieve topics): https://radar-forum.avrotros.nl/
4. Tweakers GoT: https://gathering.tweakers.net/
5. Allestoringen: https://allestoringen.nl/

### Prioriteit B (sterke aanvullers)
6. Downdetector NL: https://downdetector.nl/
7. Reddit r/geldzaken: https://www.reddit.com/r/geldzaken/new/
8. Reddit r/thenetherlands: https://www.reddit.com/r/thenetherlands/new/
9. KPN Community: https://community.kpn.com/
10. Ziggo Community: https://community.ziggo.nl/
11. Reddit r/juridischadvies: https://www.reddit.com/r/juridischadvies/new/
12. Trustpilot categories: https://www.trustpilot.com/categories
13. FOK! Forum: https://forum.fok.nl/

### Optioneel (account geeft extra waarde)
14. X/Twitter live probleemzoekopdrachten (bij account): https://x.com/search?q=%22storing%22%20(lang%3Anl)&src=typed_query&f=live
15. Facebook-groepen (niche/lokaal, account nodig)
16. LinkedIn content search (B2B frictie, account nodig)

### Overheid/juridisch validatiebronnen
- ConsuWijzer (ACM): https://www.consuwijzer.nl
- Huurcommissie: https://www.huurcommissie.nl
- Juridisch Loket: https://www.juridischloket.nl
- De Geschillencommissie: https://www.degeschillencommissie.nl

## Zoektermen
Gebruik variaties van:
- "Ik wou dat er was..."
- "Waarom bestaat er geen..."
- "Probleem met..."
- "Frustratie over..."
- "Feature request"
- "Dit zou beter moeten"
- "Iemand een tip voor..." (implies gap)

## Focus Gebieden
{CUSTOM_FOCUS}

Als geen specifieke focus gegeven: breed zoeken naar:
- Zakelijke tools/software
- Dagelijkse irritaties
- Markt inefficiënties  
- Service gaps

## Output Format

Lever precies dit format:

```
# Forum Scout Results
Datum: [vandaag]
Focus: [gegeven focus of "breed"]
Aantal ideeën: [X]

---

## Idee 1: [Titel]
**Beschrijving**: [1-2 zinnen]
**Bron**: [platform] - [URL]
**Context**: [Waarom mensen dit willen, welk probleem het oplost]
**Sentiment**: [Positief/Negatief/Neutraal]
**Urgentie**: [Hoe dringend lijkt de behoefte]
**Quotes**: "[relevante quote uit discussie]"

---

## Idee 2: [...]

[Herhaal voor minimaal 10 ideeën]

---

# Samenvatting
- Meest genoemde categorieën: [lijst]
- Sterkste signalen: [top 3]
- Opvallende trends: [observaties]
```

## Kwaliteitseisen
- Minimaal 10 echte, verschillende ideeën
- Echte URLs (geen placeholders)
- Recente discussies (laatste 6 maanden voorkeur)
- Concrete problemen, geen vage wensen
- Nederlandse bronnen of Nederlands-relevante discussies
- Verdeel bevindingen over meerdere categorieën (media, juridisch, communities, nieuws)
- Prioriteer signalen met veel interactie (meerdere reacties/likes/upvotes)

## Tooling-aanpak (zonder Brave)
- Gebruik directe URL’s + pagina-navigatie (browser/web_fetch)
- Gebruik interne zoekfuncties op de genoemde sites waar mogelijk
- Als een bron niet bereikbaar is, documenteer dit kort en ga door naar de volgende bron

## Wat NIET doen
❌ Geen ideeën verzinnen
❌ Geen fake URLs
❌ Geen algemene concepten zonder bewijs
❌ Geen oude/verouderde discussies zonder check

## Time Budget
Max 10 minuten
Als je vastloopt: lever wat je hebt + noteer wat je probeerde

## Success Criteria
✅ 10+ valide ideeën gevonden
✅ Alle URLs kloppen
✅ Duidelijke context per idee
✅ Format correct gebruikt
