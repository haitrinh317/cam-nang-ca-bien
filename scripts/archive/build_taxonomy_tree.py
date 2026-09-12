import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

species_file = r"e:\2026\_Antigravity\OCR Document\data\species.json"
output_file = r"e:\2026\_Antigravity\OCR Document\data\taxonomy_tree.json"
public_output_file = r"e:\2026\_Antigravity\OCR Document\public\data\taxonomy_tree.json"

with open(species_file, "r", encoding="utf-8") as f:
    species_list = json.load(f)

def clean_latin_name(name):
    if not name: return ""
    name = re.sub(r"[^\w\s\-\.,&]", "", name)
    return re.sub(r'\s+', ' ', name).strip()

def clean_vn_name(name):
    if not name: return ""
    # Remove text in parentheses like (Order Dasyatiformes)
    name = re.sub(r'\(.*?\)', '', name)
    # Remove latin order names if accidentally included in VN string
    name = re.sub(r'[A-Z][a-z]+iformes\b', '', name)
    name = re.sub(r"[^\w\s\-\.,&]", "", name)
    return re.sub(r'\s+', ' ', name).strip()

def clean_genus_vn(vn, latin):
    if not vn:
        return f"Giống {latin.split()[0]}"
    if ":" in vn:
        vn = vn.split(":")[-1].strip()
    
    genus_word = latin.split()[0]
    # Remove the scientific genus name and anything after it (like author names)
    vn = re.sub(rf'\b{genus_word}\b.*', '', vn, flags=re.IGNORECASE).strip()
    
    vn = clean_vn_name(vn)
    
    if not vn:
        vn = f"Cá {genus_word.lower()}"
    if not vn.startswith("Giống"):
        vn = f"Giống {vn}"
    return vn

def clean_family_vn(vn):
    if not vn:
        return ""
    if ":" in vn:
        vn = vn.split(":")[-1].strip()
    
    # Remove latin family names (ending in idae) and anything after
    vn = re.sub(r'\b[A-Z][a-z]+idae\b.*', '', vn, flags=re.IGNORECASE).strip()
    
    vn = clean_vn_name(vn)
    return vn

# Map order to biological class
def get_class_for_order(order_latin):
    if not order_latin:
        return "Cá Xương", "Osteichthyes"
    order_lower = str(order_latin).lower().strip()    # Class Leptocardii (Lớp Cá Lưỡng Tiêm)
    if "amphioxiformes" in order_lower:
        return "Lớp Cá Lưỡng Tiêm", "Leptocardii"
    # Class Chondrichthyes (Lớp Cá Sụn)
    sụn_orders = [
        "lamniformes", "squaliformes", "rajiformes", "torpediniformes", 
        "pristiophoriformes", "heterodontiformes", "hexanchiformes", 
        "orectolobiformes", "carcharhiniformes", "dasyatiformes"
    ]
    if any(o in order_lower for o in sụn_orders):
        return "Lớp Cá Sụn", "Chondrichthyes"
    # Class Osteichthyes (Lớp Cá Xương)
    return "Lớp Cá Xương", "Osteichthyes"

# Hierarchical Tree Structure
# tree = { class_latin: { order_latin: { family_latin: { genus_latin: [species] } } } }
tree_dict = {}

for sp in species_list:
    # Resolve Class
    taxo = sp.get("taxonomy") or {}
    order_data = taxo.get("order") or {}
    order_vn = order_data.get("vn") or "Cá Vược"
    order_lat = order_data.get("latin") or "Perciformes"
    
    class_vn, class_lat = get_class_for_order(order_lat)
    
    # Resolve Order
    order_vn = clean_vn_name(order_vn)
    if not order_vn.startswith("Bộ"):
        order_vn = f"Bộ {order_vn}"
    order_lat = clean_latin_name(order_lat)
    
    # Resolve Family
    family_data = taxo.get("family") or {}
    fam_vn = clean_family_vn(family_data.get("vn") or "")
    fam_lat = clean_latin_name(family_data.get("latin") or "")
    if not fam_vn.startswith("Họ"):
        fam_vn = f"Họ {fam_vn}"
        
    # Resolve Genus
    genus_data = taxo.get("genus") or {}
    gen_vn = genus_data.get("vn") or ""
    gen_lat = genus_data.get("latin") or ""
    gen_lat_clean = gen_lat.split()[0] if gen_lat else "Unknown"
    gen_vn = clean_genus_vn(gen_vn, gen_lat_clean)
    
    # Species data
    sp_data = {
        "id": sp["id"],
        "volume": sp.get("volume", 0),
        "page": sp.get("page", ""),
        "speciesIndex": sp.get("speciesIndex", 0),
        "vnName": sp.get("vnName") or (sp.get("specs", {}).get("vn", {}).get("alternateNames", "")) or "Cá",
        "scientificName": sp.get("scientificName", ""),
        "authorship": sp.get("authorship", ""),
        "status": sp.get("status", "")
    }
    
    # Insert into nested dict
    if class_lat not in tree_dict:
        tree_dict[class_lat] = {"vn": class_vn, "latin": class_lat, "orders": {}}
        
    orders_dict = tree_dict[class_lat]["orders"]
    if order_lat not in orders_dict:
        orders_dict[order_lat] = {"vn": order_vn, "latin": order_lat, "families": {}}
        
    families_dict = orders_dict[order_lat]["families"]
    if fam_lat not in families_dict:
        families_dict[fam_lat] = {"vn": fam_vn, "latin": fam_lat, "genera": {}}
        
    genera_dict = families_dict[fam_lat]["genera"]
    if gen_lat_clean not in genera_dict:
        genera_dict[gen_lat_clean] = {"vn": gen_vn, "latin": gen_lat_clean, "species": []}
        
    genera_dict[gen_lat_clean]["species"].append(sp_data)

# Convert nested dict to sorting list-based JSON tree structure
tree_list = []

for c_lat, c_node in sorted(tree_dict.items()):
    c_children = []
    c_species_count = 0
    
    for o_lat, o_node in sorted(c_node["orders"].items()):
        o_children = []
        o_species_count = 0
        
        for f_lat, f_node in sorted(o_node["families"].items()):
            f_children = []
            f_species_count = 0
            
            for g_lat, g_node in sorted(f_node["genera"].items()):
                # Sort species by index
                sorted_species = sorted(g_node["species"], key=lambda x: x["speciesIndex"])
                g_count = len(sorted_species)
                f_species_count += g_count
                
                f_children.append({
                    "vn": g_node["vn"],
                    "latin": g_node["latin"],
                    "type": "genus",
                    "species_count": g_count,
                    "species": sorted_species
                })
                
            # Sort genera alphabetically
            f_children = sorted(f_children, key=lambda x: x["latin"])
            o_species_count += f_species_count
            
            f_children_sorted = f_children
            
            # For displaying families cleanly, we can resolve if fam_vn matches any empty strings
            f_vn = f_node["vn"]
            if f_vn == "Họ ":
                f_vn = f"Họ {f_lat.title()}"
                
            o_children.append({
                "vn": f_vn,
                "latin": f_lat,
                "type": "family",
                "species_count": f_species_count,
                "children": f_children_sorted
            })
            
        # Sort families alphabetically
        o_children = sorted(o_children, key=lambda x: x["latin"])
        c_species_count += o_species_count
        
        o_vn = o_node["vn"]
        if o_vn == "Bộ ":
            o_vn = f"Bộ {o_lat.title()}"
            
        c_children.append({
            "vn": o_vn,
            "latin": o_lat,
            "type": "order",
            "species_count": o_species_count,
            "children": o_children
        })
        
    # Sort orders alphabetically
    c_children = sorted(c_children, key=lambda x: x["latin"])
    
    tree_list.append({
        "vn": c_node["vn"],
        "latin": c_node["latin"],
        "type": "class",
        "species_count": c_species_count,
        "children": c_children
    })

# Save JSON tree to data/ and public/data/
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(tree_list, f, ensure_ascii=False, indent=2)
print(f"Taxonomy tree written to {output_file}")

os.makedirs(os.path.dirname(public_output_file), exist_ok=True)
with open(public_output_file, "w", encoding="utf-8") as f:
    json.dump(tree_list, f, ensure_ascii=False, indent=2)
print(f"Taxonomy tree written to {public_output_file}")
