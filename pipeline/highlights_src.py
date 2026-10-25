# Day-by-day highlights between main stops, in driving order.
# Entry: (Wikipedia title, caption, type)  type: B beach, N nature, C culture, H history, P peaceful
# "~FERRY~" splits a ferry leg (items before = before sailing).
# ("~DATE~", "YYYY-MM-DD") = following items start on that date (earlier items spread up to it).
FERRY = "~FERRY~"
def DATE(d): return ("~DATE~", d)

H = {
"parnu>nida": [
 ("Jūrmala", "Pine dunes and 30 km of sand", "B"),
 ("Ventas Rumba", "Europe's widest waterfall, Kuldīga", "N"),
],
"nida>krakow": [
 ("Pažaislis Monastery", "Baroque monastery by Kaunas lagoon", "C"),
 ("Wigry National Park", "Lakes and forest, Suwałki", "P"),
 ("Warsaw Old Town", "Rebuilt brick by brick after 1944", "H"),
 ("Jasna Góra Monastery", "Black Madonna of Częstochowa", "C"),
],
"krakow>tatras": [
 ("Wieliczka Salt Mine", "Chapels carved in rock salt", "H"),
 ("Pieniny National Park (Poland)", "Dunajec gorge raft trip", "N"),
],
"tatras>trencin": [
 ("Orava Castle", "Castle on a crag above the river", "H"),
 ("Vlkolínec", "UNESCO log-house village", "P"),
],
"trencin>balaton": [
 ("Banská Štiavnica", "Silver-mining town in a crater", "H"),
 ("Esztergom Basilica", "Hungary's largest church on the Danube", "C"),
 ("Pannonhalma Archabbey", "Benedictine abbey since 996", "C"),
],
"balaton>soca": [
 ("Tihany Abbey", "Lavender and lake views", "C"),
 ("Lake Hévíz", "Swim in a warm thermal lake", "P"),
 ("Lake Bled", "Island church and castle", "N"),
 ("Lake Bohinj", "Quiet alpine lake for swimming", "P"),
],
"soca>plitvice": [
 ("Škocjan Caves", "Underground river canyon", "N"),
 ("Piran", "Venetian harbour town", "B"),
 ("Motovun", "Hilltop town above truffle forests", "C"),
 ("Rovinj", "Old town on the Istrian coast", "B"),
 ("Opatija", "Seafront promenade", "B"),
],
"plitvice>sarajevo": [
 ("Krka National Park", "Travertine falls and river", "N"),
 ("Kravica Waterfall", "Swim under the falls", "B"),
 ("Stari Most", "Mostar's Old Bridge", "H"),
],
"sarajevo>sutjeska": [
 ("Lukomir", "Bosnia's highest mountain village", "P"),
 ("Mehmed Paša Sokolović Bridge", "Ottoman bridge on the Drina", "H"),
 ("Perućica", "One of Europe's last primeval forests", "N"),
],
"sutjeska>durmitor": [
 ("Piva Lake", "Emerald reservoir in a canyon", "N"),
 ("Đurđevića Tara Bridge", "Bridge over the Tara canyon", "N"),
],
"durmitor>kotor": [
 ("Ostrog Monastery", "Monastery built into a cliff", "C"),
 ("Perast", "Baroque village and island churches", "H"),
],
"kotor>shkodra": [
 ("Sveti Stefan", "Island village and pink beaches", "B"),
 ("Stari Bar", "Ruined hill town", "H"),
],
"shkodra>riviera": [
 ("Theth", "Valley in the Accursed Mountains", "N"),
 ("Krujë Castle", "Skanderbeg's stronghold", "H"),
 ("Berat", "Town of a thousand windows", "H"),
],
"riviera>zagori": [
 ("Ksamil", "White beaches and islets", "B"),
 ("Butrint", "Greek, Roman and Venetian ruins", "H"),
 ("Gjirokastër", "Stone town and castle", "H"),
],
"zagori>meteora": [
 ("Papingo", "Stone village under the Astraka towers", "P"),
 ("Ioannina", "Lakeside castle town", "C"),
 ("Metsovo", "Mountain village of the Pindus", "C"),
],
"meteora>igoumenitsa": [
 ("Dodona", "Oracle and ancient theatre", "H"),
 ("Parga", "Harbour town and castle", "B"),
 ("Syvota", "Turquoise coves", "B"),
],
"igoumenitsa>matera": [
 FERRY,
 ("Alberobello", "Trulli houses", "C"),
],
"matera>barbagia": [
 ("Amalfi Coast", "Cliff road above the sea", "B"),
 ("Pompeii", "Roman city under the ash", "H"),
 ("Civita di Bagnoregio", "Village on a crumbling pinnacle", "P"),
 FERRY,
 ("Cala Goloritzé", "Limestone arch and clear water", "B"),
],
"barbagia>portotorres": [
 ("Su Nuraxi di Barumini", "Bronze Age stone towers", "H"),
 ("Tharros", "Phoenician city by the sea", "H"),
 ("Bosa", "Pastel town on the river", "C"),
 ("Alghero", "Catalan walled town", "C"),
 ("Neptune's Grotto", "Sea cave at Capo Caccia", "N"),
 ("Stintino", "La Pelosa beach", "B"),
],
"portotorres>logrono": [
 FERRY,
 ("Sagrada Família", "Gaudí's basilica", "C"),
 ("Montserrat (mountain)", "Monastery in the saw-tooth peaks", "C"),
],
"logrono>picos": [
 ("Laguardia", "Walled wine village", "C"),
 ("San Millán de la Cogolla", "Yuso and Suso monasteries", "H"),
 ("Burgos Cathedral", "Gothic cathedral", "C"),
 ("Guggenheim Museum Bilbao", "Titanium museum", "C"),
 ("San Juan de Gaztelugatxe", "Islet chapel and stone stair", "N"),
 ("Santillana del Mar", "Medieval village", "H"),
 ("Fuente Dé", "Cable car into the Picos", "N"),
],
"picos>douro": [
 ("Lakes of Covadonga", "Glacial lakes in the Picos", "N"),
 ("Cudillero", "Fishing village of coloured houses", "P"),
 ("As Catedrais beach", "Rock arches at low tide", "B"),
 ("Roman walls of Lugo", "Complete Roman city walls", "H"),
 ("Ribeira Sacra", "Terraced vineyards in the Sil canyon", "N"),
 ("Santiago de Compostela Cathedral", "End of the Camino", "C"),
 ("Cape Finisterre", "The end of the world", "N"),
 ("Combarro", "Granaries on the shore", "P"),
 ("Castro of Santa Trega", "Celtic hill fort over the Miño", "H"),
 ("Peneda-Gerês National Park", "Portugal's only national park", "N"),
 ("Bom Jesus do Monte", "Baroque stairway", "C"),
 ("Guimarães Castle", "Birthplace of Portugal", "H"),
 ("Dom Luís I Bridge", "Porto's iron bridge", "C"),
 ("Amarante, Portugal", "Bridge town on the Tâmega", "P"),
],
"douro>golega": [
 ("Mateus Palace", "Baroque manor and gardens", "C"),
 ("Pinhão", "Quintas at harvest", "C"),
 ("Vila Nova de Foz Côa", "Côa Valley rock art", "H"),
 ("Lamego", "Shrine stairway of 686 steps", "C"),
 ("Serra da Estrela", "Portugal's highest mountains", "N"),
 ("Piódão", "Schist village in the hills", "P"),
 ("Buçaco Palace", "Palace in an ancient forest", "C"),
 ("University of Coimbra", "Old university and library", "H"),
 ("Aveiro, Portugal", "Canals and moliceiro boats", "C"),
 ("Costa Nova do Prado", "Striped beach houses", "B"),
 ("Conímbriga", "Roman mosaics", "H"),
 ("Batalha Monastery", "Gothic monastery", "H"),
 ("Alcobaça Monastery", "Cistercian abbey", "H"),
 ("Nazaré, Portugal", "Giant-wave beach", "B"),
 ("Óbidos, Portugal", "Walled village", "H"),
 ("Peniche, Portugal", "Cliffs and surf", "B"),
 ("Ericeira", "Surf village", "B"),
 ("Pena Palace", "Sintra's painted palace", "C"),
 ("Cabo da Roca", "Westernmost point of mainland Europe", "N"),
 ("Belém Tower", "Age of Discovery", "H"),
 ("Alfama", "Lisbon's oldest quarter and fado", "C"),
 ("Arrábida Natural Park", "Hills dropping into clear sea", "B"),
 ("Comporta", "Rice fields and empty beaches", "B"),
 ("Roman Temple of Évora", "Roman temple in a walled city", "H"),
 ("Monsaraz", "Hilltop village over the lake", "P"),
 ("Marvão", "Eagle's-nest village", "P"),
 ("Castelo de Vide", "Jewish quarter and springs", "H"),
 ("Convent of Christ (Tomar)", "Templar castle-convent", "H"),
 ("Almourol Castle", "Castle on a river island", "H"),
],
"golega>algeciras": [
 ("Ponta da Piedade", "Sea stacks at Lagos", "B"),
 ("Benagil Cave", "Sea cave with a skylight", "B"),
 ("Vejer de la Frontera", "White hill town", "P"),
],
"algeciras>toubkal": [
 FERRY,
 ("Chefchaouen", "The blue town", "C"),
 ("Volubilis", "Roman city in Morocco", "H"),
 ("Fes el Bali", "Medieval medina", "H"),
 ("Ifrane National Park", "Cedar forests and macaques", "N"),
 ("Ouzoud Falls", "110 m waterfall", "N"),
 ("Jemaa el-Fnaa", "Marrakech's great square", "C"),
 ("Majorelle Garden", "Blue garden in Marrakech", "P"),
],
"toubkal>merzouga": [
 ("Telouet Kasbah", "Glaoui palace on the old caravan road", "H"),
 ("Aït Benhaddou", "Earthen ksar", "H"),
 ("Taourirt Kasbah", "Ouarzazate kasbah", "H"),
 ("Agdz", "Draa valley palm groves", "P"),
 ("Tamegroute", "Green pottery and old library", "C"),
 ("N'Kob", "Village of kasbahs", "H"),
 ("Rissani", "Market town of the Tafilalt", "C"),
],
"merzouga>tiznit": [
 ("Todgha Gorge", "300 m canyon walls", "N"),
 ("Dadès Gorges", "Hairpin road through red rock", "N"),
 ("Kalaat M'Gouna", "Valley of roses", "P"),
 ("Skoura", "Palm oasis and kasbahs", "P"),
 ("Taliouine", "Saffron country", "C"),
 ("Taroudant", "Walled market town", "H"),
 ("Taghazout", "Surf village", "B"),
 ("Agadir Oufella", "Kasbah ruins over the bay", "H"),
 ("Souss-Massa National Park", "Bald ibis and estuary", "N"),
 ("Aglou", "Long Atlantic beach", "B"),
],
"tiznit>camargue": [
 # winter base: excursions every few days
 ("Mirleft", "Cliff coves", "B"),
 ("Legzira", "Red sea arches", "B"),
 ("Sidi Ifni", "Art-deco Spanish town", "H"),
 ("Guelmim", "Camel market, gateway to the Sahara", "C"),
 ("Tan-Tan", "Saharan town", "C"),
 ("Khenifiss National Park", "Lagoon and flamingos", "N"),
 ("Tarfaya", "Saint-Exupéry's airmail post", "H"),
 ("Amtoudi", "Fortified granary on a crag", "H"),
 ("Akka", "Oasis and rock art", "H"),
 ("Tata, Morocco", "Desert oasis town", "P"),
 ("Tafraoute", "Granite valley of almond blossom", "P"),
 DATE("2028-02-12"),
 ("Imsouane", "Long right-hand wave", "B"),
 ("Essaouira", "Ramparts and fishing port", "C"),
 ("Oualidia", "Lagoon and oysters", "P"),
 ("Portuguese City of Mazagan", "Portuguese cistern, El Jadida", "H"),
 ("Hassan II Mosque", "Mosque over the Atlantic", "C"),
 ("Kasbah of the Udayas", "Blue-and-white kasbah, Rabat", "H"),
 ("Asilah", "Whitewashed walls and murals", "C"),
 FERRY,
 DATE("2028-02-19"),
 ("Rock of Gibraltar", "Barbary macaques on the Rock", "N"),
 ("Baelo Claudia", "Roman town on a dune beach", "B"),
 ("Cádiz", "Old port city on a peninsula", "C"),
 ("Doñana National Park", "Marshes, lynx and flamingos", "N"),
 ("Alcázar of Seville", "Royal palace and gardens", "H"),
 ("Mosque–Cathedral of Córdoba", "Forest of striped arches", "H"),
 ("Setenil de las Bodegas", "Houses under the rock", "P"),
 ("Ronda", "Bridge over the gorge", "H"),
 ("Caminito del Rey", "Cliff walkway through a gorge", "N"),
 ("Cave of Nerja", "Giant caverns by the sea", "N"),
 ("Alhambra", "Nasrid palaces, Granada", "H"),
 ("Guadix", "Cave houses", "C"),
 ("Cabo de Gata-Níjar Natural Park", "Volcanic coast and empty coves", "B"),
 ("Mojácar", "White village above the sea", "B"),
 ("Roman Theatre of Cartagena", "Theatre found under the city", "H"),
 ("Guadalest", "Castle village on a rock", "P"),
 ("City of Arts and Sciences", "Valencia", "C"),
 ("Albufera (Valencia)", "Lagoon, rice fields and paella", "P"),
 ("Peñíscola", "Castle on a sea rock", "H"),
 ("Morella, Castellón", "Walled hill town", "H"),
 ("Ebro Delta", "Rice fields and flamingos", "N"),
 ("Amphitheatre of Tarragona", "Roman arena by the sea", "H"),
 ("Sitges", "Beaches and old town", "B"),
 ("Girona Cathedral", "Stairway and old Jewish quarter", "H"),
 ("Besalú", "Medieval bridge", "H"),
 ("Cadaqués", "Dalí's white fishing village", "B"),
 ("Cap de Creus", "Wind-carved headland", "N"),
 ("Collioure", "Painters' harbour", "B"),
 ("Cité de Carcassonne", "Walled medieval city", "H"),
 ("Aigues-Mortes", "Walled town in the salt marsh", "H"),
],
"camargue>alsace": [
 ("Arles Amphitheatre", "Roman arena", "H"),
 ("Les Baux-de-Provence", "Village on a rock spur", "H"),
 ("Calanques National Park", "Limestone inlets", "B"),
 ("Cassis", "Harbour and cliffs", "B"),
 ("Gorges du Verdon", "Europe's grandest canyon", "N"),
 ("Moustiers-Sainte-Marie", "Village with a star on a chain", "P"),
 ("Gordes", "Stone village on a hill", "P"),
 ("Sénanque Abbey", "Cistercian abbey", "P"),
 ("Roussillon, Vaucluse", "Ochre cliffs", "N"),
 ("Mont Ventoux", "Giant of Provence", "N"),
 ("Palais des Papes", "Popes' palace, Avignon", "H"),
 ("Pont du Gard", "Roman aqueduct", "H"),
 ("Pont d'Arc", "Natural arch over the Ardèche", "N"),
 ("Château de Grignan", "Renaissance château", "H"),
 ("Vercors Massif", "Limestone plateau", "N"),
 ("Vieux Lyon", "Renaissance old town", "C"),
 ("Pérouges", "Medieval village", "H"),
 ("Lake Annecy", "Clear alpine lake", "N"),
 ("Aiguille du Midi", "Cable car to Mont Blanc's face", "N"),
 ("Lavaux", "Vineyard terraces over Lake Geneva", "C"),
 ("Chillon Castle", "Castle on the lake", "H"),
 ("Gruyères", "Cheese town and castle", "C"),
 ("Old City (Bern)", "Arcaded old town", "H"),
 ("Lauterbrunnen", "Valley of 72 waterfalls", "N"),
 ("Rhine Falls", "Europe's largest waterfall by volume", "N"),
 ("Basel Minster", "Red sandstone cathedral", "C"),
 ("Colmar", "Canals of Little Venice", "C"),
 ("Eguisheim", "Circular wine village", "P"),
 ("Kaysersberg", "Village under a ruined castle", "P"),
 ("Haut-Kœnigsbourg Castle", "Castle over the Alsace plain", "H"),
],
"alsace>berlin": [
 ("Strasbourg Cathedral", "Pink sandstone Gothic", "C"),
 ("Porta Nigra", "Roman gate, Trier", "H"),
 ("Reichsburg Cochem", "Castle over the Moselle", "H"),
 ("Burg Eltz", "Castle in a forest valley", "H"),
 ("Loreley", "Rock above the Rhine gorge", "N"),
 ("Rüdesheim am Rhein", "Vineyards and the Niederwald", "C"),
 ("Heidelberg Castle", "Red castle over the Neckar", "H"),
 ("Rothenburg ob der Tauber", "Walled medieval town", "H"),
 ("Würzburg Residence", "Baroque palace", "C"),
 ("Bamberg", "Old town on the river", "H"),
 ("Wartburg", "Where Luther translated the Bible", "H"),
 ("Weimar", "Goethe and Schiller's town", "C"),
 ("Königstein Fortress", "Fortress on a table mountain", "H"),
 ("Bastei", "Sandstone bridge over the Elbe", "N"),
 ("Frauenkirche, Dresden", "Rebuilt baroque church", "C"),
 ("Moritzburg Castle (Saxony)", "Moated hunting lodge", "H"),
 ("Muskau Park", "Landscape park across the border", "P"),
 ("Spreewald", "Paddle the forest canals", "P"),
 ("Sanssouci", "Frederick the Great's palace", "H"),
],
"berlin>home1": [
 ("Chorin Abbey", "Brick Gothic abbey ruin", "H"),
 ("Wolin National Park", "Cliffs and bison", "N"),
 ("Słowiński National Park", "Moving sand dunes", "N"),
 ("Hel Peninsula", "Sand spit into the Baltic", "B"),
 ("St. Mary's Church, Gdańsk", "Largest brick church", "C"),
 ("Westerplatte", "Where WWII began", "H"),
 ("Malbork Castle", "Teutonic Knights' castle", "H"),
 ("Elbląg Canal", "Boats hauled over hills", "H"),
 ("Frombork", "Copernicus's cathedral", "H"),
 ("Święta Lipka", "Baroque pilgrimage church", "C"),
 ("Wolf's Lair", "Hitler's forest bunkers", "H"),
 ("Mikołajki", "Masurian lakes", "P"),
 ("Białowieża Forest", "Primeval forest and bison", "N"),
 ("Druskininkai", "Spa town on the Neman", "P"),
 ("Grūtas Park", "Soviet statue park", "H"),
 ("Trakai Island Castle", "Castle in the lake", "H"),
 ("Vilnius Old Town", "Baroque old town", "C"),
 ("Kernavė", "Hill forts of the first capital", "H"),
 ("Kaunas Castle", "Castle at the river fork", "H"),
 ("Hill of Crosses", "Thousands of crosses", "C"),
 ("Rundāle Palace", "Rastrelli's baroque palace", "C"),
 ("Bauska Castle", "Castle on two rivers", "H"),
 ("Old Riga", "Art Nouveau and the old town", "C"),
 ("Ķemeri National Park", "Boardwalk over the bog", "P"),
 ("Cape Kolka", "Where the gulf meets the sea", "N"),
 ("Turaida Castle", "Red castle in the Gauja valley", "H"),
 ("Gauja National Park", "Sandstone cliffs and canoeing", "N"),
 ("Cēsis Castle", "Livonian Order castle", "H"),
 ("Āraiši Lake Fortress", "Reconstructed lake dwelling", "H"),
 ("Rõuge", "Valley of seven lakes", "P"),
 ("Suur Munamägi", "Highest point in the Baltics", "N"),
 ("Piusa Caves", "Sandstone caves and bats", "N"),
 ("Tartu", "University town", "C"),
 ("Lake Peipus", "Old Believer villages", "P"),
 ("Pühtitsa Convent", "Orthodox convent at Kuremäe", "C"),
 ("Narva Castle", "Castle facing Russia", "H"),
 ("Valaste waterfall", "Waterfall over the cliff", "N"),
 ("Lahemaa National Park", "Manors, bogs and coast", "N"),
 ("Palmse Manor", "Baltic German manor", "H"),
 ("Jägala waterfall", "Estonia's widest waterfall", "N"),
 ("Keila Falls", "Waterfall and manor park", "P"),
 ("Haapsalu Castle", "Bishop's castle by the sea", "H"),
 ("Matsalu National Park", "Bird migration reserve", "N"),
 ("Viljandi Castle", "Castle ruins over the lake", "H"),
 ("Soomaa National Park", "Bog land and canoe trips", "P"),
],
"home1>rovaniemi": [
 DATE("2028-07-12"),
 FERRY,
 ("Helsinki Cathedral", "White cathedral on Senate Square", "C"),
 ("Häme Castle", "Brick castle by the lake", "H"),
],
"rovaniemi>nordkapp": [
 ("Pyhä-Luosto National Park", "Fell ridges and old forest", "N"),
 ("Urho Kekkonen National Park", "Fells of Lapland", "N"),
 ("Siida", "Sámi museum, Inari", "C"),
 ("Lake Inari", "Lake of 3,000 islands", "P"),
 ("Kevo Strict Nature Reserve", "Canyon in the tundra", "N"),
],
"nordkapp>lofoten": [
 ("Alta Museum", "Rock carvings", "H"),
 ("Lyngen Alps", "Peaks rising from the fjord", "N"),
 ("Arctic Cathedral", "Tromsø's church", "C"),
 ("Senja", "Peaks and white beaches", "B"),
 ("Andenes", "Whale safaris", "N"),
 ("Henningsvær", "Fishing village on skerries", "P"),
 ("Nusfjord", "Old fishing village", "H"),
],
"lofoten>geiranger": [
 ("Lofotr Viking Museum", "Chieftain's longhouse", "H"),
 ("Kjerringøy", "Old trading post", "H"),
 ("Saltstraumen", "World's strongest tidal current", "N"),
 ("Saltfjellet–Svartisen National Park", "Glacier and the Arctic Circle", "N"),
 ("Torghatten", "Mountain with a hole", "N"),
 ("Nidaros Cathedral", "Trondheim cathedral", "C"),
 ("Atlantic Ocean Road", "Road over the skerries", "N"),
 ("Ålesund", "Art Nouveau town", "C"),
 ("Trollveggen", "Europe's tallest rock face", "N"),
 ("Trollstigen", "Hairpins up the mountain", "N"),
],
"geiranger>stockholm": [
 ("Briksdalsbreen", "Glacier arm", "N"),
 ("Urnes Stave Church", "Oldest stave church", "H"),
 ("Borgund Stave Church", "Best-kept stave church", "H"),
 ("Nærøyfjord", "Narrowest fjord", "N"),
 ("Bryggen", "Hanseatic wharf, Bergen", "H"),
 ("Vøringsfossen", "182 m waterfall", "N"),
 ("Heddal Stave Church", "Largest stave church", "H"),
 ("Oslo Opera House", "Walk on the roof", "C"),
 ("Örebro Castle", "Castle in the river", "H"),
],
"stockholm>home2": [
 FERRY,
 ("Kadriorg Palace", "Peter the Great's palace", "H"),
 ("Rummu", "Flooded quarry lake", "P"),
 ("Padise Abbey", "Cistercian monastery ruin", "H"),
],
}

# ---- denser legs (two sights on most days) ----
H["nida>krakow"] = [
 ("Pažaislis Monastery", "Baroque monastery by Kaunas lagoon", "C"),
 ("Wigry National Park", "Lakes and forest, Suwałki", "P"),
 ("Warsaw Old Town", "Rebuilt brick by brick after 1944", "H"),
 ("Łazienki Park", "Palace on the water, Warsaw", "P"),
 ("Jasna Góra Monastery", "Black Madonna of Częstochowa", "C"),
 ("Ojców National Park", "Limestone valley and castle", "N"),
]
H["krakow>tatras"] = [
 ("Wieliczka Salt Mine", "Chapels carved in rock salt", "H"),
 ("Niedzica Castle", "Castle above the Dunajec lake", "H"),
 ("Pieniny National Park (Poland)", "Dunajec gorge raft trip", "N"),
 ("Chochołów", "Village of log houses", "P"),
]
H["camargue>alsace"] = [
 ("Maison Carrée", "Roman temple, Nîmes", "H"),
 ("Arles Amphitheatre", "Roman arena", "H"),
 ("Glanum", "Roman town under the Alpilles", "H"),
 ("Les Baux-de-Provence", "Village on a rock spur", "H"),
 ("Cours Mirabeau", "Fountains and plane trees, Aix", "C"),
 ("Montagne Sainte-Victoire", "Cézanne's mountain", "N"),
 ("Calanques National Park", "Limestone inlets", "B"),
 ("Cassis", "Harbour and cliffs", "B"),
 ("Lac de Sainte-Croix", "Turquoise lake for a swim", "B"),
 ("Gorges du Verdon", "Europe's grandest canyon", "N"),
 ("Moustiers-Sainte-Marie", "Village with a star on a chain", "P"),
 ("Plateau de Valensole", "Lavender plateau", "P"),
 ("Gordes", "Stone village on a hill", "P"),
 ("Sénanque Abbey", "Cistercian abbey", "P"),
 ("Roussillon, Vaucluse", "Ochre cliffs", "N"),
 ("Fontaine-de-Vaucluse", "Spring of the Sorgue", "N"),
 ("L'Isle-sur-la-Sorgue", "Water wheels and antiques", "C"),
 ("Palais des Papes", "Popes' palace, Avignon", "H"),
 ("Pont du Gard", "Roman aqueduct", "H"),
 ("Roman Theatre of Orange", "Roman stage wall still standing", "H"),
 ("Vaison-la-Romaine", "Roman town and medieval upper town", "H"),
 ("Dentelles de Montmirail", "Lace-like limestone ridges", "N"),
 ("Mont Ventoux", "Giant of Provence", "N"),
 ("Pont d'Arc", "Natural arch over the Ardèche", "N"),
 ("Château de Grignan", "Renaissance château", "H"),
 ("Vercors Massif", "Limestone plateau", "N"),
 ("Bastille (Grenoble)", "Cable-car bubbles over Grenoble", "C"),
 ("Grande Chartreuse", "Monastery in the mountains", "P"),
 ("Vieux Lyon", "Renaissance old town", "C"),
 ("Pérouges", "Medieval village", "H"),
 ("Lake Annecy", "Clear alpine lake", "N"),
 ("Palais de l'Isle", "Prison on the canal, Annecy", "H"),
 ("Mer de Glace", "France's longest glacier", "N"),
 ("Aiguille du Midi", "Cable car to Mont Blanc's face", "N"),
 ("Yvoire", "Medieval village on Lake Geneva", "P"),
 ("Lavaux", "Vineyard terraces over Lake Geneva", "C"),
 ("Chillon Castle", "Castle on the lake", "H"),
 ("Gruyères", "Cheese town and castle", "C"),
 ("Old City (Bern)", "Arcaded old town", "H"),
 ("Oeschinen Lake", "Lake under the cliffs", "N"),
 ("Lauterbrunnen", "Valley of 72 waterfalls", "N"),
 ("Chapel Bridge", "Wooden bridge, Lucerne", "H"),
 ("Rhine Falls", "Europe's largest waterfall by volume", "N"),
 ("Basel Minster", "Red sandstone cathedral", "C"),
 ("Colmar", "Canals of Little Venice", "C"),
 ("Eguisheim", "Circular wine village", "P"),
 ("Kaysersberg", "Village under a ruined castle", "P"),
 ("Haut-Kœnigsbourg Castle", "Castle over the Alsace plain", "H"),
]
H["alsace>berlin"] = [
 ("Strasbourg Cathedral", "Pink sandstone Gothic", "C"),
 ("Saarschleife", "Hairpin bend of the Saar", "N"),
 ("Porta Nigra", "Roman gate, Trier", "H"),
 ("Bernkastel-Kues", "Half-timbered wine town", "C"),
 ("Reichsburg Cochem", "Castle over the Moselle", "H"),
 ("Burg Eltz", "Castle in a forest valley", "H"),
 ("Marksburg", "Unconquered Rhine castle", "H"),
 ("Loreley", "Rock above the Rhine gorge", "N"),
 ("Bacharach", "Wine village under Stahleck castle", "P"),
 ("Rüdesheim am Rhein", "Vineyards and the Niederwald", "C"),
 ("Speyer Cathedral", "Romanesque imperial cathedral", "H"),
 ("Heidelberg Castle", "Red castle over the Neckar", "H"),
 ("Dinkelsbühl", "Walled town on the Romantic Road", "H"),
 ("Rothenburg ob der Tauber", "Walled medieval town", "H"),
 ("Würzburg Residence", "Baroque palace", "C"),
 ("Bamberg", "Old town on the river", "H"),
 ("Veste Coburg", "One of Germany's largest castles", "H"),
 ("Wartburg", "Where Luther translated the Bible", "H"),
 ("Erfurt Cathedral", "Cathedral on the hill", "H"),
 ("Weimar", "Goethe and Schiller's town", "C"),
 ("St. Thomas Church, Leipzig", "Bach's church", "C"),
 ("Königstein Fortress", "Fortress on a table mountain", "H"),
 ("Bastei", "Sandstone bridge over the Elbe", "N"),
 ("Zwinger", "Baroque palace courtyard, Dresden", "C"),
 ("Frauenkirche, Dresden", "Rebuilt baroque church", "C"),
 ("Moritzburg Castle (Saxony)", "Moated hunting lodge", "H"),
 ("Görlitz", "Untouched old town on the Neisse", "H"),
 ("Muskau Park", "Landscape park across the border", "P"),
 ("Spreewald", "Paddle the forest canals", "P"),
 ("All Saints' Church, Wittenberg", "Luther's theses door", "H"),
 ("Sanssouci", "Frederick the Great's palace", "H"),
]
_b = H["berlin>home1"]
_i = lambda t: [e[0] for e in _b].index(t)
_b.insert(_i("Wolin National Park"), ("Trzęsacz", "Church ruin on the cliff edge", "P"))
_b.insert(_i("Trzęsacz"), ("Pomeranian Dukes' Castle", "Renaissance castle, Szczecin", "H"))
_b.insert(_i("St. Mary's Church, Gdańsk"), ("Oliwa Cathedral", "Organ and park", "C"))
_b.insert(_i("Oliwa Cathedral"), ("Sopot", "Longest wooden pier in Europe", "B"))
_b.insert(_i("Święta Lipka"), ("Lidzbark Warmiński Castle", "Bishops' castle of Warmia", "H"))
_b.insert(_i("Mikołajki"), ("Krutynia", "Canoe the lake-forest river", "P"))
_b.insert(_i("Białowieża Forest"), ("Tykocin", "Baroque synagogue in a quiet town", "H"))
H["rovaniemi>nordkapp"] = [
 ("Santa Claus Village", "On the Arctic Circle", "C"),
 ("Sodankylä Old Church", "Log church from 1689", "H"),
 ("Pyhä-Luosto National Park", "Fell ridges and old forest", "N"),
 ("Tankavaara", "Gold-panning village", "C"),
 ("Urho Kekkonen National Park", "Fells of Lapland", "N"),
 ("Siida", "Sámi museum, Inari", "C"),
 ("Sajos", "Sámi parliament building", "C"),
 ("Lake Inari", "Lake of 3,000 islands", "P"),
 ("Kevo Strict Nature Reserve", "Canyon in the tundra", "N"),
 ("Tana (river)", "Salmon river on the border", "P"),
]
H["nordkapp>lofoten"] = [
 ("Alta Museum", "Rock carvings", "H"),
 ("Alta Canyon", "Northern Europe's largest canyon", "N"),
 ("Lyngen Alps", "Peaks rising from the fjord", "N"),
 ("Fjellheisen", "Cable car over Tromsø", "N"),
 ("Arctic Cathedral", "Tromsø's church", "C"),
 ("Segla", "Sheer peak on Senja", "N"),
 ("Senja", "Peaks and white beaches", "B"),
 ("Bleik", "Long white beach", "B"),
 ("Andenes", "Whale safaris", "N"),
 ("Svolvær", "Lofoten's harbour town", "C"),
 ("Vågan Church", "Lofoten Cathedral", "H"),
 ("Henningsvær", "Fishing village on skerries", "P"),
 ("Haukland Beach", "White sand under the peaks", "B"),
 ("Nusfjord", "Old fishing village", "H"),
 ("Hamnøy", "Red cabins under the peaks", "P"),
]
H["lofoten>geiranger"] = [
 ("Lofotr Viking Museum", "Chieftain's longhouse", "H"),
 ("Kjerringøy", "Old trading post", "H"),
 ("Saltstraumen", "World's strongest tidal current", "N"),
 ("Saltfjellet–Svartisen National Park", "Glacier and the Arctic Circle", "N"),
 ("Seven Sisters (mountains)", "Seven peaks above the coast", "N"),
 ("Petter Dass Museum", "Poet-priest's museum", "C"),
 ("Torghatten", "Mountain with a hole", "N"),
 ("Nidaros Cathedral", "Trondheim cathedral", "C"),
 ("Munkholmen", "Monastery-fortress island", "H"),
 ("Atlantic Ocean Road", "Road over the skerries", "N"),
 ("Ålesund", "Art Nouveau town", "C"),
 ("Rampestreken", "Viewing platform over Åndalsnes", "N"),
 ("Trollveggen", "Europe's tallest rock face", "N"),
 ("Trollstigen", "Hairpins up the mountain", "N"),
]
H["geiranger>stockholm"] = [
 ("Dalsnibba", "Skywalk 1,500 m above Geiranger", "N"),
 ("Loen Skylift", "Cable car up from the fjord", "N"),
 ("Briksdalsbreen", "Glacier arm", "N"),
 ("Urnes Stave Church", "Oldest stave church", "H"),
 ("Borgund Stave Church", "Best-kept stave church", "H"),
 ("Stegastein", "Platform over the Aurlandsfjord", "N"),
 ("Flåm Line", "Railway down the valley", "C"),
 ("Nærøyfjord", "Narrowest fjord", "N"),
 ("Bryggen", "Hanseatic wharf, Bergen", "H"),
 ("Vøringsfossen", "182 m waterfall", "N"),
 ("Hardangervidda", "Europe's largest mountain plateau", "N"),
 ("Heddal Stave Church", "Largest stave church", "H"),
 ("Vemork", "Heavy-water saboteurs' plant", "H"),
 ("Oslo Opera House", "Walk on the roof", "C"),
 ("Örebro Castle", "Castle in the river", "H"),
]

# ---- Festival re-dating (25 Oct 2026): pins festival days, adds festival places ----
def _i(key, title): return [e[0] if isinstance(e, tuple) else e for e in H[key]].index(title)
def _pin(key, title, d): H[key].insert(_i(key, title), DATE(d))
def _add(key, before, item): H[key].insert(_i(key, before) if before else len(H[key]), item)
def _cap(key, title, extra):
    j = _i(key, title); t, c, ty = H[key][j]; H[key][j] = (t, f"{c}; {extra}", ty)

# Slovakia: Východná folklore festival (first weekend of July), stay for Pohoda (8-10 Jul)
H["tatras>trencin"] = [DATE("2027-07-04"),
    ("Východná", "Slovakia's oldest folklore festival, first weekend of July", "C"),
    ("Vlkolínec", "UNESCO log-house village", "P"),
    ("Orava Castle", "Castle on a crag above the river", "H")]
H["trencin>balaton"].insert(0, DATE("2027-07-11"))
# Mostar bridge diving, last Sunday of July
_pin("plitvice>sarajevo", "Stari Most", "2027-07-25")
_cap("plitvice>sarajevo", "Stari Most", "bridge diving contest, last Sunday of July")
# Puglia: Notte della Taranta final (4th Saturday of August)
_add("igoumenitsa>matera", "Alberobello", DATE("2027-08-28"))
_add("igoumenitsa>matera", "Alberobello", ("Melpignano", "La Notte della Taranta: big pizzica folk concert, late-August Saturday", "C"))
# Amalfi Byzantine New Year (31 Aug), then Civitavecchia ferry
_pin("matera>barbagia", "Amalfi Coast", "2027-08-31")
_cap("matera>barbagia", "Amalfi Coast", "Byzantine New Year parade, 31 Aug")
_pin("matera>barbagia", "Pompeii", "2027-09-01")
_pin("matera>barbagia", "Cala Goloritzé", "2027-09-02")
# Cabras barefoot race (first weekend of September)
_pin("barbagia>portotorres", "Tharros", "2027-09-04")
_cap("barbagia>portotorres", "Tharros", "Corsa degli Scalzi barefoot race at Cabras")
# Barcelona for the Diada (11 Sep), Pyrenees, San Sebastián Film Festival, Logroño San Mateo
_cap("portotorres>logrono", "Sagrada Família", "Diada, Catalan National Day, 11 Sep")
_pin("portotorres>logrono", "Montserrat (mountain)", "2027-09-12")
for t in [("Aigüestortes i Estany de Sant Maurici National Park", "Granite peaks and 200 lakes", "N"),
          ("Ordesa y Monte Perdido National Park", "Canyon walk to the Cola de Caballo falls", "N"),
          ("Castle of Loarre", "Spain's best-kept Romanesque castle", "H"),
          ("Bardenas Reales", "Badlands desert in Navarre", "N")]:
    _add("portotorres>logrono", None, t)
_add("portotorres>logrono", None, DATE("2027-09-17"))
_add("portotorres>logrono", None, ("San Sebastián", "La Concha bay and pintxos; Film Festival opens mid-September", "C"))
# O Grove seafood festival (from 1 Oct)
_pin("picos>douro", "Combarro", "2027-10-01")
_cap("picos>douro", "Combarro", "Festa do Marisco at O Grove nearby, from 1 Oct")
# Portugal: Fátima 12 Oct, Óbidos FOLIO mid-October
_d = {e[0]: e for e in H["douro>golega"] if isinstance(e, tuple)}
_fat = ("Sanctuary of Fátima", "Candlelight procession on the night of 12 Oct", "C")
_order1 = ["Mateus Palace", "Pinhão", "Vila Nova de Foz Côa", "Lamego", "Serra da Estrela", "Piódão", "Buçaco Palace"]
_order2 = ["University of Coimbra", "Aveiro, Portugal", "Costa Nova do Prado", "Conímbriga", "Batalha Monastery",
           "Alcobaça Monastery", "Nazaré, Portugal"]
_rest = [t for t in _d if t not in _order1 + _order2 + ["Óbidos, Portugal"]]
H["douro>golega"] = ([_d[t] for t in _order1] + [DATE("2027-10-12"), _fat] + [_d[t] for t in _order2] +
                     [DATE("2027-10-16"), _d["Óbidos, Portugal"]] + [_d[t] for t in _rest])
_cap("douro>golega", "Óbidos, Portugal", "FOLIO literary festival")
# Algarve on São Martinho (11 Nov), after the Golegã horse fair opening weekend
_pin("golega>algeciras", "Ponta da Piedade", "2027-11-09")
_pin("golega>algeciras", "Vejer de la Frontera", "2027-11-12")
_cap("golega>algeciras", "Benagil Cave", "São Martinho chestnuts and new wine, 11 Nov")
_cap("algeciras>toubkal", "Jemaa el-Fnaa", "Marrakech Film Festival, late November")
# Andalusia: Cádiz Carnival opening, Fallas main days, La Magdalena at Castellón
_pin("tiznit>camargue", "Cádiz", "2028-02-24")
_cap("tiznit>camargue", "Cádiz", "Carnival opens; Festival de Jerez flamenco nearby")
_pin("tiznit>camargue", "Doñana National Park", "2028-02-27")
_pin("tiznit>camargue", "City of Arts and Sciences", "2028-03-15")
_cap("tiznit>camargue", "City of Arts and Sciences", "Fallas main days 15-19 Mar")
_pin("tiznit>camargue", "Peñíscola", "2028-03-20")
_cap("tiznit>camargue", "Peñíscola", "via Castellón for La Magdalena")
# Germany: Easter fountains at Bamberg, Walpurgis Night at Erfurt (30 Apr)
_pin("alsace>berlin", "Bamberg", "2028-04-28")
_cap("alsace>berlin", "Bamberg", "Easter fountains in Franconian villages")
_pin("alsace>berlin", "Wartburg", "2028-04-29")
_pin("alsace>berlin", "Erfurt Cathedral", "2028-04-30")
_cap("alsace>berlin", "Erfurt Cathedral", "Walpurgis Night and maypole on Domplatz, 30 Apr")
_pin("alsace>berlin", "Weimar", "2028-05-01")

# ---- Departure moved to 19 Jul 2027 (25 Oct 2026): all 2027 dates +24 days; Toubkal after the winter base ----
from datetime import date as _date, timedelta as _td
for _k, _v in H.items():
    for _j, _e in enumerate(_v):
        if isinstance(_e, tuple) and _e[0] == "~DATE~" and _e[1] < "2028-01-01":
            _v[_j] = DATE((_date.fromisoformat(_e[1]) + _td(days=24)).isoformat())
def _uncap(key, title, cap=None):
    j = _i(key, title); t, c, ty = H[key][j]; H[key][j] = (t, cap or c.split("; ")[0], ty)
# festival-only detour no longer lines up: drop Melpignano (and its date pin)
_j = _i("igoumenitsa>matera", "Melpignano"); del H["igoumenitsa>matera"][_j - 1:_j + 1]
for _k, _t in [("plitvice>sarajevo", "Stari Most"), ("matera>barbagia", "Amalfi Coast"), ("barbagia>portotorres", "Tharros"),
               ("portotorres>logrono", "Sagrada Família"), ("picos>douro", "Combarro"), ("douro>golega", "Óbidos, Portugal"),
               ("golega>algeciras", "Benagil Cave"), ("algeciras>toubkal", "Jemaa el-Fnaa")]:
    _uncap(_k, _t)
_uncap("tatras>trencin", "Východná", "Folk-festival village under Kriváň")
_uncap("portotorres>logrono", "San Sebastián", "La Concha bay and pintxos")
_uncap("douro>golega", "Sanctuary of Fátima", "Pilgrimage shrine and basilica")
# Toubkal at the end of the winter base, then north to the ferry (19 Feb)
_L = H["tiznit>camargue"]; _L[_L.index(DATE("2028-02-12"))] = DATE("2028-02-07")
_add("tiznit>camargue", "Essaouira", DATE("2028-02-09"))
_add("tiznit>camargue", "Essaouira", ("Toubkal", "Winter ascent of North Africa's highest peak, 4,167 m, from Imlil", "N"))
_add("tiznit>camargue", "Essaouira", DATE("2028-02-13"))

# ---- Vuelta change (25 Oct 2026): Pärnu straight to Kraków, Sardinia dropped, Civitavecchia–Barcelona ferry ----
_T = {e[0]: e for v in H.values() for e in v if isinstance(e, tuple) and e[0] != "~DATE~"}
H["parnu>krakow"] = [_T[t] for t in ["Warsaw Old Town", "Łazienki Park", "Jasna Góra Monastery", "Ojców National Park"]]
H["matera>logrono"] = ([DATE("2027-09-18")] + [_T[t] for t in ["Amalfi Coast", "Pompeii", "Civita di Bagnoregio"]] + [FERRY, DATE("2027-09-22")] +
    [_T[t] for t in ["Sagrada Família", "Montserrat (mountain)", "Aigüestortes i Estany de Sant Maurici National Park",
                     "Ordesa y Monte Perdido National Park", "Castle of Loarre", "Bardenas Reales", "San Sebastián"]])
_j = _i("matera>logrono", "Sagrada Família"); _t, _c, _y = H["matera>logrono"][_j]
H["matera>logrono"][_j] = (_t, _c + "; then follow the last week of La Vuelta (22–26 Sep)", _y)
for _k in ("parnu>nida", "nida>krakow", "matera>barbagia", "barbagia>portotorres", "portotorres>logrono"): H.pop(_k, None)
for _k, _v in H.items():
    if _k in ("matera>logrono", "parnu>krakow"): continue
    for _j, _e in enumerate(_v):
        if isinstance(_e, tuple) and _e[0] == "~DATE~":
            if _e[1] < "2027-09-15": _v[_j] = DATE((_date.fromisoformat(_e[1]) - _td(days=2)).isoformat())
            elif "2027-09-28" < _e[1] < "2028-01-01": _v[_j] = DATE((_date.fromisoformat(_e[1]) - _td(days=13)).isoformat())

# ---- Rome added before the Civitavecchia ferry (25 Oct 2026) ----
H["matera>logrono"] = ([DATE("2027-09-16"), _T["Amalfi Coast"], _T["Pompeii"], DATE("2027-09-18"),
    ("Colosseum", "Colosseum and the Roman Forum", "H"), ("Pantheon, Rome", "2,000-year-old dome; Trevi and Piazza Navona nearby", "H"),
    ("St. Peter's Basilica", "Vatican: basilica, square and museums", "C"), DATE("2027-09-20"), _T["Civita di Bagnoregio"]] +
    H["matera>logrono"][H["matera>logrono"].index(FERRY):])

# ---- No time in Barcelona (25 Oct 2026): straight off the ferry ----
_L = H["matera>logrono"]; del _L[_i("matera>logrono", "Sagrada Família")]
_j = _i("matera>logrono", "Montserrat (mountain)"); _t, _c, _y = _L[_j]
_L[_j] = (_t, _c + "; then follow the last week of La Vuelta (22–26 Sep)", _y)

# ---- Marrakech dropped (already visited), 25 Oct 2026 ----
H["algeciras>merzouga"] = ([e for e in H["algeciras>toubkal"] if not (isinstance(e, tuple) and e[0] in ("Jemaa el-Fnaa", "Majorelle Garden"))]
                           + H["toubkal>merzouga"])
H.pop("algeciras>toubkal"); H.pop("toubkal>merzouga")

# ---- Dubrovnik for the last day of its Summer Festival (25 Aug); Ostrog moved after Kotor (25 Oct 2026) ----
_ost = _T["Ostrog Monastery"]
H["durmitor>kotor"] = [DATE("2027-08-25"), ("Dubrovnik", "Walled old town; Summer Festival on its last night (to 25 Aug)", "H"), _T["Perast"]]
H["kotor>shkodra"] = [e for e in H["kotor>shkodra"]] + [_ost]

# ---- Small festival changes (25 Oct 2026) ----
# 1. Zagori to 8 Sep for the Nativity feast
_pin("zagori>meteora", "Ioannina", "2027-09-09")
_cap("zagori>meteora", "Papingo", "Nativity village feast 7–8 Sep (Vradeto or Makrino)")
# 2. Asturias: Villaviciosa cider festival (about 8–12 Oct, odd years)
_add("picos>douro", "Cudillero", DATE("2027-10-08"))
_add("picos>douro", "Cudillero", ("Villaviciosa", "Cider town; Festival de la Manzana, early October in odd years", "C"))
_cap("picos>douro", "Roman walls of Lugo", "San Froilán fair (4–12 Oct)")
# 3. Portugal: Golegã 10–12 Nov (fair, São Martinho), Marvão 13–14 Nov (chestnut fair), Alcobaça 18 Nov (convent sweets fair)
_mv = {t: _T[t] for t in ("Marvão", "Castelo de Vide", "Alcobaça Monastery")}
H["douro>golega"] = [e for e in H["douro>golega"] if not (isinstance(e, tuple) and e[0] in _mv)]
_L = H["golega>algeciras"]
_L[0:0] = [DATE("2027-11-13"), (_mv["Marvão"][0], _mv["Marvão"][1] + "; chestnut fair (Festa do Castanheiro)", "P"),
           _mv["Castelo de Vide"], DATE("2027-11-18"),
           (_mv["Alcobaça Monastery"][0], _mv["Alcobaça Monastery"][1] + "; convent sweets and liqueurs fair", "H")]
# 4. Morocco: Zagora Sunday souk, Rissani Tuesday souk; Asni Saturday souk leaving Imlil
_pin("algeciras>merzouga", "Tamegroute", "2027-12-05")
_cap("algeciras>merzouga", "Tamegroute", "Zagora Sunday souk")
_pin("algeciras>merzouga", "Rissani", "2027-12-07")
_cap("algeciras>merzouga", "Rissani", "Tuesday souk")
_cap("tiznit>camargue", "Toubkal", "Asni Saturday souk on the way out (12 Feb)")
