#!/usr/bin/env python3
"""Build the FLOWSA marketing site.

Generates every page that uses the new design (site.css / site.js) from shared
partials, so the nav, footer and repeated blocks live in one place.

    python3 tools/build_site.py

Sources:
  site_src/home.html     homepage sections ({{RESULTS}} / {{PROCESS}} placeholders)
  site_src/mockups.html  device mockups, split on <!-- @name --> markers
Everything else (page copy) lives in this file.

Not generated (old design, left alone): vsl.html, demo/index.html.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site_src"
YEAR = 2026
WHATSAPP = "https://wa.me/31600000000?text=Hallo%2C%20ik%20wil%20graag%20meer%20weten%20over%20jullie%20systemen"
LOGIN = "https://Login.flowsa.app"


def icon(d, size=22, sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>')


ICONS = {
    "website": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "sms": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 6h4"/><path d="M9 13l2 2 4-4"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "crm": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
    "mail": '<path d="M4 4h16v16H4z"/><polyline points="4 6 12 13 20 6"/>',
    "whatsapp": '<path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/>',
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "steps": '<path d="M3 12h4l3 8 4-16 3 8h4"/>',
    "house": '<path d="M2 20h20M5 20V9l7-5 7 5v11"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>',
    "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "bell": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "map": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "repeat": '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
    "mobile": '<rect x="7" y="2" width="10" height="20" rx="2"/><line x1="11" y1="18" x2="13" y2="18"/>',
    "zap": '<polygon points="13 2 4 14 12 14 11 22 20 10 12 10 13 2"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
}
CHEV = icon('<polyline points="6 9 12 15 18 9"/>', 12, 3).replace('aria-hidden', 'class="dd-chev" aria-hidden')
ARROW = icon('<line x1="3" y1="12" x2="21" y2="12"/><polyline points="15 6 21 12 15 18"/>', 16, 2.5)
CHECK = icon(ICONS["check"], 16, 3)
DOWN = '<polyline points="6 9 12 15 18 9"/>'
FAQ_CHEV = icon(DOWN, 22, 3)
ACC_CHEV = icon(DOWN, 16, 3)


def eur(n):
    return f"{n:,}".replace(",", ".")
BADGE = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l2.4 2.1 3.2-.3.9 3.1 2.8 1.6-1.2 3 1.2 3-2.8 1.6-.9 3.1-3.2-.3L12 22l-2.4-2.1-3.2.3-.9-3.1-2.8-1.6 1.2-3-1.2-3 2.8-1.6.9-3.1 3.2.3z"/>'
         '<path d="M8.5 12.2l2.3 2.3 4.7-4.8" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

PLANS = {"Basic": "/prijzen", "Plus": "/prijzen", "Pro": "/prijzen"}
PLAN_PRICE = {"Basic": 48, "Plus": 96, "Pro": 200}

# ── Features ──────────────────────────────────────────────────────────────
# facts: (value, label) — only numbers that appear elsewhere on the site
FEATURES = [
    dict(slug="website", icon="website", mock="website", plan="Basic",
         name="Professionele website", short="Een website die aanvragen oplevert",
         title="Professionele website",
         lead="Een website die er strak uitziet, gevonden wordt in Google en van bezoekers aanvragen maakt. Wij bouwen hem, jij keurt goed.",
         facts=[("± 5", "werkdagen tot je website gemiddeld live staat"),
                ("100%", "geoptimaliseerd voor desktop én mobiel"),
                ("€48", "per maand, vanaf het Basic-pakket")],
         what="Wat krijg je met een FLOWSA-website?",
         cards=[("search", "Vindbaar in Google", "Je website is vanaf dag één ingericht op lokale zoekopdrachten, zodat mensen in jouw regio je vinden als ze een vakman zoeken."),
                ("mobile", "Perfect op elk scherm", "De meeste mensen zoeken een vakman op hun telefoon. Je website laadt snel en ziet er op elk scherm goed uit."),
                ("file", "Contactformulier & chatwidget", "Bezoekers kunnen direct een offerte aanvragen of een vraag stellen. Elke aanvraag komt meteen bij jou binnen."),
                ("star", "Laat je beste werk zien", "Projecten, reviews en je werkgebied staan overzichtelijk op één plek. Zo zien bezoekers meteen waarom ze voor jou moeten kiezen.")]),
    dict(slug="chatbot", icon="chat", mock="chatbot", plan="Plus",
         name="Chatbot", short="Beantwoordt vragen, 24/7",
         title="Chatbot op jouw website",
         lead="Je website slaapt nooit. Ook om 22:00 op zaterdag krijgt een bezoeker direct antwoord, en plant de chatbot meteen een afspraak in.",
         facts=[("24/7", "online, ook 's avonds en in het weekend"),
                ("3×", "meer aanvragen binnen 8 weken bij een aannemer in aanbouw & verbouw"),
                ("38%", "van die aanvragen kwam buiten werktijd binnen")],
         what="Wat doet de chatbot voor je?",
         cards=[("moon", "Altijd beschikbaar", "De chatbot beantwoordt vragen over je diensten en werkgebied, dag en nacht, ook als jij op de bouwplaats staat."),
                ("filter", "Leads kwalificeren", "Hij vraagt door naar wat de bezoeker precies nodig heeft, zodat jij alleen serieuze aanvragen opvolgt."),
                ("calendar", "Afspraken inplannen", "Past het? Dan plant de chatbot meteen een eerste afspraak in je agenda."),
                ("user", "In jouw toon & huisstijl", "Geen robotachtige teksten. De chatbot praat zoals jij met je klanten praat.")],
         case="/case-de-vries-bouw"),
    dict(slug="belsysteem", icon="phone", mock="belsysteem", plan="Plus",
         name="Belsysteem", short="Neemt op als jij niet kan",
         title="Belsysteem",
         lead="Sta je op een dak of zit je onder een aanrecht? Het belsysteem neemt de telefoon voor je op en zorgt dat geen enkele beller verloren gaat.",
         facts=[("< 60s", "en een gemiste oproep wordt automatisch opgevolgd"),
                ("2 → 11", "leads per maand bij een dakdekkersbedrijf"),
                ("24/7", "bereikbaar, ook buiten werktijd")],
         what="Wat doet het belsysteem?",
         cards=[("phone", "Neemt op als jij niet kan", "Het belsysteem neemt de telefoon voor je op met een natuurlijk klinkende stem en vraagt waar de beller mee geholpen wil worden."),
                ("file", "Gespreksverslag in je mail", "Na elk gesprek krijg je een kort verslag: wie belde, wat hij nodig heeft en hoe je hem bereikt."),
                ("crm", "Direct in je overzicht", "De gegevens van de beller komen meteen in je systeem, inclusief of het om een spoedklus of een offerteaanvraag gaat."),
                ("moon", "Ook buiten werktijd", "Belt iemand 's avonds of in het weekend? Die wordt net zo goed geholpen als op maandagochtend.")],
         case="/case-janssen-dakwerken"),
    dict(slug="sms-bij-gemiste-oproep", icon="sms", mock="belsysteem", plan="Plus",
         name="Sms bij gemiste oproep", short="Binnen 60 seconden terug",
         title="Sms bij gemiste oproep",
         lead="Iedereen mist weleens een oproep. Maar niet iedereen stuurt binnen een minuut een berichtje terug. Wees degene die dat wél doet.",
         facts=[("60 sec", "en de beller heeft automatisch een sms van je"),
                ("0", "onbeantwoorde oproepen bij een dakdekkersbedrijf"),
                ("€96", "per maand, onderdeel van het Plus-pakket")],
         what="Waarom een sms bij een gemiste oproep?",
         cards=[("zap", "Val op tussen de concurrentie", "De meeste vakmensen bellen pas uren later terug. Jij reageert binnen een minuut, nog voordat de klant de volgende belt."),
                ("shield", "Geen verloren leads meer", "Iemand die geen gehoor krijgt, belt vaak meteen een ander. Met een sms houd je het gesprek bij jou."),
                ("user", "Laat zien dat je om klanten geeft", "Een persoonlijk berichtje voelt beter dan een voicemail. Klanten weten meteen dat hun vraag gezien is."),
                ("moon", "Ook 's avonds en in het weekend", "Gemist na werktijd? De sms gaat er toch meteen uit, zodat niemand tot maandag hoeft te wachten.")],
         case="/case-janssen-dakwerken"),
    dict(slug="google-reviews", icon="star", mock="reviews", plan="Basic",
         name="Google Review-systeem", short="Automatisch meer reviews",
         title="Google Review-systeem",
         lead="\"Ik laat zeker een review achter!\" Maar dan vergeten ze het. Wij herinneren je klanten er netjes aan, na elke klus.",
         facts=[("3.9 → 4.8", "Google-beoordeling in 4 maanden bij een hoveniersbedrijf"),
                ("40+", "nieuwe reviews in diezelfde periode"),
                ("€48", "per maand, al in het Basic-pakket")],
         what="Hoe werkt het review-systeem?",
         cards=[("repeat", "Automatisch na elke klus", "Na elke afgeronde klus krijgt je klant vanzelf een verzoek met een directe link naar je Google-pagina."),
                ("bell", "Melding bij ontevredenheid", "Is een klant minder tevreden? Dan krijg jij direct een melding, zodat je het persoonlijk kunt oplossen."),
                ("map", "Hoger in Google Maps", "Meer en betere reviews betekent meer vertrouwen en een hogere plek in Google Maps, precies waar klanten zoeken."),
                ("zap", "Geen omkijken naar", "Je hoeft er niet zelf aan te denken. Het systeem doet het werk, jij ziet de reviews binnenkomen.")],
         case="/case-bakker-tuinen"),
    dict(slug="crm-dashboard", icon="crm", mock="crm", plan="Pro",
         name="CRM-dashboard", short="Al je leads op één plek",
         title="Alles-in-één CRM-dashboard",
         lead="Geen briefjes, losse appjes en vergeten mails meer. Alle leads, gesprekken en afspraken staan op één plek.",
         facts=[("4 min", "gemiddelde reactietijd bij een schildersbedrijf, was ruim 2 dagen"),
                ("1", "overzicht voor chat, telefoon, formulieren en afspraken"),
                ("∞", "gebruikers, leads en klanten in het Pro-pakket")],
         what="Wat zit er in het dashboard?",
         cards=[("crm", "Alle leads op één plek", "Chatgesprekken, terugbelverslagen, formulieren en afspraken. Je ziet in één oogopslag wat er speelt."),
                ("chart", "Pijplijnoverzicht", "Zie per lead waar hij staat: nieuw, afspraak, offerte of gewonnen. Zo valt er niets tussen wal en schip."),
                ("users", "Onbeperkt gebruikers", "Geef je hele team toegang, zonder extra kosten per gebruiker."),
                ("mail", "E-mail & sms vanuit één plek", "Stuur berichten en volg leads op zonder te wisselen tussen apps.")],
         case="/case-van-dijk-schilderwerken"),
    dict(slug="automatische-opvolging", icon="mail", mock="opvolging", plan="Pro",
         name="Automatische opvolging", short="Via e-mail &amp; sms",
         title="Automatische opvolging",
         lead="Offerte verstuurd en dan... stilte. Het systeem volgt automatisch op via e-mail en sms, tot de klant reageert.",
         facts=[("0", "gemiste aanvragen bij een schildersbedrijf"),
                ("E-mail + sms", "opvolging via de kanalen die klanten lezen"),
                ("€200", "per maand, onderdeel van het Pro-pakket")],
         what="Wat doet automatische opvolging?",
         cards=[("repeat", "Vanzelf opvolgen", "Na een offerte of eerste contact krijgt de klant op vaste momenten een vriendelijk berichtje. Jij hoeft er niet aan te denken."),
                ("bell", "Stopt zodra de klant reageert", "Reageert de klant? Dan stopt de reeks automatisch en neem jij het gesprek over."),
                ("user", "Persoonlijk, niet opdringerig", "De berichten zijn in jouw toon geschreven en voelen als een appje van jou, niet als spam."),
                ("chart", "Meer offertes omgezet", "Veel klanten haken niet af omdat ze nee zeggen, maar omdat ze het vergeten. Opvolging haalt die terug.")],
         case="/case-van-dijk-schilderwerken"),
    dict(slug="whatsapp", icon="whatsapp", mock="whatsapp", plan="Pro",
         name="WhatsApp-koppeling", short="Bereik leads waar ze zitten",
         title="WhatsApp-koppeling",
         lead="Je klanten zitten op WhatsApp, dus jij ook. Bereik leads via het kanaal dat ze het meest gebruiken, gewoon vanuit je dashboard.",
         facts=[("1", "inbox voor WhatsApp, sms, e-mail en chat"),
                ("Automatisch", "afspraakbevestigingen en herinneringen"),
                ("€200", "per maand, onderdeel van het Pro-pakket")],
         what="Wat kun je met de WhatsApp-koppeling?",
         cards=[("whatsapp", "Chat waar je klant zit", "Stuur en ontvang WhatsApp-berichten vanuit hetzelfde dashboard als al je andere leads."),
                ("calendar", "Herinneringen voor afspraken", "Klanten krijgen automatisch een bevestiging en herinnering, zodat er minder afspraken mislopen."),
                ("users", "Samen met je team", "Iedereen in je team ziet dezelfde gesprekken. Geen berichten meer op de privételefoon van één persoon."),
                ("crm", "Gekoppeld aan je leads", "Elk gesprek staat bij de juiste lead, met alle eerdere contactmomenten erbij.")]),
    dict(slug="vindbaar-in-google", icon="search", mock="google", plan="Basic",
         name="Vindbaar in Google", short="Lokale SEO vanaf dag één",
         title="Vindbaar in Google",
         lead="Bovenaan staan in Google kost tijd, en wie iets anders belooft, liegt. Maar met de juiste basis begin je wel voorop.",
         facts=[("9", "extra aanvragen via Google in één kwartaal bij een hoveniersbedrijf"),
                ("Lokaal", "ingericht op zoekopdrachten in jouw werkgebied"),
                ("€48", "per maand, al in het Basic-pakket")],
         what="Hoe zorgen we dat je gevonden wordt?",
         cards=[("map", "Lokale zoekopdrachten", "Je website is ingericht op wat klanten in jouw regio zoeken, zoals \"schilder in Utrecht\" of \"dakdekker bij mij in de buurt\"."),
                ("star", "Reviews die meetellen", "Samen met het review-systeem bouw je aan een sterk Google-profiel, en dat helpt je hoger in Google Maps."),
                ("zap", "Snel en technisch in orde", "Snelle laadtijden, goede mobiele weergave en een nette opbouw: de basis waar Google op let."),
                ("filter", "Gekwalificeerde aanvragen", "Mensen die jou via Google vinden, zoeken actief een vakman. Dat zijn betere leads dan gekochte.")],
         case="/case-bakker-tuinen"),
]
FEAT = {f["slug"]: f for f in FEATURES}

CASES = [
    dict(slug="case-de-vries-bouw", who="Aannemersbedrijf", trade="Aanbouw &amp; verbouw", av="AV",
         stat="3×", stat_label="meer aanvragen binnen 8 weken na livegang",
         quote="De chatbot reageert nu ook 's avonds en in het weekend. Dat leverde meteen extra afspraken op die anders gemist zouden zijn.",
         title="3× meer aanvragen binnen 8 weken",
         sub="Hoe een chatbot die dag en nacht klaarstaat een kleine aannemer meteen meer werk opleverde.",
         stats=[("3×", "meer aanvragen"), ("8 wk", "tot zichtbaar resultaat"), ("24/7", "bereikbaar, ook buiten werktijd")],
         challenge="Een aannemersbedrijf in de aanbouw &amp; verbouw runt de zaak grotendeels met een klein team: overdag op de bouwplaats, 's avonds de administratie. Aanvragen kwamen binnen via WhatsApp, telefoon en een simpel contactformulier, maar wie 's avonds of in het weekend op de website kwam, kreeg vaak pas de volgende werkdag antwoord. Een deel van die bezoekers ging intussen bij een concurrent kijken.",
         approach=["FLOWSA bouwde een nieuwe website met een chatbot die continu klaarstaat. De chatbot beantwoordt veelgestelde vragen over diensten en werkgebied, vraagt door naar wat de bezoeker precies nodig heeft, en plant, als het past, meteen een eerste afspraak in. Alles komt binnen in één CRM-dashboard, zodat het team 's ochtends in één overzicht ziet wat er is binnengekomen.",
                   "In de praktijk reageert de chatbot nu ook 's avonds en in het weekend, precies de momenten waarop vroeger niemand klaarstond. Dat leverde meteen extra afspraken op die anders gemist zouden zijn, zonder dat het team er zelf iets voor hoeft te doen."],
         result="Binnen acht weken na livegang steeg het aantal aanvragen met een factor drie. 38% daarvan kwam 's avonds of in het weekend binnen, precies de momenten waarop er voorheen niets gebeurde. Van die extra aanvragen zijn er inmiddels drie omgezet in aanbouwprojecten van gemiddeld €18.000, samen goed voor ruim €50.000 extra omzet in het eerste kwartaal. Het team hoeft nu alleen nog de al-gekwalificeerde aanvragen op te volgen, in plaats van elke avond zelf de berichten door te spitten.",
         used=["chatbot", "crm-dashboard"]),
    dict(slug="case-janssen-dakwerken", who="Dakdekkersbedrijf", trade="Dakrenovatie", av="DR",
         stat="2 → 11", stat_label="leads per maand na het belsysteem",
         quote="Vroeger belden klanten terwijl het team op het dak stond en werd er niet opgenomen. Nu belt het systeem meteen terug.",
         title="Van 2 naar 11 leads per maand",
         sub="Hoe een automatisch belsysteem gemiste oproepen omzette in nieuwe klussen.",
         stats=[("2 → 11", "leads per maand"), ("&lt; 60s", "terugbellen bij gemiste oproep"), ("0", "onbeantwoorde oproepen")],
         challenge="Een dakdekkersbedrijf brengt het grootste deel van de dag hoog op het dak door, precies waar een telefoon opnemen niet kan. Bellers die geen gehoor kregen, hingen op en probeerden vaak meteen een concurrent. Elke gemiste oproep was een kans die stilletjes verdween, zonder dat het bedrijf er ooit iets van merkte.",
         approach=["FLOWSA koppelde het belsysteem aan de bedrijfslijn: een gemiste oproep wordt binnen 60 seconden automatisch teruggebeld, met een natuurlijk klinkende stem die de reden van het gesprek vraagt en de gegevens direct in het CRM zet. Elk gesprek komt terug als notitie, inclusief of het om een spoedklus of een offerteaanvraag ging.",
                   "Vroeger belden klanten terwijl het team op het dak stond en werd er niet opgenomen. Nu belt het systeem meteen terug. Simpel, maar het werkt."],
         result="Het aantal leads per maand ging van gemiddeld twee naar elf. Van alle gemiste oproepen wordt inmiddels 92% binnen 60 seconden teruggebeld; voorheen verdween het grootste deel daarvan zonder dat het bedrijf het ooit merkte. Gemiddeld leidt dat tot zes geboekte dakklussen per maand, tegen een gemiddelde opdrachtwaarde van €4.200: ruim €25.000 aan omzet die er zonder het systeem niet was geweest. Er hoeft niets te veranderen aan de werkdag op het dak; het systeem vangt op wat er anders gemist zou worden.",
         used=["belsysteem", "sms-bij-gemiste-oproep"]),
    dict(slug="case-bakker-tuinen", who="Hoveniersbedrijf", trade="Tuinonderhoud &amp; bestrating", av="TB",
         stat="3.9 → 4.8", stat_label="gemiddelde Google-beoordeling in 4 maanden",
         quote="Het reviewsysteem vraagt automatisch om een beoordeling na een geklaarde klus. De score is nu écht een afspiegeling van het werk.",
         title="Van 3.9 naar 4.8 sterren in 4 maanden",
         sub="Hoe een automatisch reviewsysteem het echte werk van dit hoveniersbedrijf eindelijk zichtbaar maakte op Google.",
         stats=[("3.9 → 4.8", "Google-beoordeling"), ("4 mnd", "tot resultaat"), ("40+", "nieuwe reviews")],
         challenge="Een hoveniersbedrijf levert al jaren goed werk, maar dat was niet te zien op Google: een handvol oude reviews en een score net onder de 4. Tevreden klanten dachten simpelweg niet aan het achterlaten van een beoordeling, terwijl een enkele ontevreden klant wél de moeite nam. Het resultaat: een score die het werk niet eerlijk weergaf, en twijfelende nieuwe klanten.",
         approach=["FLOWSA bouwde een geautomatiseerd reviewsysteem dat na elke afgeronde klus een verzoek stuurt om een beoordeling achter te laten. Elke klant krijgt dezelfde vraag en een directe link naar de Google-pagina. Geeft iemand aan minder tevreden te zijn, dan krijgt het bedrijf meteen een melding, zodat het probleem persoonlijk opgelost kan worden.",
                   "Het reviewsysteem vraagt automatisch om een beoordeling na een geklaarde klus. De score is nu écht een afspiegeling van het geleverde werk."],
         result="Binnen vier maanden steeg de gemiddelde beoordeling van 3.9 naar 4.8 sterren, met een reviewaantal dat groeide van 12 naar 58: niet langer alleen de stem van een enkele ontevreden klant, maar een eerlijke afspiegeling van het werk. Die hogere positie in de Google Maps-resultaten leverde dat kwartaal negen nieuwe aanvragen op van klanten die zelf aangaven het bedrijf via Google te hebben gevonden, goed voor zo'n €14.000 extra omzet.",
         used=["google-reviews", "vindbaar-in-google"]),
    dict(slug="case-van-dijk-schilderwerken", who="Schildersbedrijf", trade="Schilderwerk", av="SW",
         stat="4 min", stat_label="gemiddelde reactietijd, was ruim 2 dagen",
         quote="Er werd vaak pas na het weekend gereageerd. Nu krijgt iedereen binnen een paar minuten antwoord, ook buiten kantoortijd.",
         title="Reactietijd van 2 dagen naar 4 minuten",
         sub="Hoe dit schildersbedrijf nooit meer een aanvraag laat liggen tot na het weekend.",
         stats=[("4 min", "gemiddelde reactietijd"), ("was 2d", "vóór FLOWSA"), ("0", "gemiste aanvragen")],
         challenge="Een schildersbedrijf beheerde aanvragen naast het eigenlijke schilderwerk, meestal 's avonds na een volle werkdag. Aanvragen die vrijdagmiddag binnenkwamen, bleven vaak tot maandag liggen. Tegen die tijd hadden veel klanten allang bij een andere schilder aangeklopt.",
         approach=["FLOWSA combineerde de chatbot met het CRM-dashboard: elke aanvraag krijgt direct een reactie, ook in het weekend en 's avonds. De chatbot stelt de eerste vragen (soort werk, oppervlakte, gewenste periode) en zet alles overzichtelijk klaar, zodat het team zelf alleen nog het gesprek hoeft te vervolgen, zonder dat er iets tussen wal en schip valt.",
                   "Er werd vaak pas na het weekend gereageerd. Nu krijgt iedereen binnen een paar minuten antwoord, ook als er niemand achter de telefoon zit."],
         result="De gemiddelde reactietijd ging van ruim twee dagen naar vier minuten. Waar vroeger zo'n 1 op de 4 aanvragen afhaakte voordat er was gereageerd, wordt nu vrijwel niemand meer koud. Dat betekent 30% meer aanvragen die uitmonden in een geboekte klus, goed voor zo'n €22.000 extra omzet per kwartaal.",
         used=["chatbot", "crm-dashboard", "automatische-opvolging"]),
]

TRADES_MAIN = [
    ("Schilderwerk", '<rect x="3" y="3" width="14" height="6" rx="1"/><path d="M17 6h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-7v3"/><rect x="10" y="14" width="4" height="7" rx="1"/>'),
    ("Loodgieterij", '<path d="M4 4h6v4H4zM7 8v5a3 3 0 0 0 3 3h6"/><path d="M16 13v6M19 16h-6"/><path d="M14 20h4"/>'),
    ("Elektra &amp; installatie", '<polygon points="13 2 4 14 12 14 11 22 20 10 12 10 13 2"/>'),
    ("Aanbouw &amp; verbouw", '<path d="M3 21h18M5 21V10l7-6 7 6v11"/><path d="M9 21v-6h6v6"/><path d="M15 4h3v4"/>'),
    ("Dakrenovatie", '<path d="M2 13l10-9 10 9"/><path d="M5 11l7-6 7 6M8 9.5l4-3.5 4 3.5"/><path d="M5 13v8h14v-8"/>'),
    ("Vloeren &amp; tegels", '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M9 3v6M15 9v6M9 15v6"/>'),
    ("Tuin &amp; bestrating", '<path d="M12 22V12"/><path d="M12 12c0-4 3-7 7-7 0 4-3 7-7 7z"/><path d="M12 15c0-3-2.5-5.5-6-5.5 0 3 2.5 5.5 6 5.5z"/><path d="M4 22h16"/>'),
    ("Klusbedrijven", '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'),
    ("Kozijnen &amp; deuren", '<rect x="4" y="2" width="16" height="20" rx="1"/><path d="M12 2v20M4 12h16"/>'),
    ("CV &amp; warmtepompen", '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>'),
    ("Stukadoors", '<path d="M3 21l7-7"/><rect x="9" y="3" width="12" height="9" rx="1" transform="rotate(0)"/><path d="M10 12l-2 2"/>'),
    ("Timmerwerk", '<path d="M15 12l-8.5 8.5a2.12 2.12 0 0 1-3-3L12 9"/><path d="M17.64 15L22 10.64"/><path d="M20.91 11.7l-1.25-1.25a2.42 2.42 0 0 1 0-3.42l.34-.34a2 2 0 0 0 0-2.83l-.98-.98a2 2 0 0 0-2.83 0L14 4.97"/>'),
]
TRADES_ALL = sorted("""Aannemers|Aanbouw & verbouw|Airco & koeling|Badkamerrenovatie|Behangers|Bestrating|Betonwerk|CV & verwarming|Dakdekkers|Dakgoten & zinkwerk|Elektriciens|Gevelreiniging|Glaszetters|Grondwerk|Hoveniers|Installatiebedrijven|Interieurbouw|Isolatie|Keukenmontage|Klusbedrijven|Kozijnen & deuren|Laadpalen|Loodgieters|Metselaars|Ongediertebestrijding|Overkappingen & veranda's|Rolluiken & zonwering|Schilders|Schoonmaakbedrijven|Schuttingen & tuinhout|Sloopwerk|Stukadoors|Tegelzetters|Timmerlieden|Trappen|Verhuizers|Vloerenleggers|Voegwerk|Warmtepompen|Zonnepanelen""".split("|"))

FAQ_GENERAL = [
    ("Werkt het ook voor mijn branche?", "FLOWSA wordt gebruikt door aannemers, makelaars, klinieken en meer. Schilder, loodgieter, dakdekker of hovenier: als jij klanten wil, werkt het voor jou."),
    ("Hoe snel is alles live?", "Gemiddeld binnen 5 werkdagen. Na het demogesprek vul je een kort formulier in met je bedrijfsgegevens, en dan gaan wij aan de slag."),
    ("Moet ik zelf technische kennis hebben?", "Nee. Wij bouwen en richten alles voor je in. Bij de livegang lopen we samen door hoe het werkt, en daarna kun je altijd bij ons terecht met vragen."),
    ("Zijn belminuten en sms inbegrepen?", "Ja, binnen redelijk gebruik. Bij uitzonderlijk hoog verbruik nemen we eerst contact met je op en rekenen we de extra kosten door tegen kostprijs, zonder verrassingen."),
    ("Hoe werkt de 30 dagen geld-terug-garantie?", "Ben je binnen 30 dagen na livegang niet tevreden? Dan krijg je je geld terug, ook bij jaarlijkse betaling."),
    ("Wat als ik vragen heb?", "Je hebt altijd toegang tot onze klantenservice. Geen chatbot, gewoon een mens. Of stuur ons een berichtje via WhatsApp."),
]

# ── Partials ──────────────────────────────────────────────────────────────

def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/site.css">
</head>
<body>
"""


def dd_item(href, ic, title, sub):
    return (f'            <a href="{href}" class="dd-item"><span class="dd-ic">{icon(ICONS[ic])}</span>'
            f'<span><b>{title}</b><small>{sub}</small></span></a>\n')


def nav(active=""):
    mega = "".join(dd_item(f"/functies/{f['slug']}", f["icon"], f["name"], f["short"]) for f in FEATURES)
    about = "".join([dd_item("/werkwijze", "steps", "Werkwijze", "Zo werken we samen"),
                     dd_item("/vakgebieden", "house", "Vakgebieden", "Voor wie we werken"),
                     dd_item("/cases", "chart", "Cases", "Resultaten van klanten"),
                     dd_item("/contact", "mail", "Contact", "Stel je vraag")])

    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    mm_feats = "".join(f'      <a href="/functies/{f["slug"]}">{f["name"]}</a>\n' for f in FEATURES)
    return f"""  <header class="nav">
    <div class="nav-inner">
      <a href="/" class="logo" aria-label="FLOWSA home">
        <img class="logo-mascot" src="/mascot.svg" alt="" width="34" height="54">
        <span class="logo-text">FLOWSA</span>
      </a>
      <nav class="nav-links" aria-label="Hoofdmenu">
        <div class="dd">
          <button class="dd-btn{' is-active' if active == 'functies' else ''}" type="button" aria-expanded="false">Functies {CHEV}</button>
          <div class="dd-panel dd-mega">
            <div class="dd-title">Systemen &amp; functies <a href="/functies">Bekijk alle functies →</a></div>
            <div class="dd-grid">
{mega}            </div>
          </div>
        </div>
        {a('/prijzen', 'Prijzen', 'prijzen')}
        {a('/cases', 'Cases', 'cases')}
        {a('/werkwijze', 'Werkwijze', 'werkwijze')}
        <div class="dd">
          <button class="dd-btn{' is-active' if active == 'over' else ''}" type="button" aria-expanded="false">Over ons {CHEV}</button>
          <div class="dd-panel dd-small">
            <div class="dd-grid dd-grid-1">
{about}            </div>
          </div>
        </div>
      </nav>
      <div class="nav-right">
        <a href="{LOGIN}" class="nav-login">Inloggen</a>
        <a href="/demo/" class="btn nav-cta">Plan demo</a>
        <button class="burger" id="burger" aria-label="Menu openen" aria-expanded="false" aria-controls="mobile-menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </header>
  <nav class="mobile-menu" id="mobile-menu" aria-label="Mobiel menu">
    <details class="mm-group"><summary>Functies {CHEV}</summary>
      <a href="/functies">Alle functies</a>
{mm_feats}    </details>
    <a href="/prijzen">Prijzen</a>
    <a href="/cases">Cases</a>
    <a href="/werkwijze">Werkwijze</a>
    <details class="mm-group"><summary>Over ons {CHEV}</summary>
      <a href="/vakgebieden">Vakgebieden</a>
      <a href="/contact">Contact</a>
    </details>
    <a href="{LOGIN}" class="mm-login">Inloggen</a>
    <a href="/demo/" class="btn">Plan demo</a>
  </nav>
"""


def footer():
    feats = "".join(f'          <a href="/functies/{f["slug"]}">{f["name"]}</a>\n' for f in FEATURES[:5])
    feats2 = "".join(f'          <a href="/functies/{f["slug"]}">{f["name"]}</a>\n' for f in FEATURES[5:])
    return f"""  <footer class="footer">
    <div class="wrap">
      <div class="footer-top">
        <a href="/" class="logo"><img class="logo-mascot" src="/mascot.svg" alt="" width="40" height="64" style="width:40px;height:64px;"><span class="logo-text">FLOWSA</span></a>
        <div class="footer-top-cta">Klaar om te beginnen? <a href="/demo/" class="btn btn-sm">Plan demo</a></div>
      </div>
      <div class="footer-cols">
        <div class="footer-pitch">
          <h4>Benieuwd wat we voor jouw bedrijf kunnen doen?</h4>
          <a href="/demo/" class="btn">Plan een demo</a>
        </div>
        <div class="footer-col">
          <h4>Links</h4>
          <a href="/prijzen">Prijzen</a>
          <a href="/cases">Cases</a>
          <a href="/functies">Alle functies</a>
          <a href="{LOGIN}">Inloggen</a>
        </div>
        <div class="footer-col">
          <h4>Over ons</h4>
          <a href="/werkwijze">Werkwijze</a>
          <a href="/vakgebieden">Vakgebieden</a>
          <a href="/contact">Contact</a>
          <a href="/demo/">Demo plannen</a>
        </div>
        <div class="footer-col footer-col-wide">
          <h4>Functies</h4>
          <div class="footer-2col"><div>
{feats}          </div><div>
{feats2}          </div></div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© {YEAR} FLOWSA — Alle rechten voorbehouden</span>
        <span>Prijzen exclusief btw</span>
      </div>
    </div>
  </footer>
"""


def tail():
    return '  <script src="/site.js"></script>\n</body>\n</html>\n'


def results(bg="bg-grey"):
    slides = ""
    for c in CASES:
        slides += f"""          <article class="slide">
            <div class="slide-stat"><b>{c['stat']}</b><span>{c['stat_label']}</span></div>
            <div class="slide-body">
              <div class="slide-quote-mark" aria-hidden="true">“</div>
              <p>{c['quote']}</p>
              <div class="slide-foot">
                <div class="slide-who">{c['who']}<span>{c['trade']}</span></div>
                <a href="/{c['slug']}" class="slide-link">Lees case →</a>
              </div>
            </div>
          </article>
"""
    return f"""  <section class="results sec {bg}">
    <div class="wrap">
      <h2 class="h-section rv">Mooie woorden zijn makkelijk…<br>Dit is wat het oplevert</h2>
      <div class="slider rv">
        <button class="slider-btn slider-prev" type="button" aria-label="Vorige">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 5 8 12 15 19"/></svg>
        </button>
        <div class="slider-track">
{slides}        </div>
        <button class="slider-btn slider-next" type="button" aria-label="Volgende">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 5 16 12 9 19"/></svg>
        </button>
      </div>
      <div class="results-more rv"><a href="/cases" class="btn btn-outline">Bekijk alle cases</a></div>
    </div>
  </section>
"""


STEPS = [
    ("Demogesprek", "(± 20 min)", "We laten je zien hoe het werkt, beantwoorden al je vragen en kijken samen wat jouw bedrijf nodig heeft. Geen verkooppraatjes, gewoon eerlijk advies."),
    ("Wij bouwen jouw systeem", "(± 5 werkdagen)", "Je vult een kort formulier in met je bedrijfsgegevens. Daarna gaan wij aan de slag met je website, chatbot, belsysteem en reviews."),
    ("Livegang", "(oplevergesprek)", "We lopen samen alles door en laten zien hoe het werkt. Daarna draait het vanzelf, en heb je vragen, dan spreek je gewoon een mens."),
]


def process(bg="bg-grey", anchor=""):
    steps = "".join(f"""        <div class="step rv">
          <div class="step-num">{i}</div>
          <h3>{t}<br>{d}</h3>
          <p>{p}</p>
        </div>
""" for i, (t, d, p) in enumerate(STEPS, 1))
    aid = f' id="{anchor}"' if anchor else ""
    return f"""  <section class="process sec {bg}"{aid}>
    <div class="wrap">
      <h2 class="h-section rv">Zo ziet samenwerken met ons eruit…</h2>
      <div class="steps">
        <svg class="steps-line" viewBox="0 0 800 100" preserveAspectRatio="none" aria-hidden="true"><path d="M10 43 C 120 100, 240 100, 390 43 S 660 -10, 790 43" fill="none" stroke="currentColor" stroke-width="4" stroke-dasharray="2 12" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>
{steps}      </div>
    </div>
  </section>
"""


def cta(bg="bg-white", title="Zullen we even kennismaken?",
        text="Plan een gratis demo in en ontdek hoe jouw website meer aanvragen kan opleveren. Vrijblijvend, in ongeveer 20 minuten."):
    return f"""  <section class="cta-wrap sec {bg}">
    <div class="wrap">
      <div class="cta-box rv">
        <div>
          <h2>{title}</h2>
          <p>{text}</p>
          <div class="cta-actions">
            <a href="/demo/" class="btn">Plan een demo</a>
            <a href="{WHATSAPP}" class="btn btn-outline-light">WhatsApp ons</a>
          </div>
        </div>
        <div class="cta-mascot"><img src="/mascot.svg" alt="" width="400" height="640" loading="lazy"></div>
      </div>
    </div>
  </section>
"""


def faq(items, bg="bg-grey", title="Veelgestelde vragen"):
    rows = ""
    for i, (q, a) in enumerate(items):
        rows += f"""        <details class="faq-item rv"{' open' if i == 0 else ''}>
          <summary>{q}{FAQ_CHEV}</summary>
          <div class="faq-a"><p>{a}</p></div>
        </details>
"""
    return f"""  <section class="faq sec {bg}">
    <div class="wrap">
      <h2 class="h-section rv">{title}</h2>
      <div class="faq-list">
{rows}      </div>
    </div>
  </section>
"""


def page_hero(title, sub="", bg="bg-grey", extra=""):
    s = f'\n      <p class="page-sub rv">{sub}</p>' if sub else ""
    return f"""  <section class="page-hero sec {bg}">
    <div class="wrap">
      <h1 class="h-page rv">{title}</h1>{s}{extra}
    </div>
  </section>
"""


def plan_badge(plan):
    return f'<a href="/prijzen" class="plan-pill">Inbegrepen vanaf <b>{plan}</b></a>'


def load_mockups():
    raw = (SRC / "mockups.html").read_text()
    out = {}
    for m in re.finditer(r"<!-- @(\w+) -->\n(.*?)(?=\n<!-- @|\Z)", raw, re.S):
        out[m.group(1)] = m.group(2).strip("\n")
    return out


MOCKS = load_mockups()


def wrap_page(title, desc, body, active=""):
    return head(title, desc) + nav(active) + "\n  <main>\n" + body + "  </main>\n\n" + footer() + "\n" + tail()


# ── Pages ─────────────────────────────────────────────────────────────────

def feature_page(f):
    facts = "".join(f'          <div class="fact rv"><b>{v}</b><span>{l}</span></div>\n' for v, l in f["facts"])
    cards = "".join(f"""        <div class="what-card rv">
          <h3><span class="what-ic">{icon(ICONS[ic], 26, 1.8)}</span>{t}</h3>
          <p>{p}</p>
        </div>
""" for ic, t, p in f["cards"])
    case_link = ""
    if f.get("case"):
        c = next(c for c in CASES if c["slug"] == f["case"].strip("/"))
        case_link = f"""      <div class="feat-case rv">
        <div class="feat-case-stat"><b>{c['stat']}</b><span>{c['stat_label']}</span></div>
        <div><p>“{c['quote']}”</p><a href="/{c['slug']}" class="slide-link">Lees de case van dit {c['who'].lower()} →</a></div>
      </div>
"""
    others = [o for o in FEATURES if o["slug"] != f["slug"]]
    rel = "".join(f'        <a href="/functies/{o["slug"]}" class="rel-item"><span class="dd-ic">{icon(ICONS[o["icon"]])}</span><span><b>{o["name"]}</b><small>{o["short"]}</small></span></a>\n' for o in others)

    body = f"""  <section class="feat-hero sec bg-grey">
    <div class="wrap">
      <h1 class="h-page rv">{f['title']}</h1>
      <p class="page-sub rv">{f['lead']}</p>
      <div class="feat-top">
        <div class="facts">
{facts}        </div>
        <div class="feat-show rv">
          <div class="feat-show-head">Zo ziet het eruit {plan_badge(f['plan'])}</div>
          <div class="feat-visual">
{MOCKS[f['mock']]}
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="what sec bg-navy">
    <div class="wrap">
      <h2 class="h-section rv">{f['what']}</h2>
      <div class="what-grid">
{cards}      </div>
{case_link}      <div class="what-cta rv"><a href="/demo/" class="btn">Plan een demo</a></div>
    </div>
  </section>

{cta('bg-white')}
{process('bg-grey')}
  <section class="related sec bg-white">
    <div class="wrap">
      <h2 class="h-section rv">Werkt nog beter samen met…</h2>
      <div class="rel-grid rv">
{rel}      </div>
    </div>
  </section>

{results('bg-grey')}"""
    return wrap_page(f"FLOWSA — {f['name']}", html.escape(html.unescape(f['lead']), quote=True), body, "functies")


def functies_page():
    cards = ""
    for f in FEATURES:
        cards += f"""        <a href="/functies/{f['slug']}" class="ov-card rv">
          <span class="ov-ic">{icon(ICONS[f['icon']], 28, 1.8)}</span>
          <h3>{f['name']}</h3>
          <p>{f['lead']}</p>
          <span class="ov-foot"><span class="plan-pill">Vanaf {f['plan']}</span><span class="slide-link">Meer info →</span></span>
        </a>
"""
    body = page_hero("Simpele systemen die gewoon werken",
                     "Alles wat je nodig hebt om van websitebezoeker naar betalende klant te gaan. Volledig automatisch, zonder dat jij er iets voor hoeft te doen.",
                     extra=f'\n      <div class="ov-grid">\n{cards}      </div>')
    body += cta("bg-white") + process("bg-grey") + results("bg-white")
    return wrap_page("FLOWSA — Functies", "Website, chatbot, belsysteem, Google Review-systeem, CRM-dashboard en meer: alle functies van FLOWSA voor aannemers.", body, "functies")


def prijzen_page():
    tiers = [
        ("Basic", "Ideaal voor startende aannemers", 60, 48, False,
         ["Professionele website", "Perfect op desktop &amp; mobiel", "Vindbaar in Google (SEO)", "Contactformulier &amp; chatwidget", "Automatisch meer Google reviews", "Persoonlijke ondersteuning"]),
        ("Plus", "Ideaal voor gevestigde aannemers", 120, 96, True,
         ["Alles uit Basic", "AI-chatbot die 24/7 vragen beantwoordt", "AI-belsysteem dat opneemt als jij niet kan", "Gemiste oproep? Binnen 60 sec. automatisch een sms terug", "Gespreksverslagen &amp; meldingen per e-mail", "Persoonlijke ondersteuning"]),
        ("Pro", "Ideaal voor groeiende aannemers", 250, 200, False,
         ["Alles uit Plus", "CRM-dashboard met al je leads op één plek", "Onbeperkt gebruikers, leads &amp; klanten", "Automatische opvolging via e-mail &amp; sms", "WhatsApp-koppeling", "Ondersteuning met voorrang"]),
    ]
    cards = ""
    for name, sub, m, y, hot, items in tiers:
        lis = "".join(f"<li>{CHECK}{i}</li>" for i in items)
        tag = '<span class="plan-tag">MEEST GEKOZEN</span>' if hot else ""
        btn = "btn" if hot else "btn btn-outline"
        cards += f"""        <div class="plan{' hot' if hot else ''} rv">
          {tag}<h3>{name}</h3>
          <div class="plan-for">{sub}</div>
          <div class="plan-price">€<span class="js-price" data-monthly="{m}" data-yearly="{y}">{y}</span> <small>/mnd</small></div>
          <div class="plan-note js-note" data-monthly="Maandelijks opzegbaar tarief" data-yearly="€{eur(y*12)} per jaar gefactureerd, je bespaart €{eur((m-y)*12)}">€{eur(y*12)} per jaar gefactureerd, je bespaart €{eur((m-y)*12)}</div>
          <ul>{lis}</ul>
          <a href="/demo/" class="{btn}">Begin met {name}</a>
        </div>
"""
    rows = [
        ("Website", 1, 1, 1), ("Geoptimaliseerd voor desktop &amp; mobiel", 1, 1, 1), ("Vindbaar in Google (SEO)", 1, 1, 1),
        ("Contactformulier", 1, 1, 1), ("Chatwidget", 1, 1, 1), ("Google Review-systeem", 1, 1, 1),
        ("AI-chatbot op jouw website", 0, 1, 1), ("AI-belsysteem", 0, 1, 1), ("Automatische sms bij gemiste oproep", 0, 1, 1),
        ("Gespreksverslagen &amp; meldingen per e-mail", 0, 1, 1), ("CRM-dashboard", 0, 0, 1), ("Onbeperkt gebruikers", 0, 0, 1),
        ("Automatische opvolging via e-mail &amp; sms", 0, 0, 1), ("WhatsApp-koppeling", 0, 0, 1),
        ("Ondersteuning", "Standaard", "Standaard", "Met voorrang"),
        ("Meta-advertenties", "Op aanvraag", "Op aanvraag", "Op aanvraag"), ("Google-advertenties", "Op aanvraag", "Op aanvraag", "Op aanvraag"),
    ]

    def cell(v):
        if v == 1:
            return f'<td class="yes">{CHECK}<span class="sr">Ja</span></td>'
        if v == 0:
            return '<td class="no">—<span class="sr">Nee</span></td>'
        return f"<td>{v}</td>"
    trs = "".join(f"<tr><th scope=\"row\">{r[0]}</th>{cell(r[1])}{cell(r[2])}{cell(r[3])}</tr>" for r in rows)

    incl = ""
    for f in FEATURES:
        incl += f"""          <details class="acc"><summary>{f['name']} <span class="plan-pill">vanaf {f['plan']}</span>{ACC_CHEV}</summary><div class="acc-a"><p>{f['lead']}</p><a href="/functies/{f['slug']}" class="slide-link">Meer over {f['name'].lower()} →</a></div></details>
"""
    extra_svc = [("Meta-advertenties", "Campagnes op Facebook en Instagram die gericht klanten in jouw regio bereiken."),
                 ("Google-advertenties", "Bovenaan in Google staan voor zoekopdrachten waar klanten nu al naar zoeken."),
                 ("Maatwerk", "Meer nodig dan in de pakketten zit? Neem contact op voor een offerte op maat.")]
    other = "".join(f'          <details class="acc"><summary>{t}{ACC_CHEV}</summary><div class="acc-a"><p>{d}</p><a href="/contact" class="slide-link">Vraag het aan →</a></div></details>\n' for t, d in extra_svc)

    toggle = """
      <div class="bill-toggle rv" role="group" aria-label="Betaalperiode">
        <button type="button" class="bill-opt" data-bill="monthly" aria-pressed="false">Maandelijks</button>
        <button type="button" class="bill-switch" aria-label="Wissel betaalperiode"><span></span></button>
        <button type="button" class="bill-opt is-on" data-bill="yearly" aria-pressed="true">Jaarlijks <em>bespaar 20%</em></button>
      </div>"""
    body = page_hero("Onze prijzen", "Transparante prijzen, geen verborgen kosten. Alle prijzen zijn exclusief btw.", extra=toggle + f"""
      <div class="plans plans-page">
{cards}      </div>
      <p class="guarantee rv">{icon(ICONS['shield'], 20)} 30 dagen niet goed, geld terug</p>""")
    body += f"""  <section class="incl sec bg-white">
    <div class="wrap">
      <div class="incl-grid">
        <div class="rv">
          <div class="incl-head">Wat zit erin?</div>
{incl}        </div>
        <div class="rv">
          <div class="incl-head">Andere diensten</div>
{other}        </div>
      </div>
      <h2 class="h-section rv" style="margin-top:96px;">Vergelijk alle functies</h2>
      <div class="cmp-wrap rv">
        <table class="cmp">
          <thead><tr><th scope="col">Functie</th><th scope="col">Basic</th><th scope="col" class="hot">Plus</th><th scope="col">Pro</th></tr></thead>
          <tbody>{trs}</tbody>
        </table>
      </div>
      <p class="cmp-note rv">Belminuten en sms vallen onder redelijk gebruik. Maatwerk nodig? <a href="/contact">Neem contact op</a> voor een offerte op maat.</p>
    </div>
  </section>
"""
    body += faq([FAQ_GENERAL[3], FAQ_GENERAL[4], FAQ_GENERAL[0], FAQ_GENERAL[1], FAQ_GENERAL[5]])
    body += cta("bg-grey") + process("bg-white") + results("bg-grey")
    return wrap_page("FLOWSA — Prijzen", "Transparante prijzen voor aannemers: Basic vanaf €48, Plus vanaf €96 en Pro vanaf €200 per maand. 30 dagen geld-terug-garantie.", body, "prijzen")


def cases_page():
    cards = ""
    for c in CASES:
        used = "".join(f'<span class="plan-pill">{FEAT[u]["name"]}</span>' for u in c["used"])
        cards += f"""        <a href="/{c['slug']}" class="case-card rv">
          <div class="case-card-stat"><b>{c['stat']}</b><span>{c['stat_label']}</span></div>
          <div class="case-card-body">
            <div class="case-who"><span class="case-av">{c['av']}</span><span><b>{c['who']}</b><small>{c['trade']}</small></span></div>
            <p>“{c['quote']}”</p>
            <div class="case-used">{used}</div>
            <span class="slide-link">Lees de volledige case →</span>
          </div>
        </a>
"""
    body = page_hero("Mooie woorden zijn makkelijk…<br>Dit is wat het oplevert",
                     "Resultaten van aannemers die met FLOWSA werken, in aanvragen, reactietijd en reviews. De bedrijfsnamen zijn geanonimiseerd.",
                     extra=f'\n      <div class="case-grid">\n{cards}      </div>')
    body += cta("bg-white") + process("bg-grey")
    return wrap_page("FLOWSA — Cases", "Resultaten van aannemers die met FLOWSA werken: meer aanvragen, snellere reacties en betere Google-reviews.", body, "cases")


def case_page(c):
    stats = "".join(f'<div class="fact"><b>{v}</b><span>{l}</span></div>' for v, l in c["stats"])
    used = "".join(f'<a href="/functies/{u}" class="rel-item"><span class="dd-ic">{icon(ICONS[FEAT[u]["icon"]])}</span><span><b>{FEAT[u]["name"]}</b><small>{FEAT[u]["short"]}</small></span></a>' for u in c["used"])
    appr = "".join(f"<p>{p}</p>" for p in c["approach"][:-1])
    body = f"""  <section class="page-hero sec bg-grey">
    <div class="wrap">
      <a href="/cases" class="back-link rv">← Alle cases</a>
      <div class="case-who case-who-lg rv"><span class="case-av">{c['av']}</span><span><b>{c['who']}</b><small>{c['trade']}</small></span></div>
      <h1 class="h-page rv">{c['title']}</h1>
      <p class="page-sub rv">{c['sub']}</p>
      <div class="case-stats rv">{stats}</div>
    </div>
  </section>

  <section class="article sec bg-white">
    <div class="wrap article-grid">
      <article class="article-body">
        <h2>De uitdaging</h2>
        <p>{c['challenge']}</p>
        <h2>De aanpak</h2>
        {appr}
        <blockquote>“{c['approach'][-1]}”</blockquote>
        <h2>Het resultaat</h2>
        <p>{c['result']}</p>
      </article>
      <aside class="article-side">
        <div class="side-card">
          <div class="incl-head">Gebruikte functies</div>
          {used}
        </div>
        <div class="side-card side-cta">
          <h3>Benieuwd wat dit voor jouw bedrijf kan doen?</h3>
          <a href="/demo/" class="btn">Plan een demo</a>
        </div>
      </aside>
    </div>
  </section>

{cta('bg-grey')}{results('bg-white')}"""
    return wrap_page(f"FLOWSA — Case: {html.unescape(c['trade'])}", html.escape(html.unescape(c['sub']), quote=True), body, "cases")


def werkwijze_page():
    zz = ""
    for i, (t, d, p) in enumerate(STEPS, 1):
        zz += f"""        <div class="zz-step{' zz-rev' if i % 2 == 0 else ''} rv">
          <div class="zz-num">{i}</div>
          <div class="zz-text"><h2>{t} <span>{d}</span></h2><p>{p}</p></div>
        </div>
"""
    need = [("file", "Je bedrijfsgegevens", "Naam, logo, werkgebied, diensten en contactgegevens."),
            ("star", "Foto's van je werk", "Een paar foto's van projecten waar je trots op bent. Niet professioneel? Geen probleem."),
            ("calendar", "Je agenda", "Wanneer je beschikbaar bent voor afspraken, zodat de chatbot direct kan inplannen."),
            ("phone", "Je telefoonnummer", "Voor het belsysteem en de sms bij gemiste oproepen.")]
    needs = "".join(f'        <div class="why-card rv">{icon(ICONS[ic], 40, 1.4)}<h3>{t}</h3><p>{p}</p></div>\n' for ic, t, p in need)
    body = f"""  <section class="page-hero sec bg-grey">
    <div class="wrap">
      <h1 class="h-page rv">Zo ziet samenwerken met ons eruit…</h1>
      <p class="page-sub rv">Drie stappen, geen gedoe. Gemiddeld staat alles binnen 5 werkdagen live.</p>
      <div class="zigzag">
        <svg class="zz-line" viewBox="0 0 1000 900" preserveAspectRatio="none" aria-hidden="true"><path d="M260 120 C 420 260, 640 260, 740 420 S 520 700, 260 760" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="14 14" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>
{zz}      </div>
    </div>
  </section>

  <section class="why sec bg-white">
    <div class="wrap">
      <h2 class="h-section rv">Wat we van je nodig hebben</h2>
      <p class="page-sub rv" style="margin-top:14px;">Na het demogesprek vul je een kort formulier in. Dit is alles wat we vragen:</p>
      <div class="why-grid why-grid-4">
{needs}      </div>
    </div>
  </section>

{cta('bg-grey')}{results('bg-white')}"""
    return wrap_page("FLOWSA — Werkwijze", "Zo werkt samenwerken met FLOWSA: demogesprek, wij bouwen je systeem in gemiddeld 5 werkdagen, en livegang.", body, "werkwijze")


def vakgebieden_page():
    tiles = "".join(f'        <div class="trade rv"><div class="trade-ic">{icon(d, 56, 1.5)}</div><h3>{n}</h3></div>\n' for n, d in TRADES_MAIN)
    lst = "".join(f'<li>{BADGE}{html.escape(t)}</li>' for t in TRADES_ALL)
    body = f"""  <section class="page-hero sec bg-grey">
    <div class="wrap">
      <h1 class="h-page rv">Voor al deze vakgebieden en meer…</h1>
      <p class="page-sub rv">Schilder, loodgieter, dakdekker of hovenier: als jij klanten wil, werkt het voor jou.</p>
      <div class="trades-grid trades-light">
{tiles}      </div>
    </div>
  </section>

  <section class="sec bg-white alltrades">
    <div class="wrap">
      <h2 class="h-section rv">Alle vakgebieden</h2>
      <ul class="trade-list rv">{lst}</ul>
      <p class="page-sub rv" style="margin-top:40px;">Staat jouw vakgebied er niet tussen? <a href="/contact">Vraag het ons</a>, grote kans dat we je kunnen helpen.</p>
    </div>
  </section>

{cta('bg-grey')}{process('bg-white')}{results('bg-grey')}"""
    return wrap_page("FLOWSA — Vakgebieden", "FLOWSA werkt voor schilders, loodgieters, dakdekkers, hoveniers, elektriciens, aannemers en elk ander vakgebied.", body, "over")


def contact_page():
    body = f"""  <section class="page-hero sec bg-grey">
    <div class="wrap">
      <h1 class="h-page rv">Neem contact op</h1>
      <p class="page-sub rv">Vul het formulier in en we nemen binnen 24 uur contact met je op, of app ons direct.</p>
      <div class="contact-grid">
        <form class="contact-card rv" id="contact-form" novalidate>
          <div class="f-row">
            <div class="f-field"><label for="cf-naam">Naam</label><input id="cf-naam" name="naam" type="text" placeholder="Jan de Vries" autocomplete="name" required></div>
            <div class="f-field"><label for="cf-bedrijf">Bedrijfsnaam</label><input id="cf-bedrijf" name="bedrijf" type="text" placeholder="De Vries Bouw" autocomplete="organization" required></div>
          </div>
          <div class="f-row">
            <div class="f-field"><label for="cf-tel">Telefoonnummer</label><input id="cf-tel" name="telefoon" type="tel" placeholder="+31 6 12345678" autocomplete="tel" required></div>
            <div class="f-field"><label for="cf-email">E-mailadres</label><input id="cf-email" name="email" type="email" placeholder="jan@devries.nl" autocomplete="email" required></div>
          </div>
          <div class="f-field"><label for="cf-bericht">Bericht</label><textarea id="cf-bericht" name="bericht" placeholder="Vertel ons wat je nodig hebt..." required></textarea></div>
          <button type="submit" class="btn">Verstuur bericht {ARROW}</button>
          <div class="f-success" id="contact-success" role="status" hidden>Bedankt! We nemen zo snel mogelijk contact met je op.</div>
        </form>
        <aside class="contact-side rv">
          <div class="side-card">
            <h3>Liever direct schakelen?</h3>
            <p>Stuur ons een berichtje via WhatsApp. We reageren zo snel mogelijk.</p>
            <a href="{WHATSAPP}" class="btn btn-wa">WhatsApp ons</a>
          </div>
          <div class="side-card">
            <h3>Meteen zien hoe het werkt?</h3>
            <p>Plan een gratis demo van ongeveer 20 minuten. Vrijblijvend.</p>
            <a href="/demo/" class="btn btn-outline">Plan een demo</a>
          </div>
          <img class="contact-mascot" src="/mascot.svg" alt="" width="400" height="640" loading="lazy">
        </aside>
      </div>
    </div>
  </section>
"""
    body += faq([FAQ_GENERAL[0], FAQ_GENERAL[1], FAQ_GENERAL[5]], bg="bg-white")
    return wrap_page("FLOWSA — Contact", "Neem contact op met FLOWSA. Vul het formulier in en we reageren binnen 24 uur, of app ons direct via WhatsApp.", body, "over")


def home_page():
    src = (SRC / "home.html").read_text()
    src = src.replace("{{RESULTS}}", results("bg-grey")).replace("{{PROCESS}}", process("bg-grey", "werkwijze"))
    body = src + "\n" + cta("bg-grey")
    return wrap_page("FLOWSA — Websites &amp; klantsystemen voor aannemers",
                     "FLOWSA bouwt websites en slimme klantsystemen voor aannemers: chatbot, belsysteem, Google Review-systeem en CRM-dashboard. Meer aanvragen, zonder extra personeel.",
                     body)


def main():
    pages = {"index.html": home_page(), "functies.html": functies_page(), "prijzen.html": prijzen_page(),
             "cases.html": cases_page(), "werkwijze.html": werkwijze_page(), "vakgebieden.html": vakgebieden_page(),
             "contact.html": contact_page()}
    for f in FEATURES:
        pages[f"functies/{f['slug']}.html"] = feature_page(f)
    for c in CASES:
        pages[f"{c['slug']}.html"] = case_page(c)
    for path, content in pages.items():
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)
    print(f"Built {len(pages)} pages:")
    for p in pages:
        print("  ", p)


if __name__ == "__main__":
    main()
