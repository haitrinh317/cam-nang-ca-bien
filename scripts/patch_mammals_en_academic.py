#!/usr/bin/env python3
"""
scripts/patch_mammals_en_academic.py
Bổ sung các trường tiếng Anh học thuật quốc tế (morphology_en, ecology_en, economic_value_en)
cho 34 loài Thú biển Việt Nam (thu-bien) trên Supabase, đưa tỷ lệ Audit lên 100% Complete.

Tác giả: Antigravity Assistant cho chú Chình
Ngày thực hiện: 13/09/2026
"""

import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

ACADEMIC_EN_DATA = {
    "thubien-species-1": {
        "morphology_en": "Fusiform body tapering to a horizontally flattened, fluked tail resembling that of cetaceans. Forelimbs modified into paddle-like flippers lacking nails. Thick, smooth skin brownish-grey dorsally and paler ventrally, covered with sparse sensory bristles. The head is large with a sharply downturned, horseshoe-shaped muscular snout and sensitive bristles adapted for benthic grazing. Adults reach 2.5 - 3.2 m in length and weigh 250 - 450 kg.",
        "ecology_en": "Habitat: Sheltered shallow bays, mangrove channels, and coastal lagoons with extensive seagrass beds. Diet: Strictly herbivorous; feeds almost exclusively on marine seagrasses (genera Halophila, Halodule, Cymodocea). Reproduction: Monogamous or solitary; slow reproductive rate with gestation of 13-15 months, giving birth to a single calf nursed for up to 18 months.",
        "economic_value_en": "Highest conservation priority in Vietnam; revered as a flagship species for marine biodiversity. Listed in CITES Appendix I, Vietnam Red Data Book (CR), and strictly protected under national law. Historically threatened by seagrass loss, entanglement in gillnets, and coastal development."
    },
    "thubien-species-2": {
        "morphology_en": "Streamlined rorqual characterized by three prominent longitudinal ridges on the dorsal surface of the rostrum (one central and two lateral ridges), a definitive diagnostic trait. Body is dark smoky grey dorsally and white or yellowish ventrally. Dorsal fin is falcate and pointed, located about two-thirds back on the body. Possesses 40-70 ventral throat grooves extending past the umbilicus. Adult length ranges from 12 to 15 m, weighing 15 to 25 tonnes.",
        "ecology_en": "Habitat: Coastal and shelf waters of tropical and warm-temperate seas, frequently observed foraging in bays and along coastal upwelling zones such as De Gi (Binh Dinh, Vietnam). Diet: Feeds on small schooling pelagic fish (anchovies, sardines, herrings) and swarming planktonic crustaceans. Reproduction: Breeds year-round in warm tropical waters; gestation lasts approximately 11-12 months.",
        "economic_value_en": "Central cultural emblem in Vietnamese maritime heritage, venerated as 'Ca Ong' (Lord Whale) and enshrined in coastal Lang Ong temples. Strictly protected under CITES Appendix I and Decree 26/2019/ND-CP. Key attraction for responsible marine ecotourism."
    },
    "thubien-species-3": {
        "morphology_en": "The largest animal ever known to have lived, with a long, slender body that appears mottled bluish-grey when submerged and slate grey at the surface. Rostrum is broad, flat, and U-shaped with a single prominent median ridge. Dorsal fin is diminutive (up to 35 cm) and set far back on the caudal peduncle. Ventral grooves number 60 to 90, extending to the navel. Baleen plates are uniformly black. Adults can reach 24 to 30 m in length and weigh up to 150-180 tonnes.",
        "ecology_en": "Habitat: Open oceanic waters, undertaking extensive seasonal migrations between polar feeding grounds and tropical breeding areas. Dives to depths of 100-500 m. Diet: Strictly stenophagous on swarming euphausiid krill, consuming up to 4 tonnes per day through bulk lunging. Reproduction: Calving takes place in warm tropical waters during winter after 10-12 months gestation.",
        "economic_value_en": "Global conservation flagship species. Highly revered in Vietnamese maritime history, with monumental skeletal remains preserved and worshipped in coastal Lang Ong Nam Hai shrines. Critically endangered by ship strikes and ocean noise pollution."
    },
    "thubien-species-4": {
        "morphology_en": "Second largest whale species, recognized by its exceptionally sleek, streamlined body and unique asymmetrical head coloration: the right lower jaw and right anterior baleen are white, while the left side is dark slate grey. Head is V-shaped with a sharp median ridge. Dorsal fin is relatively tall (up to 60 cm) and falcate, located three-quarters back on the body. Length spans 19 to 24 m, weighing 45 to 75 tonnes.",
        "ecology_en": "Habitat: Primarily deep offshore and pelagic temperate to tropical waters. Known as the 'greyhound of the sea' due to sustained swimming speeds up to 37 km/h. Diet: Opportunistic feeder on krill, squid, and schooling fish (capelin, herring, mackerel). Reproduction: Migrates seasonally, calving every 2-3 years in warm wintering zones.",
        "economic_value_en": "High scientific and phylogenetic significance. Ancient bones held in coastal whale temples across central Vietnam. Listed in CITES Appendix I and IUCN Red List (EN); fully protected against commercial exploitation."
    },
    "thubien-species-5": {
        "morphology_en": "Sleek, robust body with dark bluish-grey to charcoal coloration dorsally, often marked with light circular scars caused by cookiecutter shark bites; underside is pale grey to white. Single prominent longitudinal rostral ridge. Dorsal fin is large, falcate, and erect (25-60 cm high), rising at a steeper angle than in other rorquals. Baleen plates are dark with fine, curly white bristles. Length averages 14 to 18 m, weighing 15 to 20 tonnes.",
        "ecology_en": "Habitat: Deep offshore oceanic waters, rarely entering shallow coastal seas or bays. Avoids polar ice edges, preferring temperate and subtropical zones. Diet: Skim-feeder specializing in copepods, euphausiids, and small schooling fish. Reproduction: Winters in warm tropical seas with calves born after an 11-month gestation period.",
        "economic_value_en": "Subject to strict international and national conservation measures under CITES Appendix I. Vulnerable to collisions with commercial cargo vessels along deep-sea shipping lanes in the South China Sea."
    },
    "thubien-species-6": {
        "morphology_en": "Smallest and most common baleen whale in the Northern Hemisphere. Distinguished by an exceptionally pointed, triangular snout with a single sharp rostral ridge, and a bright white transverse band across the middle of each dark pectoral flipper. Dorsal fin is tall, falcate, and placed far back. Ventral grooves number 50-70, ending before the umbilicus. Adult length spans 7 to 9 m, weighing 5 to 9 tonnes.",
        "ecology_en": "Habitat: Highly adaptable, inhabiting both shallow coastal inshore bays, estuaries, and deep pelagic waters. Diet: Broad opportunistic diet including small schooling fish (anchovies, sardines, herring) and krill. Reproduction: Breeds in warm waters during winter; calving occurs annually or biennially.",
        "economic_value_en": "Significant ecological role as a small baleen predator in coastal marine food webs. Honored in Vietnamese folk fishing culture. Listed in CITES Appendix I and protected under the Vietnamese Fisheries Law."
    },
    "thubien-species-7": {
        "morphology_en": "Dwarf rorqual species formally described in 2003. Morphologically resembles a miniature fin whale, featuring asymmetrical head coloration (left side dark, right side pale), but differs in possessing a single rostral ridge, unique skull morphology, and a small falcate dorsal fin. Fewer ventral grooves (about 80-90) that extend past the navel. Adults reach 9.6 to 11.5 m in length and weigh approximately 4 to 8 tonnes.",
        "ecology_en": "Habitat: Coastal and shelf waters of the Indo-Pacific tropical and subtropical belt, including confirmed records from the central and southern coasts of Vietnam. Non-migratory or undertaking localized seasonal movements. Diet: Schooling pelagic fish and krill. Reproduction: Poorly known; believed to breed in tropical waters year-round.",
        "economic_value_en": "High taxonomic and evolutionary interest due to its recent scientific recognition. Skeletal specimens preserved in Vietnamese whale shrines provide vital genetic material for global cetacean systematics."
    },
    "thubien-species-8": {
        "morphology_en": "Stocky body easily identified by its extremely long pectoral flippers (up to one-third of total body length) with scalloped leading edges, and fleshy tubercles (knobs) on the head and lower jaw. Dorsal fin rests on a distinct fleshy hump. Flukes have jagged trailing edges and unique black-and-white ventral patterns used for photo-identification. Adults reach 13 to 16 m and weigh 25 to 35 tonnes.",
        "ecology_en": "Habitat: Coastal waters, island archipelagoes, and open oceans. Famous for complex vocal 'songs' and acrobatic breaching behavior. Diet: Feeds via bubble-net feeding on krill, capelin, and small schooling fish in high-latitude waters. Reproduction: Migrates thousands of kilometers to tropical coral reef zones to calve and mate.",
        "economic_value_en": "Global symbol of whale conservation and prime target for sustainable ecotourism. Recorded in coastal folklore and whale temples across central Vietnam. Protected under CITES Appendix I."
    },
    "thubien-species-9": {
        "morphology_en": "Heavy-set body covered in mottled grey-white patches caused by extensive colonies of barnacles (Cryptolepas rhachianecti) and whale lice (Cyamus). Lacks a dorsal fin, possessing instead a low dorsal hump followed by 6-12 dorsal knuckles (crests) along the caudal ridge. Throat has 2-4 short, deep creases. Rostrum is narrow and arched. Adults reach 12 to 14 m and weigh 20 to 35 tonnes.",
        "ecology_en": "Habitat: Shallow continental shelf waters; the only large baleen whale specialized in benthic suction feeding. Diet: Feeds by scooping sediment from the sea floor to filter amphipods, polychaetes, and ghost shrimp. Reproduction: Western North Pacific population undertakes migrations along the East Asian coast.",
        "economic_value_en": "The Western North Pacific gray whale subpopulation is one of the world's most critically endangered cetacean groups. Historical bone specimens in Vietnamese whale shrines document ancient migratory routes."
    },
    "thubien-species-10": {
        "morphology_en": "The largest toothed whale, unmistakable by its massive, laterally compressed, rectangular head that constitutes up to one-third of its total body length. Houses the spermaceti organ. Lower jaw is narrow and undershot, lined with 18-26 pairs of large conical teeth fitting into sockets in the toothless upper jaw. Blowhole is S-shaped and positioned far forward on the left side of the snout. Wrinkled, prune-like skin; lacks a true dorsal fin, having a triangular dorsal hump followed by knuckles. Adult males reach 16-18 m (up to 50 tonnes); females 11-12 m (up to 15 tonnes).",
        "ecology_en": "Habitat: Deep oceanic waters, submarine canyons, and oceanic trenches along continental slopes (>1,000 m). Champion deep-diver, routinely reaching depths of 1,000 to 2,500 m for up to 90 minutes. Diet: Feeds primarily on giant and colossal squid (Architeuthis, Histioteuthis) and deep-sea demersal fish. Reproduction: Matriarchal social units of adult females and calves; mature males live solitary lives in higher latitudes.",
        "economic_value_en": "Monumental cultural icon in coastal Vietnamese fishing traditions ('Ca Voi Ong'). Massive jaws and vertebrae enshrined in coastal Lang Ong temples. Strictly protected under CITES Appendix I and national wildlife laws."
    },
    "thubien-species-11": {
        "morphology_en": "Small, robust body superficially resembling a shark due to its undershot lower jaw, false gill slit marking (crescent-shaped pale patch on each side behind the eye), and blunt, squarish snout. Dorsal fin is small, falcate, and located behind the midpoint of the back. Lower jaw possesses 12 to 16 pairs of sharp, curved teeth. Adult length ranges from 3.0 to 3.8 m, weighing 300 to 450 kg.",
        "ecology_en": "Habitat: Deep tropical and warm-temperate waters over continental shelves and ocean basins. Inconspicuous at the surface, often floating motionless ('logging'). Diet: Preys on cephalopods, deep-sea fish, and decapod crabs. Releases a reddish-brown intestinal 'ink' fluid when startled to evade predators.",
        "economic_value_en": "Scientific and educational value. Regularly recorded stranded on the beaches of central Vietnam (Binh Thuan, Da Nang). Protected under CITES Appendix II."
    },
    "thubien-species-12": {
        "morphology_en": "Closely resembles the pygmy sperm whale but smaller in stature, with a taller, more erect, dolphin-like dorsal fin positioned near the middle of the back. Snout is slightly more pointed. Possesses 7 to 12 pairs of sharp mandibular teeth, occasionally with 1-3 vestigial maxillary teeth. False gill marking present behind each eye. Adult length spans 2.1 to 2.7 m, weighing 150 to 250 kg.",
        "ecology_en": "Habitat: Pelagic and continental slope waters in tropical and warm-temperate seas, generally closer to shore than K. breviceps. Diet: Feeds mainly on squids, cuttlefish, and benthic crustaceans. Solitary or in small pods of 2-4 individuals.",
        "economic_value_en": "Subject to international trade monitoring under CITES Appendix II. Stranding data in Vietnam provides essential morphological and diet records for deep-sea research."
    },
    "thubien-species-13": {
        "morphology_en": "Robust, cigar-shaped body with a short, indistinct beak and a concave forehead that becomes white in mature adult males. Lower jaw extends slightly beyond the upper jaw, bearing a single pair of robust, conical teeth at the tip (erupted only in adult males). Small falcate dorsal fin situated two-thirds back along the body. Adult length ranges from 5.5 to 7.0 m, weighing 2.5 to 3.5 tonnes.",
        "ecology_en": "Habitat: Deep pelagic waters, oceanic trenches, and steep submarine canyons. Holds the mammalian record for dive depth (2,992 m) and dive duration (222 minutes). Diet: Specialized predator of deep-sea cephalopods and benthopelagic fish. Reproduction: Poorly known; calves born in oceanic waters.",
        "economic_value_en": "Extreme vulnerability to military active mid-frequency sonar, which triggers mass-stranding events. Protected under CITES Appendix II; cranial specimens conserved in marine collections in Vietnam."
    },
    "thubien-species-14": {
        "morphology_en": "Medium-sized beaked whale characterized by highly elevated, arched lower jaws (mandibles) resembling massive crests in adult males, from which a single pair of large, flattened tusks projects above the snout. Beak is short and stout. Coloration is dark brownish-blue with extensive scarring. Dorsal fin is small and falcate. Adults measure 4.2 to 4.7 m, weighing around 1,000 kg.",
        "ecology_en": "Habitat: Deep tropical and subtropical oceanic waters worldwide. Diet: Preys on squid, lanternfish, and other mesopelagic organisms during deep foraging dives. Social structure consists of small groups of 3-7 individuals.",
        "economic_value_en": "Valuable osteological specimens documented in Vietnamese coastal whale temples. Protected under CITES Appendix II."
    },
    "thubien-species-15": {
        "morphology_en": "Similar in general body shape to other mesoplodonts, but adult males are distinguished by a pair of wide, laterally compressed teeth shaped like the leaf of the maidenhair tree (Ginkgo biloba), positioned midway along the arched lower jaw. Body is dark blue-grey with faint white spotting. Adults attain lengths of 4.5 to 5.3 m and weights of 1.5 to 2.0 tonnes.",
        "ecology_en": "Habitat: Confined primarily to the tropical and warm-temperate waters of the Indo-Pacific. Elusive pelagic habitant with few live sightings. Diet: Mesopelagic squid and benthic fish captured through suction feeding.",
        "economic_value_en": "Very rare cetacean; specimens held in Lang Ong shrines along the south-central coast of Vietnam represent globally significant distribution records. CITES Appendix II."
    },
    "thubien-species-16": {
        "morphology_en": "Large beaked whale with a long, robust body, bulbous melon, and a long, prominent dolphin-like tubular beak. Adults have a relatively large, falcate dorsal fin and a striking colour pattern ranging from dark grey to brownish-yellow with a pale throat. Two teeth at the tip of the lower jaw in adult males. Length reaches 6.0 to 7.5 m, weighing 3.5 to 4.5 tonnes.",
        "ecology_en": "Habitat: Open tropical and subtropical waters of the Indo-Pacific. Known historically from only a handful of skulls, including historic material from Vietnam. Diet: Deep-water squids and fishes.",
        "economic_value_en": "One of the rarest large mammals on Earth. Enshrined skeletal remains in Vietnamese maritime heritage sites provide critical scientific confirmation of its presence in the South China Sea."
    },
    "thubien-species-17": {
        "morphology_en": "Small, blunt-headed porpoise completely lacking a dorsal fin, featuring instead a low, narrow dorsal ridge covered with sensory tubercles (warts) on the back. Head is rounded with a forehead that rises steeply from the snout; lacks a beak. Spatulate, spade-shaped teeth (unlike the conical teeth of dolphins). Coloration is uniform slate grey. Adult length spans 1.4 to 1.9 m, weighing 40 to 65 kg.",
        "ecology_en": "Habitat: Shallow coastal waters, sheltered bays, estuaries, mangrove channels, and sandy beaches within 5 km of the coast. Diet: Opportunistic feeder on coastal fish, prawns, and small squids. Reproduction: Calves born in spring and early summer; high reproductive investment.",
        "economic_value_en": "Venerated by coastal communities in Vietnam as 'Ca Ong Su' or 'Ca Nuoc Chuot'. Highly endangered due to incidental bycatch in gillnets and bottom trawls. CITES Appendix I."
    },
    "thubien-species-18": {
        "morphology_en": "Similar to the Indo-Pacific finless porpoise but possesses a narrower dorsal tuberculated ridge (typically only 0.2-1.2 cm wide) that begins further forward on the back. Body is dark charcoal to slate grey. Adults reach 1.5 to 2.0 m in length and weigh 40 to 70 kg.",
        "ecology_en": "Habitat: Coastal waters, large river estuaries, and tidal zones in East Asia, extending into the northern Gulf of Tonkin (Vietnam). Diet: Coastal bottom fish, shrimps, and squids.",
        "economic_value_en": "Critically endangered across its global range. Protected under CITES Appendix I and priority national conservation programs."
    },
    "thubien-species-19": {
        "morphology_en": "Stout body with a distinctive fleshy hump on the back supporting a small, falcate dorsal fin. Long, well-defined slender beak. Coloration changes dramatically with age: calves are born dark slate grey, becoming mottled pinkish-white as juveniles, and turning nearly pure ivory-white or bubblegum-pink as adults due to blood vessel flushing. Adults measure 2.4 to 2.8 m, weighing 200 to 280 kg.",
        "ecology_en": "Habitat: Strictly estuarine and inshore coastal waters, bays, and mangrove zones, especially near river mouths (Ha Long Bay, Bai Tu Long, Mekong Delta, Phu Quoc). Diet: Schooling coastal and estuarine fish (mullet, croakers, anchovies).",
        "economic_value_en": "World-famous 'pink dolphin', flagship species for coastal conservation in Vietnam and East Asia. Severely threatened by habitat reclamation, pollution, and gillnet bycatch. CITES Appendix I."
    },
    "thubien-species-20": {
        "morphology_en": "Distinctive cetacean with a blunt, rounded head, bulbous forehead, and no beak. Mouthline is upturned in a permanent 'smile'. Possesses a small, rounded dorsal fin located behind the midpoint of the back. Pectoral flippers are broad and paddle-shaped. U-shaped blowhole on the left side. Adult length spans 2.1 to 2.6 m, weighing 100 to 140 kg.",
        "ecology_en": "Habitat: Coastal waters, sheltered bays, mangrove estuaries, and major tropical river systems (Mekong River basin, Kien Giang, Ba Ria-Vung Tau). Diet: Fish, cephalopods, and decapod crustaceans. Unique behavior of spitting water to herd fish.",
        "economic_value_en": "Known affectionately in Vietnam as 'Ca Nuoc Minh Hai'. Critically endangered in Vietnamese waters due to river dams, gillnets, and electrofishing. Strictly protected under CITES Appendix I."
    },
    "thubien-species-21": {
        "morphology_en": "Robust body with a moderately long, slender beak and a tall, falcate dorsal fin. Diagnostic trait: adult individuals develop conspicuous dark spots on the lower belly and sides. Body is dark grey dorsally and pale grey to pinkish ventrally. Adult length spans 2.3 to 2.6 m, weighing 160 to 230 kg.",
        "ecology_en": "Habitat: Inshore coastal waters, coral reefs, lagoons, and rocky island shores (Phu Quy, Con Dao, Cham Islands). Diet: Benthic and reef-associated fish and squids. Social groups range from 5 to 15 individuals.",
        "economic_value_en": "High ecotourism value for boat-based dolphin watching in marine protected areas (MPAs). CITES Appendix II."
    },
    "thubien-species-22": {
        "morphology_en": "Large, sturdy body with a short, stout beak sharply demarcated from the melon by a crease. Tall, falcate dorsal fin set near the midpoint of the back. Unspotted belly; dark charcoal grey dorsally, shading to light grey on the sides and white or pink on the belly. Adult length ranges from 2.5 to 3.8 m, weighing 250 to 500 kg.",
        "ecology_en": "Habitat: Wide range of marine habitats, from shallow coastal bays to deep pelagic open ocean. Highly intelligent, adaptable, and acrobatic. Diet: Broad spectrum of teleost fish, cephalopods, and rays.",
        "economic_value_en": "The most widely recognized cetacean species. Protected under CITES Appendix II and fisheries legislation."
    },
    "thubien-species-23": {
        "morphology_en": "Slender, streamlined body with a long, thin beak tip that is white. Adults are covered with a dense pattern of white spots on their dark dorsal cape, and dark spots on their pale belly. Prominent dark band extends from flipper to eye. Narrow, falcate dorsal fin. Adults reach 1.8 to 2.3 m and weigh 80 to 120 kg.",
        "ecology_en": "Habitat: Pelagic tropical and subtropical oceans. Often associates in massive multi-species schools with yellowfin tuna and spinner dolphins. Diet: Flying fish, squids, and lanternfish.",
        "economic_value_en": "Historical vulnerability to tuna purse-seine nets; subject to international dolphin-safe fishing standards. CITES Appendix II."
    },
    "thubien-species-24": {
        "morphology_en": "Very slender body with an exceptionally long, thin beak and a distinctive triangular to slightly forward-canted dorsal fin. Three-part color pattern: dark grey cape, lighter grey sides, and white/pink belly. World-renowned for spinning around its longitudinal axis up to seven times during aerial leaps. Adult length spans 1.7 to 2.1 m, weighing 55 to 80 kg.",
        "ecology_en": "Habitat: Pelagic tropical waters by night; rests in sheltered coastal bays and lagoons (e.g., Con Dao, Phu Quy) by day. Diet: Mesopelagic squids, shrimps, and small fishes.",
        "economic_value_en": "Iconic ecotourism spectacle. Protected in Vietnamese waters under CITES Appendix II."
    },
    "thubien-species-25": {
        "morphology_en": "Streamlined body with a striking, complex coloration: dark bluish-grey dorsal cape, white belly, and distinct dark stripes running from the eye to the anus and from the eye to the flipper. Light blaze extends upward towards the dorsal fin. Adults measure 2.0 to 2.5 m, weighing 90 to 150 kg.",
        "ecology_en": "Habitat: Deep offshore waters and oceanic margins. Travels in large, active pods of hundreds of individuals. Diet: Cephalopods, myctophids, and small schooling fish.",
        "economic_value_en": "Subject to CITES Appendix II trade regulations. Indicator of oceanic health and pelagic prey abundance."
    },
    "thubien-species-26": {
        "morphology_en": "Distinctive profile: conical head and long beak without a crease separating it from the melon. Teeth have fine vertical wrinkles or ridges (hence 'rough-toothed'). Dark purplish-grey body with irregular yellowish-white blotches and scars. Adults reach 2.2 to 2.6 m, weighing 100 to 150 kg.",
        "ecology_en": "Habitat: Deep tropical offshore waters and around oceanic islands. Diet: Large fish (mahi-mahi, needlefish) and pelagic squids.",
        "economic_value_en": "Recorded in central Vietnamese whale shrines ('Ca Ong'). Protected under CITES Appendix II."
    },
    "thubien-species-27": {
        "morphology_en": "Robust body with a bulbous, blunt head featuring a unique vertical median crease on the front of the melon; lacks a distinct beak. Body is heavily scarred with white linear scratches caused by squid bites and social interactions, turning older animals nearly white. Tall, falcate dorsal fin (up to 50 cm). Adults measure 3.0 to 3.8 m, weighing 300 to 500 kg.",
        "ecology_en": "Habitat: Continental shelf slopes and deep offshore trenches (400 - 1,000 m). Diet: Specialized nocturnal feeder on mesopelagic cephalopods (squid, octopus).",
        "economic_value_en": "Important deep-sea predator. Enshrined in traditional coastal Lang Ong temples in Vietnam. CITES Appendix II."
    },
    "thubien-species-28": {
        "morphology_en": "Stocky body with very short, pointed beak, small pointed flippers, and a small falcate dorsal fin. Striking coloration: dark grey cape, creamy white belly, and a prominent dark lateral stripe extending from the eye to the anus. Adults reach 2.2 to 2.6 m, weighing 140 to 210 kg.",
        "ecology_en": "Habitat: Deep oceanic waters beyond the continental shelf edge. Highly gregarious, moving in fast-swimming herds of 100 to 500 individuals. Diet: Deep-sea squids, crustaceans, and myctophid fish.",
        "economic_value_en": "Infrequent sightings in coastal waters; vital component of pelagic marine biodiversity. CITES Appendix II."
    },
    "thubien-species-29": {
        "morphology_en": "Large, robust body with a bulbous, squarish melon and a very broad-based, low falcate dorsal fin set far forward on the body. Flippers are sickle-shaped, measuring about one-sixth of body length. Black or dark charcoal with a faint anchor-shaped grey patch on the throat. Adult males reach 5.5 to 7.0 m (up to 3.5 tonnes); females 4.0 to 5.5 m.",
        "ecology_en": "Habitat: Deep waters over continental slopes and oceanic areas. Strong matriarchal social structure led by post-reproductive females. Diet: Primarily deep-water squid ('cheetahs of the deep' due to high-speed foraging sprints at depth).",
        "economic_value_en": "High susceptibility to mass stranding due to close social bonds. Honored as 'Ca Ong Tieu' in Vietnamese fishing villages. CITES Appendix II."
    },
    "thubien-species-30": {
        "morphology_en": "Slender, all-black or dark grey body with a slender, tapered head without a beak. Pectoral flippers have an S-shaped leading edge forming a prominent elbow-like hump (definitive diagnostic feature). Pointed falcate dorsal fin. Large conical teeth (8-11 in each jaw). Adult length spans 5.0 to 6.0 m, weighing 1.2 to 2.0 tonnes.",
        "ecology_en": "Habitat: Warm tropical and subtropical pelagic waters. Known to hunt in cooperative packs for large fish (tuna, swordfish, mahi-mahi) and occasionally other small cetaceans. Diet: Pelagic fish and cephalopods.",
        "economic_value_en": "Apex predator. Frequently interacts with longline fisheries. Revered and buried with honors in coastal Lang Ong shrines in Vietnam. CITES Appendix II."
    },
    "thubien-species-31": {
        "morphology_en": "The largest dolphin and the ocean's ultimate apex predator. Robust, streamlined black body with stark white patches behind each eye, under the jaw, and on the lower belly; grey saddle patch behind the dorsal fin. Pectoral flippers are broad and paddle-shaped. Adult males feature an erect, triangular dorsal fin up to 1.8 m high; females have a smaller falcate fin (up to 0.9 m). Males reach 7.5 to 9.0 m (up to 6 tonnes); females 6.5 to 7.5 m (up to 4 tonnes).",
        "ecology_en": "Habitat: Found in all oceans from ice edges to warm tropical seas, including sporadic sightings in offshore waters of the South China Sea. Highly sophisticated matriarchal pods with dialect-specific acoustic repertoires. Diet: Opportunistic apex predator feeding on fish, squids, sea turtles, seabirds, and marine mammals.",
        "economic_value_en": "Global conservation and cultural icon. Revered in Vietnamese folklore as 'Ca Kinh' (sacred warrior of the sea). Listed in CITES Appendix II and strictly protected under Vietnamese law."
    },
    "thubien-species-32": {
        "morphology_en": "Small, slender body with a rounded head lacking a beak. Pectoral flippers have rounded tips. Body is dark grey to black with white or pink margins around the lips and a diffuse white ventral patch. Possesses 8-11 pairs of teeth in upper jaw, 11-13 in lower jaw. Adult length reaches 2.1 to 2.4 m, weighing 110 to 170 kg.",
        "ecology_en": "Habitat: Deep tropical and subtropical oceanic waters worldwide. Shy, elusive, and rarely encountered. Diet: Small pelagic fish, squids, and occasionally other small dolphins.",
        "economic_value_en": "Rare cetacean species. Scientific records in Vietnam depend heavily on specimen identification from coastal strandings. CITES Appendix II."
    },
    "thubien-species-33": {
        "morphology_en": "Triangular head with a pointed snout and no distinct beak, tapering sharply from the eyes forward (melon-headed appearance). Faint white borders on the lips. Body is charcoal grey with a dark dorsal cape. Long, sharply pointed flippers and a tall, falcate dorsal fin. Adults reach 2.5 to 2.8 m and weigh 200 to 275 kg.",
        "ecology_en": "Habitat: Deep tropical oceanic waters worldwide. Forms large, tightly packed pods of 100 to 1,000 individuals, often resting at the surface. Diet: Mesopelagic fish and squids.",
        "economic_value_en": "Prone to mass-stranding events. Documented in coastal folklore as 'Ca Voi Bau Dot'. Protected under CITES Appendix II."
    },
    "thubien-species-34": {
        "morphology_en": "Slender, colorful dolphin with a moderately long, slender beak and an hour-glass pattern (figure-eight) on its flanks: yellowish-tan thoracic patch anteriorly and light grey flank patch posteriorly. Dorsal fin is tall and falcate. Each jaw has 40 to 55 pairs of small, sharp conical teeth. Adult length ranges from 1.8 to 2.4 m, weighing 75 to 130 kg.",
        "ecology_en": "Habitat: Pelagic and coastal waters in warm-temperate and tropical oceans. Extremely fast, acrobatic swimmers that frequently bow-ride and leap in unison. Diet: Small schooling fish (anchovies, sardines) and squids.",
        "economic_value_en": "Ecological sentinel of coastal marine productivity. Protected under CITES Appendix II and fisheries conservation regulations."
    }
}

def main():
    print("=" * 80)
    print("🐋 BỔ SUNG 100% TIẾNG ANH HỌC THUẬT QUỐC TẾ (SMM STANDARDS)")
    print("   CHO TOÀN BỘ 34 LOÀI THÚ BIỂN VIỆT NAM (thu-bien)")
    print("=" * 80)

    updated = 0
    errors = 0

    for sid, data in ACADEMIC_EN_DATA.items():
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sid}"
        req = urllib.request.Request(
            patch_url,
            data=json.dumps(data).encode("utf-8"),
            headers=HEADERS,
            method="PATCH"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
                print(f"  ✓ [{sid}] Đã bổ sung morphology_en, ecology_en, economic_value_en")
                updated += 1
        except Exception as e:
            print(f"  ✗ [{sid}] Lỗi: {e}")
            errors += 1

    print("=" * 80)
    print(f"📊 TỔNG KẾT: Đã cập nhật thành công {updated}/34 loài Thú biển!")
    if errors > 0:
        print(f"⚠️ Có {errors} lỗi xảy ra.")
    print("=" * 80)

if __name__ == "__main__":
    main()
