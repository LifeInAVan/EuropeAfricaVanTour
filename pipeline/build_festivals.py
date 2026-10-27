#!/usr/bin/env python3
"""festivals.json (data for the website) + festivals.md (doc tab), from the table below.
Status: on / near / missed. 'pass' = how the current itinerary (route.json, 25 Oct 2026 re-dating) meets it."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
CH = ["Baltic departure (19 – 25 Jul 2027)", "Heart of Europe (26 Jul – 7 Aug 2027)", "Dinaric wilds (8 – 23 Aug 2027)",
      "Adriatic and Ionian (24 Aug – 13 Sep 2027)", "Puglia to Rome (14 – 20 Sep 2027)", "Pyrenees, the Vuelta and Green Spain (21 Sep – 17 Oct 2027)",
      "Portugal (18 Oct – 23 Nov 2027)", "Morocco: Atlas, Sahara, winter and Toubkal (24 Nov 2027 – 12 Feb 2028)",
      "Al-Andalus and the Mediterranean (13 Feb – 25 Mar 2028)", "Provence (26 Mar – 9 Apr 2028)", "The Alps (10 – 18 Apr 2028)",
      "Rhine to the Oder (19 Apr – 10 May 2028)", "Poland's coast and lakes (11 – 28 May 2028)",
      "Baltic states and Laulupidu (29 May – 11 Jul 2028)", "Lapland and Arctic Norway (12 – 29 Jul 2028)", "Fjords and home (30 Jul – 22 Aug 2028)"]
# (chapter, event, place, usual timing, dates, status, pass, source name, url)
F = [
(1,"Jaanipäev and Victory Day","Pärnu, all Estonia","Fixed: 23–24 Jun","23–24 Jun","missed","About 4 weeks before we leave (19 Jul)","Visit Estonia","https://visitestonia.com/en/midsummers-eve-when-dusk-meets-dawn-jaanipaev"),
(1,"Līgo / Jāņi (midsummer)","Jūrmala, all Latvia","Fixed: night of 23–24 Jun","23–24 Jun","missed","About 4 weeks before we pass","Live Riga","https://www.liveriga.com/en/2711-ligo-and-summer-solstice-festival"),
(1,"Jewish Culture Festival","Kraków","Late Jun / early Jul, 5 days","Not announced (2026: 1–5 Jul)","missed","Kraków 23 Jul, about 3 weeks late","jewishfestival.pl","https://jewishfestival.pl/en/dates-of-the-35th-jcf-in-the-year-2026/"),
(2,"Východná folklore festival","Východná, Liptov, SK","First weekend of July","About 1–4 Jul (by rule)","missed","Východná 26 Jul, about 3 weeks late","Visit Liptov","https://www.visitliptov.sk/en/event/folklore-festival-vychodna-2026/"),
(2,"Pohoda","Trenčín, SK","Second weekend of July","**8–10 Jul (confirmed)**","missed","Before we leave; Trenčín 30 Jul","Pohoda","https://www.pohodafestival.sk/en/news/pohoda-in-london-we-re-starting-to-put-together-the-pohoda-2027-line-up"),
(2,"Valley of Arts","Kapolcs, HU","Late July, 10 days","**23 Jul – 1 Aug (confirmed)**","near","Balaton 4 Aug, 3 days late","programturizmus.hu","https://www.programturizmus.hu/ajanlat-muveszetek-volgye-fesztival-kapolcson.html"),
(2,"Ljubljana Festival","Ljubljana","Late Jun – early Sep","Not announced (2026: 21 Jun – 8 Sep)","on","Bled 6 Aug, 55 km","Ljubljana Festival","https://www.ljubljanafestival.si/en/press-releases/16251-summer-of-art-at-the-highest-level-the-74th-ljubljana-festival"),
(2,"Lights on the Lake","Bled","Penultimate Saturday of July","24 Jul (by rule)","missed","Bled 6 Aug, 13 days late","bled.si","https://www.bled.si/en/events/"),
(3,"Motovun Film Festival (Cinehill)","Motovun, HR","Late July, 6 days","Not announced (2026: 21–26 Jul, Gorski kotar)","missed","Motovun 10 Aug, about 2 weeks late","HAVC","https://havc.hr/eng/croatian-film/film-festivals-in-croatia/festival-list/cinehill-motovun-film-festival"),
(3,"Pula Film Festival","Pula Arena","Mid-July, 8 days","Not announced (2026: 9–16 Jul)","missed","About 4 weeks late","istra.hr","https://www.istra.hr/en/destinations/pula/events/22515"),
(3,"Old Bridge diving","Mostar","Last Sunday of July","25 Jul (by rule)","missed","Mostar 16 Aug, 3 weeks late","FENA","https://fena.ba/article/1636506/traditional-459th-old-bridge-diving-competition-to-be-held-on-sunday"),
(3,"Sinjska Alka (knights' tournament)","Sinj, HR","Early-August Sunday","Not announced (2026: 9 Aug)","near","Krka 14 Aug (Sinj 60 km), about 6 days late","Croatia Week","https://www.croatiaweek.com/milanovic-sinj-alka-311-preparations-2026/"),
(3,"Baščaršija Nights","Sarajevo","All July, free","Not announced (2026: 1–31 Jul)","missed","Sarajevo 17 Aug, after it ends","Visit Sarajevo","https://www.visitsarajevo.ba/event/bascarsija-nights-festival/"),
(3,"Sarajevo Film Festival","Sarajevo","Mid-August, 8 days","Not announced (2026: 14–21 Aug)","on","Sarajevo 17 Aug","SFF","https://www.sff.ba/en/news/12803/film-submissions-for-the-32nd-sarajevo-film-festival-programmes"),
(4,"Dubrovnik Summer Festival","Dubrovnik","10 Jul – 25 Aug","Not announced (same in 2026)","on","Dubrovnik 25 Aug, last night","Croatia Week","https://www.croatiaweek.com/77th-dubrovnik-summer-festival-opens-2026/"),
(4,"KotorArt","Kotor","13 Jul – mid-August","Not announced (2025: 13 Jul – 15 Aug)","missed","Kotor 26 Aug, 11 days after it ends","kotor.me programme","https://www.kotor.me/files/documents/1747984961-PROGRAM%20MANIFESTACIJA%20ZA%202025.%20GODINU.pdf"),
(4,"Summer Carnival","Kotor","Turn of Jul/Aug, 3 days","Not announced (2025: 31 Jul – 2 Aug)","missed","About 4 weeks late","kotor.me programme","https://www.kotor.me/files/documents/1747984961-PROGRAM%20MANIFESTACIJA%20ZA%202025.%20GODINU.pdf"),
(4,"Boka Night","Kotor","Late-August Saturday","Not announced (2025: 23 Aug)","near","Kotor 26 Aug: 2 days early if it is Sat 28 Aug","kotor.me programme","https://www.kotor.me/files/documents/1747984961-PROGRAM%20MANIFESTACIJA%20ZA%202025.%20GODINU.pdf"),
(4,"Assumption village feasts (panigiria)","Zagori villages, GR","Fixed: 15 Aug, 3 days","15 Aug","missed","Zagori 5–6 Sep, 3 weeks late","Zagori View","https://zagoriview.com/panegyria/"),
(5,"Notte della Taranta final concert","Melpignano, Salento","Fourth Saturday of August (2025, 2026)","28 Aug (by rule; not announced)","missed","We are in Greece","Sorrisi","https://www.sorrisi.com/tv/news-e-anticipazioni/la-notte-della-taranta-2026-in-diretta-su-rai-3-e-nel-circuito-eurovisione/"),
(5,"Byzantine New Year parade","Amalfi","31 Aug – 1 Sep","31 Aug – 1 Sep","missed","Amalfi 16 Sep","SiViaggia","https://siviaggia.it/notizie/capodanno-bizantino-amalfi/411801/"),
(5,"Festa del Redentore","Nuoro","Late August; pilgrimage 29 Aug","Not announced (2026: 22–29 Aug)","missed","Sardinia is no longer on the route","Blu Alghero","https://www.blualghero-sardinia.com/it/redentore-di-nuoro-programma/"),
(5,"Corsa degli Scalzi (barefoot race)","Cabras","Sat–Sun, late Aug / early Sep","Not announced (2026: 5–6 Sep)","missed","Sardinia is no longer on the route","Unione Sarda","https://www.unionesarda.it/en/sardinia/cabras-900-barefoot-runners-countdown-to-the-corsa-degli-scalzi-barefoot-race-sppyy1vb"),
(5,"Autunno in Barbagia (open village houses)","33 villages around Nuoro","Weekends, Sep – Dec","Not announced (2026: from 5 Sep)","missed","Sardinia is no longer on the route","Unione Sarda","https://www.unionesarda.it/en/sardinia/from-september-to-december-autumn-in-barbagia-stops-in-33-towns-rpxpdk90"),
(5,"Nostra Signora di Regnos Altos","Bosa","Mid-September weekend","Not announced (2025: 13–14 Sep)","missed","Sardinia is no longer on the route","Sardegna Turismo","https://www.sardegnaturismo.it/en/node/287011"),
(6,"Fiestas del Pilar","Zaragoza","Around 12 Oct, Saturday to Sunday, 9 days","About 9–17 Oct (by pattern; 2026: 10–18 Oct)","missed","Loarre 25 Sep, 2 weeks early","Soy de Zaragoza","https://soydezaragoza.es/fechas-de-las-fiestas-del-pilar/"),
(6,"Diada (Catalan National Day)","Barcelona","Fixed: 11 Sep","11 Sep","missed","We land at Barcelona 21 Sep and drive straight on","barcelona.cat","https://barcelona.cat/en/living-in-bcn/diada"),
(6,"La Vuelta a España","Santiago de Compostela to Madrid","2027 moved to September","**4–26 Sep (confirmed)**; stage towns due Dec 2026","on","Last week, 22–26 Sep, including the Madrid finish; stage towns to follow once the route is announced","Cyclingnews","https://www.cyclingnews.com/pro-cycling/racing/vuelta-a-espana-grand-depart-returns-to-home-soil-with-start-in-galicia-in-2027/"),
(6,"San Sebastián Film Festival","San Sebastián","Second half of September, opens on a Friday","About 17–25 Sep (by pattern)","near","San Sebastián 27 Sep, about 2 days late","SSIFF","https://www.sansebastianfestival.com/press/dates_and_forecasts/1/22440/in/t_22441"),
(6,"San Mateo grape harvest festival","Logroño","Week around 21 Sep","About 18–24 Sep (by pattern)","near","Logroño 29 Sep, about 5 days late","Nuevecuatrouno","https://nuevecuatrouno.com/2026/03/11/logrono-celia-sanz-logica-adelanto-cohete-fiestas-san-mateo/"),
(6,"Festa do Marisco (seafood)","O Grove","1–12 Oct","1–12 Oct (by pattern)","on","Combarro 12 Oct, last day (O Grove 15 km)","Festivales de España","https://www.festivalesdeespana.com/festival/festa-de-exaltacion-do-marisco-de-o-grove"),
(7,"Grape harvest","Douro valley","Late Aug – mid-Oct, set by the weather","Seasonal","near","Douro 18–21 Oct, around the end of harvest","e-konomista","https://www.e-konomista.pt/vindimas-no-douro/"),
(7,"October pilgrimage, candlelight procession","Fátima","Fixed: 12–13 Oct","12–13 Oct","near","Fátima 23 Oct, 10 days late","Africanews","https://www.africanews.com/amp/2025/10/13/thousands-gather-at-fatima-shrine-for-final-pilgrimage-of-the-year/"),
(7,"FOLIO literary festival","Óbidos","Early – mid-Oct, 11 days","About 7–17 Oct (by pattern)","near","Óbidos 27 Oct, about 10 days late","NiT","https://www.nit.pt/cultura/livros/folio-revela-as-datas-da-proxima-edicao-e-confirma-presenca-de-jon-fosse-e-leila-slimani"),
(7,"Big-wave surf contest","Nazaré","Window 1 Nov – 31 Mar, held when the swell comes","Not announced","near","Nazaré 26 Oct, 6 days before the window opens","The Inertia","https://www.theinertia.com/surf/nazare-big-wave-challenge-returns-winter-new-format/"),
(7,"National Horse Fair","Golegã","About 10 days around São Martinho","About 5–14 Nov (by pattern)","on","Golegã 10–12 Nov","Observador","https://observador.pt/2025/11/07/golega-investe-600-mil-euros-na-feira-do-cavalo-e-quer-torna-la-patrimonio-imaterial/"),
(7,"São Martinho (chestnuts, new wine)","All Portugal","Fixed: 11 Nov","11 Nov","on","11 Nov at the Golegã fair","Radical Storage","https://radicalstorage.com/travel/pt-pt/magusto-porto-sao-martinho/"),
(8,"International Film Festival","Marrakech","Late Nov – early Dec","About 19–27 Nov (by pattern)","missed","Not visiting Marrakech","ACC","https://acc.film/cannes100/2026/marrakech-international-film-festival.php"),
(8,"Date festival","Erfoud","Late Oct – early Nov","Not announced (2025: 29 Oct – 2 Nov)","missed","","Infomédiaire","https://www.infomediaire.net/?p=184020"),
(8,"Taragalte nomad music festival","M'Hamid El Ghizlane","Late Oct / Nov","Not announced (2024: 1–3 Nov)","missed","","L'ODJ","https://lodj.ma/file/242092"),
(8,"Saffron Festival","Taliouine","November","Not announced (2025: 20–23 Nov)","missed","Taliouine 15 Dec","TelQuel","https://telquel.ma/instant-t/2025/11/17/taliouine-accueille-le-16e-festival-international-du-safran_1961256/"),
(8,"Jazz sous l'Arganier","Essaouira","Late December","Not announced (2025: 27–29 Dec)","on","Trip from the Tiznit base (from 19 Dec)","AllAfrica","https://fr.allafrica.com/stories/202512250130.html"),
(8,"Amazigh New Year (Yennayer)","Tiznit, Agadir","About 13–14 Jan","14 Jan 2028 (holiday)","on","Tiznit base","Hespress","https://fr.hespress.com/404879-404879.html"),
(8,"Camel market","Guelmim","Every Saturday","Weekly","on","Saturday trip from Tiznit","Médias24","https://medias24.com/2023/12/18/guelmim-les-portes-ouvertes-vers-la-magie-du-desert/"),
(8,"Tan-Tan Moussem","Tan-Tan","Moves between years","Not announced (2026: 30 Oct – 3 Nov)","missed","","Le Matin","https://lematin.ma/culture/moussem-de-tan-tan-la-19e-edition-se-tiendra-du-30-octobre-au-3-novembre/366795"),
(8,"Almond Festival","Tafraout","Feb – Apr, with the blossom; Ramadan may move it","Not announced (2026: 9–12 Apr)","missed","Probably; the blossom itself (late Jan – Feb) is on route","AllAfrica","https://fr.allafrica.com/stories/202604080673.html"),
(9,"Almond blossom","Axarquía and Montes de Málaga","Peak late Jan – early Feb","Weather-dependent","missed","Peak missed by about 3 weeks","El Debate","https://www.eldebate.com/espana/andalucia/malaga/20260301/campo-malagueno-viste-gala-ruta-floracion-almendro-ocho-pueblos-provincia_389703.html"),
(9,"Carnival","Cádiz","Thursday before Ash Wednesday, 11 days","About 24 Feb – 5 Mar (by rule)","on","24–26 Feb, opening days","Festivales de España","https://www.festivalesdeespana.com/festival/carnaval-de-cadiz"),
(9,"Festival de Jerez (flamenco)","Jerez de la Frontera","Late Feb – early Mar, 2 weeks","Not announced (2027: 19 Feb – 6 Mar)","on","From Cádiz 24–26 Feb, 35 km","Vida Flamenca","https://vidaflamenca.org/31a-festival-de-jerez-2027-programa-de-cursos-y-talleres-las-inscripciones-se-abriran-14-de-septiembre/"),
(9,"Fallas","Valencia","Fixed: fireworks daily 1–19 Mar, main days 15–19 Mar","1–19 Mar","on","15–19 Mar, main days and the Cremà","Visit Valencia","https://www.visitvalencia.com/agenda-valencia/mascletas-de-las-fallas"),
(9,"Fiestas de la Magdalena","Castellón","Saturday before the 3rd Sunday of Lent, 9 days","About 18–26 Mar (by rule)","on","Castellón 20 Mar","iCalendario","https://icalendario.net/fiestas-religiosas/catolicas-locales/fiestas-de-la-magdalena"),
(10,"Gitan pilgrimage to Sainte Sara","Saintes-Maries-de-la-Mer","Fixed: 24–25 May","24–25 May","missed","About 2 months","Festival en France","https://festivalenfrance.com/festival/pelerinage-des-gitans-aux-saintes-maries-de-la-mer"),
(10,"Easter Feria","Arles","Easter weekend, 4 days","About 14–17 Apr (Easter 16 Apr)","missed","Arles 27 Mar","Provence tourism","https://provence-alpes-cotedazur.com/que-faire/sortir/toutes-les-sorties/la-feria-de-paques-arles-fr-4565560/"),
(11,"Fête de la Tulipe","Morges, Lake Geneva","Late Mar – mid-May","Not announced (2027: 23 Mar – 9 May)","on","Lavaux 12 Apr","Morges Tourisme","https://www.morges-tourisme.ch/en/P91876"),
(11,"Sechseläuten (burning the Böögg)","Zürich","Usually 3rd Monday of April","**24 Apr parade (confirmed)**, from 21 Apr","near","Rhine Falls 16 Apr, 8 days early","La Télé","https://latele.ch/articles/neuchatel-et-le-jura-hotes-d-honneur-du-sechselaeuten-en-2028"),
(12,"Easter and spring markets","Colmar","Before Easter to 3 weeks after","About late Mar – 7 May (by pattern)","on","Colmar 17 Apr","info.fr","https://info.fr/colmar-fete-printemps-marches-paques-animations-2026/"),
(12,"Heidelberger Frühling (classical music)","Heidelberg","Mid-Mar – mid-Apr","Not announced","near","Heidelberg 25 Apr, about 10 days late","Festival report","https://www.heidelberger-fruehling.de/wp-content/uploads/2026/04/26-04-19_PI_Bilanz_Heidelberger_Fruehling_Musikfestival_2026_.pdf"),
(12,"Easter fountains (Osterbrunnen)","Fränkische Schweiz, east of Bamberg","Holy Week to 2 weeks after Easter","To about 30 Apr","on","Bamberg 28 Apr","Pegnitz flyer","https://www.pegnitz.de/_Resources/Persistent/c/5/4/6/c546402e5437469f817fb36f66d9a2b92acd2cd2/Osterbrunnen_Flyer_2026.pdf"),
(12,"Walpurgis Night","Harz: Thale, Schierke, Wernigerode","Fixed: 30 Apr","30 Apr","near","Same night, but we are in Erfurt, 150 km away","Volksstimme","https://www.volksstimme.de/lokal/wernigerode/walpurgis-2026-harz-schierke-thale-hexentanzplatz-wernigerode-quedlinburg-programm-anreise-tickets-parken-3595569"),
(12,"Walpurgis Night and maypole","Erfurt, Domplatz","29–30 Apr","29–30 Apr (by pattern)","on","Erfurt 30 Apr","Festivals in Deutschland","https://www.festivalsindeutschland.de/festival/walpurgisnacht-domplatz-erfurt"),
(12,"Rhein in Flammen (fireworks)","Bonn, Bingen, Koblenz, Oberwesel, St Goar","Five Saturdays, May – Sep","Not announced","missed","","Wikipedia","https://en.wikipedia.org/wiki/Rhein_in_Flammen"),
(12,"Baumblütenfest (blossom festival)","Werder (Havel), by Potsdam","Late Apr – early May","Not announced (2026: 25 Apr – 3 May)","near","Potsdam 9 May, about 6 days late","Festivals in Deutschland","https://www.festivalsindeutschland.de/festival/baumbluetenfest-werder-havel"),
(12,"International Dixieland Festival","Dresden","Pentecost week","Pentecost is 4 Jun","missed","","Festival","https://www.dixielandfestival-dresden.com/en/program.html"),
(13,"Resort Days (season opening)","Sopot","End-of-May weekend","Not announced (2026: 30–31 May)","missed","Sopot 16 May, about 12 days early","Visit Sopot","https://visit.sopot.pl/en/news/see-you-at-the-resort-days-in-sopot-32120076"),
(14,"Estonian Song and Dance Festival (Laulupidu)","Tallinn","Every 5 years; 2028 is the first joint edition (dance, then song)","**30 Jun – 9 Jul (confirmed)**","on","Home 25 Jun – 11 Jul","ERR","https://news.err.ee/1609548682/youth-festivals-to-be-merged-with-estonia-s-song-and-dance-festival-in-2028"),
(14,"Jaanipäev and Victory Day","All Estonia","Fixed: 23–24 Jun","23–24 Jun","on","Viljandi and Soomaa","Wikipedia","https://en.wikipedia.org/wiki/Jaanip%C3%A4ev"),
(14,"Līgo / Jāņi","All Latvia","Fixed: night of 23–24 Jun","23–24 Jun","missed","We are in Estonia","Latvia Travel","https://www.latvia.travel/en/summer-solstice-celebrations"),
(14,"Hanseatic Days","Pärnu","First weekend of July","Not announced (2026: 3–5 Jul)","on","Home","Baltic Guide","https://balticguide.ee/en/?p=159667"),
(14,"Pärnu Music Festival (Järvi)","Pärnu","Mid-July","Not announced (2026: 8–18 Jul)","on","Partly; we leave 11 Jul","paavojarvi.com","https://paavojarvi.com/parnu-music-festival-2026-8-18-july/"),
(14,"Tallinn Maritime Days","Tallinn","Now mid-July (was late August)","Not announced (2025: 11–13 Jul)","on","Probably; Tallinn 11–12 Jul for the Helsinki ferry","Visit Estonia","https://visitestonia.com/en/tallinn-maritime-days"),
(14,"Old Town Days","Tallinn","Early June","Not announced (2026: 5–7 Jun)","missed","","Baltic Guide","https://balticguide.ee/en/tallinns-old-town-days-start-next-week/?l"),
(14,"Street Music Day","Vilnius","Mid-May Saturday","Not announced","missed","About 2 weeks","LRT","https://www.lrt.lt/en/news-in-english/19/2554154/summer-festivals-in-vilnius-key-dates"),
(14,"Days of Live Archaeology","Kernavė","Early July","Not announced (2026: 4–6 Jul)","missed","","bilietai.lt","https://www.bilietai.lt/en/series/IAPNXONZS7/gyvosios-archeologijos-dienos-kernaveje-xxvi"),
(14,"Seto Kingdom Day","Setomaa","Early-August Saturday","Not announced","missed","","Baltic Guide","https://balticguide.ee/en/setomaas-summer-is-full-of-events/"),
(14,"Folk Music Festival","Viljandi","Late July, Thu–Sun","Not announced","missed","","Visit Estonia","https://www.visitestonia.com/en/viljandi-folk-music-festival"),
(15,"Riddu Riđđu (Sámi and indigenous peoples)","Manndalen, NO","Early – mid-July","Not announced (2026: 8–12 Jul)","near","Lyngen 21 Jul, about 10 days late","riddu.no","https://riddu.no/en/nyheter/ministry-culture-opening-riddu-riddu-2026"),
(15,"Ijahis Idja (Sámi music)","Inari, FI","Mid-August","Not announced (2026: 14–15 Aug)","missed","","Lapland North","https://laplandnorth.fi/en/events/ijahis-idja/"),
(16,"Olavsfestdagene","Trondheim","Week around 29 Jul","Not announced (2026: 28 Jul – 3 Aug)","on","Trondheim 3 Aug, probably the last day","Life in Norway","https://www.lifeinnorway.net/major-events-in-trondheim"),
(16,"Trøndelag Food Festival","Trondheim","Straight after Olavsfest","Not announced (2026: 6–8 Aug)","near","3 days early","Life in Norway","https://www.lifeinnorway.net/major-events-in-trondheim"),
(16,"Moldejazz","Molde","Week 29","About 10–16 Jul","missed","About 2.5 weeks","Fjord Norway","https://www.fjordnorway.com/en/events/moldejazz"),
(16,"Øya Festival","Oslo","Mid-August (week 33 in 2026)","Not announced; week 33 would be 16–19 Aug","near","Oslo 16 Aug: on route if 2028 is week 33, else 1 day late","GIITTV","https://www.godisinthetvzine.co.uk/2026/05/19/news-oslos-oya-festival-announces-final-artists-for-2026-line-up/"),
(16,"Kulturfestivalen (free)","Stockholm","Mid-August, 5 days (week 33 in 2026)","Not announced; week 33 would be 16–20 Aug","near","Stockholm 18 Aug: on route if 2028 is week 33, else 2 days late","TT","https://via.tt.se/pressmeddelande/4486528/en-vecka-kvar-till-kulturfestivalen?lang=sv"),
(1,"Summer Jazz Festival","Kraków","Late Jun – end Aug, about 150 concerts","Not announced (2026: 27 Jun – 31 Aug)","on","Kraków 23 Jul","Visit Kraków","https://visitkrakow.com/summer-jazz-festival-krakow-guide/"),
(1,"Warsaw Uprising anniversary (sirens at 17:00)","Warsaw","Fixed: 1 Aug","1 Aug","missed","Warsaw 20 Jul, 12 days early","Wprost","https://www.wprost.pl/12403947"),
(2,"Summer craft days","Vlkolínec","Early Jul – end Aug, daily","Not announced (2026: 4 Jul – 30 Aug)","on","Vlkolínec 27 Jul (small)","Visit Liptov","https://www.visitliptov.sk/en/?p=722165"),
(2,"Jánošíkove dni (international folklore festival)","Terchová, between Orava and Žilina","Wed–Sun, late Jul / early Aug","About 28 Jul – 1 Aug (2026: 29 Jul – 2 Aug)","on","29 Jul, free day between Orava and Trenčín","TASR","https://www.teraz.sk/regiony/v-stredu-sa-zacina-64-rocnik-folkl/981310-clanok.html"),
(2,"Podroháčske folk festival","Zuberec, Orava","Early August, 5 days","About 4–8 Aug (2026: 5–9 Aug)","near","Orava 28 Jul, about 7 days early","TASR","https://www.teraz.sk/regiony/podrohacske-folklorne-slavnosti-osl/982879-clanok.html"),
(2,"Okarina world music festival","Bled","Late Jul – first week of Aug","Last confirmed 2019 (23 Jul – 3 Aug)","near","Bled 6 Aug, about 3 days late; may no longer run","RTV Slovenija","https://www.rtvslo.si/kultura/glasba/s-festivalom-okarina-znova-zvoki-etna-in-dzeza-na-bledu/495185"),
(2,"Sziget","Budapest","Mid-August","**10–14 Aug (confirmed)**","near","Balaton 4–5 Aug, 5 days early; 130 km off route","festivalinfo.nl","https://www.festivalinfo.nl/news/59200/Sziget-maakt-datum-locatie-en-ticketverkoop-bekend-voor-2027-en-blikt-terug-op-2026/"),
(2,"St Stephen's Day (fireworks, folk arts fair)","Budapest","Fixed: 20 Aug","20 Aug","missed","15 days after Balaton","Xpatloop","https://xpatloop.com/channels/2026/08/budapests-august-20-celebrations-will-feature-fireworks-free-programmes.html"),
(3,"Bridge diving into the Soča","Kanal ob Soči","A Sunday in mid-August (2nd Sunday in 2018, 2019, 2024)","About 8 Aug (by pattern)","on","Soča 8 Aug, if the pattern holds","Slovenia Times","https://sloveniatimes.com/event/270/spectacular-dives-from-kanal-bridge"),
(3,"Velika Gospa (Assumption)","Croatian shrines; Međugorje and Ljubuški in Herzegovina","Fixed: 15 Aug","15 Aug","on","Kravica 15 Aug: crowds and closures","Croatia Week","https://www.croatiaweek.com/velika-gospa-croatia-pilgrims-marian-shrines/"),
(3,"Bridge diving at the Mehmed Paša Sokolović bridge","Višegrad","A Saturday in late August","About 21 or 28 Aug (2025: 23 Aug)","near","Višegrad 19 Aug, 2 or 9 days early","SeeSrpska","https://seesrpska.com/en/zivot/sta-donosi-avgust-u-visegradu-10-8-2025"),
(4,"Herceg Novi Film Festival (open air)","Herceg Novi","Late August (2026); earlier years early August","Not announced (2026: 22–28 Aug)","on","25 Aug between Dubrovnik and Perast, if the late-August slot stays","Cineuropa","https://cineuropa.org/en/newsdetail/494367"),
(4,"Budva Theatre City","Budva","1 Jul – about 23 Aug","Not announced (2025: 1 Jul – 23 Aug)","near","Sveti Stefan 27 Aug, about 4 days late","Festival Finder","https://www.festivalfinder.eu/festivals/xxxix-festival-theatre-city"),
(4,"Shkodra Jazz Festival","Shkodër","Mid-August to about 1 Sep","Not announced (2024: 12 Aug – 1 Sep; 2025 to 31 Aug)","on","Shkodra 29 Aug, likely","Shqiptarja","https://shqiptarja.com/lajm/aktivitetet-kulturore-vijon-edicioni-i-16te-i-festivalit-te-xhazit-ne-shkoder-microfolie-tirana-muze-digjital-te-parku-europa"),
(4,"Sari Salltik pilgrimage","Krujë mountain","14 Aug – 14 Sep (one source)","Unverified","on","Krujë 31 Aug, unverified","Sara Kuehn","https://www.sarakuehn.com/kruja-pilgrimage-albania"),
(4,"Mount Tomorr Bektashi pilgrimage","Mount Tomorr, above Berat","20–25 Aug","About 20–25 Aug (2026: 18–25 Aug)","near","Berat 1 Sep, 7 days after it ends","BalkanWeb","https://www.balkanweb.com/nis-pelegrinazhi-7-ditor-ne-malin-e-tomorrit-pritet-te-marrin-pjese-rreth-600-mije-pelegrine-policia-vendos-kufizime-ne-qarkullim/"),
(4,"National Folklore Festival","Gjirokastër castle","Every 5–8 years","Last 2023; next expected 2028","missed","No 2027 edition","Albania Visit","https://albaniavisit.com/gjirokaster-folklore-festival/"),
(4,"Nativity of the Virgin village feasts (panigyria)","Makrino and Vradeto, Zagori","Fixed: 8 Sep, dancing on the evening of the 7th","8 Sep","on","Zagori 6–8 Sep","Music of our Desire","https://www.musicofourdesire.com/el/blog/panigyria-ioanninon"),
(5,"Fiera del Levante","Bari","9 days in mid-September","Not announced (2025: 13–21 Sep; 2026: 19–27 Sep)","on","Bari 14 Sep, probably; 4 days early if it starts on the 18th","nTradeshows","https://www.ntradeshows.com/campionaria-generale-internazionale-fiera-del-levante/"),
(5,"San Gennaro feast and blood 'miracle'","Naples cathedral","Fixed: 19 Sep","19 Sep (Sunday)","near","Pompeii 17 Sep, 2 days early","Napolike","https://www.napolike.it/festa-san-gennaro-2026-programma"),
(5,"Romaeuropa Festival (theatre, dance, music)","Rome","September – mid-November","About Sep – Nov (2026: 8 Sep – 15 Nov)","on","Rome 18–19 Sep","Turismo Roma","https://www.turismoroma.it/en/events/romaeuropa-festival-ref2026"),
(5,"Palio della Tonna (donkey race)","Civita di Bagnoregio","1st Sunday of June and 2nd Sunday of September","About 12 Sep","near","Civita 20 Sep, 8 days late","Eventi e Sagre","https://www.eventiesagre.it/Eventi_Storici/8250_Palio+della+Tonna.html"),
(5,"Festa del Pesce","Positano","Last Saturday of September","About 25 Sep","near","Amalfi coast 16 Sep, 9 days early","Napolike","https://www.napolike.it/festa-pesce-2026-positano"),
(5,"Sagra dell'Uva (grape festival)","Marino, near Rome","First weekend of October","About 2–3 Oct","missed","Rome 18–19 Sep, 2 weeks early","Voloscontato","https://www.voloscontato.it/sagre-ed-eventi/centenario-sagra-delluva-di-marino-2026-dove-quando-e-info.php"),
(6,"La Mercè (city festival)","Barcelona","4–5 days around 24 Sep","About 23–26 Sep (2026: 23–27 Sep)","near","We land 21 Sep, 2 days early","idealista","https://www.idealista.com/en/news/lifestyle-in-spain/2026/09/18/913352-merce-festival-2026-dates-programme-and-concert-highlights"),
(6,"San Froilán (fair, octopus, music)","Lugo","4–12 Oct","4–12 Oct (by pattern)","on","Lugo 9 Oct","Festivales de España","https://www.festivalesdeespana.com/festival/san-froilan-lugo"),
(6,"Festival de la Manzana (cider)","Villaviciosa, Asturias","Odd years, early October","About 8–12 Oct (2025: 9–13 Oct)","on","Villaviciosa 8 Oct; held in odd years only","Asturias.com","https://asturias.com/festival-de-la-manzana/"),
(6,"Picos de Europa cheese contest","Cangas de Onís","About 12 Oct","About 12 Oct","near","Covadonga 7 Oct, 5 days early","Festivales de España","https://www.festivalesdeespana.com/festival/concurso-exposicion-quesos-picos-europa-cangas-de-onis"),
(6,"Xacobeo Holy Year (Holy Door open)","Santiago de Compostela","Years when 25 Jul is a Sunday","**All of 2027 (confirmed)**","on","Santiago 10 Oct; expect crowds","Correos","https://www.elcaminoconcorreos.com/es/xacobeo-2027"),
(7,"Weekly market","Barcelos, 20 min from Braga","Every Thursday","Weekly","on","Thu 14 Oct","Vagamundos","https://www.vagamundos.pt/visitar-barcelos-num-dia/"),
(7,"National Gastronomy Festival","Santarém","About 10 days in late October","About late Oct (2026: 22 Oct – 1 Nov)","on","Detour of about 1 h from Fátima or Batalha, 23–26 Oct","Sábado","https://www.sabado.pt/comunicados-imprensa/detalhe/festival-nacional-de-gastronomia-recupera-sabores-e-tradicoes-de-antigamente-e-celebra-45-anos"),
(7,"Feira dos Santos","Chaves","About 30 Oct – 1 Nov","About 29 Oct – 1 Nov (2024: 30 Oct – 3 Nov)","missed","We are 400 km south","Termas de Chaves","https://termasdechaves.com/en/news/termas-de-chaves-with-exclusive-discounts-during-feira-dos-santos"),
(7,"All Saints and Pão-por-Deus","All Portugal","Fixed: 1 Nov","1 Nov (Monday)","on","Lisbon area; public holiday, expect closures","RFM","https://rfm.pt/content/3600/o-que-e-o-pao-por-deus-no-dia-de-todos-os-santos"),
(7,"Feira da Ladra (flea market)","Lisbon","Every Tuesday and Saturday","Weekly","on","Tue 2 Nov","Visit Lisboa","https://www.visitlisboa.com/pt-pt/locais/feira-da-ladra"),
(7,"LEFFEST (film festival)","Lisbon and Estoril","Early – mid-November","About 5–14 Nov (2026: 6–15 Nov)","near","We leave Lisbon 3 Nov, 2 days early","Time Out","https://www.timeout.pt/lisboa/pt/filmes/leffest"),
(7,"European Capital of Culture","Évora","All of 2027","**2027 (confirmed)**; programme due late 2026","on","Évora 5 Nov","RTP","https://www.rtp.pt/noticias/cultura/programacao-de-evora-2027-arranca-em-fevereiro-desse-ano-e-sera-anunciada-no-fim-de-2026_n1665360"),
(7,"Festa do Castanheiro (chestnut fair)","Marvão","Weekend after São Martinho","About 13–14 Nov (2026: 14–15 Nov)","on","Marvão 13 Nov","Marvão agenda 2026","https://www.cm-marvao.pt/wp-content/uploads/2026/01/Agenda-Cultural-Marvao-2026.pdf"),
(7,"Convent sweets and liqueurs fair","Alcobaça monastery","Thu–Sun, mid to late November","About 18–21 Nov (2026: 19–22 Nov)","on","Alcobaça 18 Nov","Viral Agenda","https://www.viralagenda.com/pt/events/1828888/28-mostra-internacional-de-doces-licores-conventuais"),
(7,"Guimarães Jazz","Guimarães","Mid-November","About 11–20 Nov (2026: 12–21 Nov)","near","Spare days 16–17 Nov, but 3 h north","CCVF","https://www.ccvf.pt/en/detail-eventos/20261112-guimaraes-jazz-2026-geral/"),
(7,"Sweet Potato Festival","Aljezur, 30 km from Lagos","Fri–Sun, late November","About 26–28 Nov (2025: 28–30 Nov)","near","Algarve 20–22 Nov, about 4 days early","Postal","https://postal.pt/vida-lazer/gastronomia/aljezur-transforma-se-na-capital-da-batata-doce-com-tres-dias-de-festa-sabores-e-tradicao/"),
(7,"Festa dos Tabuleiros (every 4 years)","Tomar","July","**July 2027 (confirmed)**; days not set","missed","Before we leave","Notícias ao Minuto","https://www.noticiasaominuto.com/pais/2975363/populacao-de-tomar-vota-pela-realizacao-da-festa-dos-tabuleiros-em-2027"),
(8,"Zamane desert music festival","M'Hamid El Ghizlane, 95 km south of Zagora","Late Nov or early Dec, varies","Not announced (2025: 14–16 Nov; 2026: 3–6 Dec)","on","Zagora 4 Dec, if early December","le360","https://fr.le360.ma/culture/zamane-a-mhamid-el-ghizlane-le-festival-qui-fait-battre-le-coeur-musical-du-desert_OE72SEJM3VGPXJBWD62Z32MTM4/"),
(8,"Cinéma et Migrations festival (beach screenings)","Agadir","November or December, varies","Not announced (2025: 8–13 Dec)","near","Agadir 16 Dec, about 3 days late if like 2025","Le Matin","https://lematin.ma/culture/festival-cinema-et-migrations-la-21e-edition-du-8-au-13-decembre/316127"),
(8,"Visa For Music","Rabat","Mid to late November","About 17–20 Nov (2026: 18–21 Nov)","near","Before we arrive; Rabat not on the way out","Hespress","https://fr.hespress.com/492398-visa-for-music-2026-rabat-devoile-la-programmation-de-sa-13e-edition.html"),
(8,"Weekly souks","Tiznit (Thu), Tafraoute (Wed), Sidi Ifni (Sun), Zagora (Wed, Sun), Rissani (Sun, Tue, Thu), Taroudant (Sun), Asni (Sat)","Weekly","Weekly","on","Tiznit, Tafraoute and Sidi Ifni from the base; Asni Sat 12 Feb; Zagora Sun 5 Dec; Rissani Tue 7 Dec; Taroudant a day off","Away with the Steiners","https://awaywiththesteiners.com/things-to-do-in-tiznit-morocco/"),
(8,"Yennayer programme (concerts, crafts)","Agadir","11–14 Jan","About 11–14 Jan","on","1.5 h from the Tiznit base","maroc.ma","https://www.maroc.ma/fr/actualites/agadir-un-riche-programme-pour-la-celebration-du-nouvel-amazigh-2976"),
(8,"Africa Eco Race (Tangier–Dakar rally)","Assa, Khenifiss, Guelmim area","Late January","2028 not announced; 2027 starts in Tangier 24 Jan","on","Southern stages about 25–29 Jan, from the Tiznit base","Morocco World News","https://www.moroccoworldnews.com/2026/10/343203/tangier-to-launch-2027-africa-eco-race-across-three-countries/"),
(8,"1-54 African art fair","Marrakech","Late Jan or early Feb","Not announced (2026: 5–8 Feb); Ramadan may move it","near","Imlil 9 Feb, about 1 day; 1.5 h from Marrakech","TelQuel","https://telquel.ma/instant-t/2026/01/15/marrakech-la-foire-dart-contemporain-africain-1-54-revient-du-5-au-8-fevrier_1970418/"),
(8,"Pro Taghazout Bay (surf contest)","Taghazout","Late Feb or March, set around Ramadan","Not announced (2026: 22–29 Mar)","missed","Probably March, after we leave","Hespress","https://fr.hespress.com/462699-le-pro-taghazout-bay-accueillera-lelite-du-surf-europeen-et-africain-en-mars-2026.html"),
(8,"Mawlid, and the summer moussems (Moulay Idriss, Sidi Hmad Ou Moussa)","Nationwide; Moulay Idriss; Tazeroualt","August – September","About 15 Aug 2027 (Mawlid)","missed","All in summer","timeanddate","https://www.timeanddate.com/holidays/morocco/prophet-birthday"),
]
LBL = {"on": "**On route**", "near": "Near miss", "missed": "Missed"}
# Phase 6: each festival's date rule (festival_rules.py) and map position (fetch_festival_places.py), so the
# website can work out the dates for any start date. "status" and "our_pass" are the old hand-written results.
from festival_rules import R
_pos = json.load(open(os.path.join(HERE, "cache", "festival_places.json"), encoding="utf-8"))
def where(place):
    if place.startswith("country:"): return dict(country=place[8:])
    out = []
    for q in place.split(" / "):
        q, _, days = q.partition("@")
        lat, lon = _pos[q.strip()]
        out.append(dict(lat=lat, lon=lon, **(dict(days=days.strip()) if days else {})))
    return dict(places=out)
json.dump([dict(chapter=c, event=e, place=p, timing=t, dates=d, status=s, our_pass=ps, source=sn, url=u,
                rule=R[(c, e)][0], **where(R[(c, e)][1]))
           for c, e, p, t, d, s, ps, sn, u in F], open(os.path.join(ROOT, "data", "festivals.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
n = {k: sum(1 for f in F if f[5] == k) for k in LBL}
md = ["# Festivals on or near the route", "",
      f"{len(F)} events, grouped by the 16 recommended chapters, checked against the itinerary leaving Pärnu on 19 Jul 2027: "
      f"**{n['on']} on route**, {n['near']} near misses (within 10 days), {n['missed']} missed. "
      "Most 2027–28 dates are not announced yet: \"by rule\" or \"by pattern\" means worked out from previous years.", ""]
for i, name in enumerate(CH, 1):
    md += [f"## {i}. {name}", "", "| Event | Place | Usual timing | Dates | Our pass | Source |", "|---|---|---|---|---|---|"]
    for c, e, p, t, d, s, ps, sn, u in F:
        if c == i:
            md.append(f"| {e} | {p} | {t} | {d} | {LBL[s]}{': ' + ps if ps else ''} | [{sn}]({u}) |")
    md.append("")
md += ["## Checked and left out (outside our dates or no dates found)", "",
 "- Morocco: Kelaat M'Gouna rose festival (May), Imilchil marriage festival (September), Fès Sufi Culture Festival (17–24 Oct 2026).",
 "- Balkans: Bled Days (no official dates).",
 "- Italy and Iberia: Stintino regatta (timing unclear).",
 "- Germany: Dresden Music Festival (no dates); International Hanseatic Days 2028 in Stralsund, 15–18 Jun (off route).",
 "- Also checked, outside our dates: Tartini Festival in Piran (to about 5 Sep), Arcus Temporum at Pannonhalma (late Aug), the Anna Ball at Balatonfüred (late Jul), Grisia in Rovinj (late Aug), Feira de Santa Iria (mid-Oct, Faro), Festival des Andalousies Atlantiques in Essaouira (late Oct), International Nomads Festival at M'Hamid (spring).",
 "- Baltics and Nordics: Viljandi Hanseatic Days (early June), Kaunas City Days (late May), Riga Opera Festival (June, no dates), Midnight Sun Film Festival in Sodankylä (mid-June), Wolin Slavs and Vikings Festival (late July), Lofotr Viking Festival (no dates)."]
open(os.path.join(ROOT, "docs", "festivals.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
print(n, len(F))
