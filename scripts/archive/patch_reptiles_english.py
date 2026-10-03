#!/usr/bin/env python3
"""
scripts/patch_reptiles_english.py
Bổ sung các trường tiếng Anh học thuật quốc tế (morphology_en, ecology_en, economic_value_en)
cho 6 loài bò sát biển trên Supabase, đưa tỷ lệ Audit lên 100% Complete.

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

PATCHES = {
    "casau-species-1": {
        "morphology_en": "Large head with a broad, elongated snout. A distinct pair of bony ridges runs from the eyes down the center of the snout (a key diagnostic trait distinguishing it from the Siamese crocodile). Upper jaw has 17-19 teeth on each side, lower jaw 14-15 teeth. The fourth mandibular tooth fits into an external notch in the upper jaw and remains visible when the mouth is closed. Dorsal surface is covered with heavy, non-overlapping scutes, with fewer bony osteoderms on the belly, making its belly hide prized in the leather trade. Coloration ranges from yellowish-tan with dark stripes in juveniles to dark olive-brown or almost black in large adults.",
        "ecology_en": "Habitat: Estuaries, mangrove swamps, brackish peat swamps, coastal lagoons, and open coastal waters, with an extraordinary capacity to navigate and swim hundreds of kilometers across open ocean. Diet: Apex predator of coastal and estuarine zones. Juveniles feed on insects, crustaceans, and small fish; adults prey on large mammals, sea turtles, fish, and birds. Reproduction: Oviparous; constructs large mound nests of vegetation and mud in secluded riverbanks and mangroves during the wet season, laying 40-70 eggs.",
        "economic_value_en": "Apex predator and key ecological indicator of mangrove health. High scientific value in paleontology and herpetology. Historically severely depleted by commercial hunting for the luxury exotic skin trade and persecution; now strictly protected under international and national law."
    },
    "ruabien-species-1": {
        "morphology_en": "Rounded head covered in horny scales; characterized by a single pair of prefrontal scales between the eyes (unlike other sea turtle species which have two pairs). Jaw is serrated with a flat, non-hooked beak adapted for grazing. Carapace is broad, smooth, and heart-shaped, typically dark olive, brown, or black with radiating streaks in adults; plastron is pale yellow or cream-colored. Adult carapace length ranges from 80 to 120 cm, weighing 100 to 200 kg.",
        "ecology_en": "Habitat: Coral reefs, seagrass meadows, coastal sandy beaches, and inshore waters. Diet: The only predominantly herbivorous sea turtle as an adult, feeding almost exclusively on marine seagrasses and macroalgae (such as Halophila, Thalassia, and Sargassum), while hatchlings and juveniles are omnivorous. Reproduction: Females return to natal nesting beaches every 2-4 years, laying clutches of 100-130 eggs in deep sand pits at night.",
        "economic_value_en": "Critical ecological keystone species responsible for grazing and maintaining the health of coastal seagrass meadows and nutrient recycling. High value for marine ecotourism. Strictly protected; illegal trade in meat, eggs, and shells is banned."
    },
    "ruabien-species-2": {
        "morphology_en": "Narrow, elongated head tapering to a prominent, sharply hooked beak resembling a bird of prey (hawk-like beak). Head possesses two pairs of prefrontal scales. Most distinct diagnostic feature: Carapace scutes strongly overlap (imbricate) like roof tiles (except in very old individuals). Carapace margins are distinctly serrated. Dorsal coloration is richly patterned with amber, gold, brown, and black marbling, known historically as 'tortoiseshell'.",
        "ecology_en": "Habitat: Closely associated with warm, shallow tropical coral reefs, lagoons, and rocky hard-bottom habitats at depths of 1-30 m. Diet: Highly specialized spongivore; feeds primarily on reef-dwelling sponges (Demospongiae), which are toxic to most other animals, as well as soft corals, sea anemones, and crustaceans. Reproduction: Breeds near coral reefs, laying 100-180 eggs per clutch on sandy coves and secluded beaches.",
        "economic_value_en": "Keystone species preventing aggressive sponges from outcompeting reef-building corals, thus safeguarding coral reef biodiversity. Historically driven to near-extinction by intense global trade in 'tortoiseshell' (bekko) for luxury jewelry and decorative crafts. Totally prohibited from commercial harvest."
    },
    "ruabien-species-3": {
        "morphology_en": "Carapace is broad, heart-shaped, and high-domed, uniformly dark olive-green. Key diagnostic trait: Carapace features 6 to 9 pairs of lateral (costal) scutes (often asymmetrical), far more than the 4-5 pairs found in other sea turtles. Head is triangular with two pairs of prefrontal scales. Smallest of the sea turtles found in Vietnamese waters, with adult carapace length of 60-75 cm and weighing 35-50 kg.",
        "ecology_en": "Habitat: Shallow coastal waters, bays, estuaries, and offshore neritic zones over muddy or sandy bottoms. Diet: Carnivorous and opportunistic; feeds on benthic invertebrates including crabs, shrimp, mollusks, jellyfish, tunicates, and small bottom fish. Reproduction: Renowned for massive synchronized mass-nesting events ('arribadas'), although in Vietnam nesting occurs predominantly as solitary, scattered events.",
        "economic_value_en": "Regulates benthic invertebrate populations on shallow coastal shelves. Highly vulnerable to incidental capture in bottom trawl nets, gillnets, and marine debris. Strictly protected by national biodiversity legislation."
    },
    "ruabien-species-4": {
        "morphology_en": "Most remarkable feature is its disproportionately large, broad head with powerful, heavily ossified jaws designed for crushing hard-shelled prey. Carapace is elongated, heart-shaped, with 5 pairs of costal scutes; reddish-brown in color, while the plastron is pale yellow. Possesses two pairs of prefrontal scales and two claws on each fore flipper. Adult carapace length typically spans 85-110 cm, weighing 80-160 kg.",
        "ecology_en": "Habitat: Oceanic pelagic waters during juvenile stages; adults inhabit coastal bays, lagoons, and offshore reefs, undertaking trans-oceanic migrations. Diet: Carnivorous; feeds predominantly on hard-shelled benthic organisms including large crabs, conchs, bivalves, sea urchins, and horseshoe crabs. Reproduction: Nests every 2-3 years, depositing multiple clutches of 100-120 eggs on open temperate and subtropical sandy beaches.",
        "economic_value_en": "Important biological indicator of open-ocean and shelf ecosystem integrity. Heavy declines caused by longline bycatch, degradation of nesting dunes, and marine plastic ingestion. Subject to strict commercial protection."
    },
    "ruabien-species-5": {
        "morphology_en": "Unique amongst living chelonians: lacks a bony shell and horny epidermal scutes. Instead, its carapace is composed of a tough, leathery, flexible skin embedded with thousands of tiny polygonal osteoderms, featuring seven prominent longitudinal ridges. Overall body is streamlined and spindle-shaped, dark grey or black with white or pink spotting. Fore flippers are exceptionally long, wing-like, and lack claws. Largest extant turtle and one of the heaviest living reptiles, reaching 1.5 - 2.2 m in total length and weighing 300 - 700 kg.",
        "ecology_en": "Habitat: High-seas pelagic ocean wanderer capable of tolerating near-freezing subpolar waters through gigantothermy and a specialized countercurrent circulatory system; dives to record depths exceeding 1,200 m. Diet: Highly specialized gelatinivore; feeds almost exclusively on jellyfish (Scyphozoa), salps, and other gelatinous pelagic organisms. Reproduction: Nests in tropical sandy beaches with deep-water oceanic approaches.",
        "economic_value_en": "Critical biological regulator of ocean jellyfish blooms, protecting commercial fish larvae from excessive gelatinous predation. Highly revered in Vietnamese maritime folk culture as 'Ông Khế' (sacred sea guardian). Critically endangered due to plastic bag ingestion (mistaken for jellyfish) and deep-sea longline entanglement."
    }
}

for sp_id, data in PATCHES.items():
    print(f"[*] Cập nhật bản dịch tiếng Anh cho {sp_id}...")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        method="PATCH"
    )
    with urllib.request.urlopen(req) as resp:
        print(f"  ✅ Thành công {sp_id}")

print("\n Hoàn tất cập nhật bản dịch tiếng Anh học thuật cho 6 loài bò sát biển!")
