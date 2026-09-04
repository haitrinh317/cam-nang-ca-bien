import json

def fix_species():
    targets = ["data/species.json", "public/data/species.json"]
    for target in targets:
        with open(target, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        for sp in data:
            if sp.get("volume") == 4:
                if sp["speciesIndex"] == 22:
                    sp["specs"]["vn"]["size"] = "130 - 140 mm. Lớn nhất 160 mm."
                    sp["specs"]["vn"]["distribution"] = "Đông Phi, Hồng Hải, Srilanca, Ấn Độ, Indonesia, Philippin, Melanesia, Samoa, Macsan, Việt Nam. Trung Bộ, Nam Bộ."
                    sp["specs"]["vn"]["specimen"] = "Viện Hải Dương Học (Nha Trang)."
                    sp["specs"]["vn"]["status"] = "Thường gặp."
                    sp["specs"]["vn"]["literature"] = "de Beaufort, 1940. Myers, 1991."
                    
                    sp["specs"]["en"]["size"] = "130 - 140 mm. Maximum 160 mm."
                    sp["specs"]["en"]["distribution"] = "Eastern Africa, Red sea, Srilanca, India, Indonesia, Philippines, Melanesia, Samoa, Marshall, Vietnam. Central and Southern Vietnam."
                    sp["specs"]["en"]["specimen"] = "Institute of Oceanography (Nhatrang)."
                    sp["specs"]["en"]["status"] = "Common."
                    sp["specs"]["en"]["literature"] = "de Beaufort, 1940. Myers, 1991."
                
                if sp["speciesIndex"] == 34:
                    sp["vnName"] = "Cá Bàng Chài sọc chấm"
                    sp["scientificName"] = "Halichoeres cyanopleura"
                    sp["authorship"] = "(Bleeker, 1853)"
                    
                    sp["specs"]["vn"]["size"] = "65 - 105 mm. Lớn nhất 132 mm."
                    sp["specs"]["vn"]["distribution"] = "Indonesia, Philippin, Trung Quốc, Việt Nam. Vịnh Bắc Bộ, Trung Bộ."
                    sp["specs"]["vn"]["specimen"] = "Viện Hải Dương Học (Nha Trang). Phân viện Hải Dương Học Hải Phòng."
                    sp["specs"]["vn"]["status"] = "Thường gặp."
                    sp["specs"]["vn"]["literature"] = "de Beaufort, 1940. Trịnh Bảo San, 1962. Orsi, 1974."
                    
                    sp["specs"]["en"]["commonName"] = "Cyanopleura wrasse"
                    sp["specs"]["en"]["size"] = "65 - 105 mm. Maximum 132 mm."
                    sp["specs"]["en"]["distribution"] = "Indonesia, Philippines, China, Vietnam. Gulf of Tonkin, Central Vietnam."
                    sp["specs"]["en"]["specimen"] = "Institute of Oceanography (Nhatrang). Haiphong Branch of Institute of Oceanography."
                    sp["specs"]["en"]["status"] = "Common."
                    sp["specs"]["en"]["literature"] = "de Beaufort, 1940. Zheng, 1962. Orsi, 1974."
                    
                    sp["synonyms"] = [
                        "Julis (Halichoeres) cyanopleura Bleeker, Nat. Tijds. Ned. Ind., Vol. 4, p. 489, 1853.",
                        "Julis (Halichoeres) pyrrhogrammatoides Bleeker, Nat. Tijds. Ned. Ind., Vol. 4, p. 490, 1853.",
                        "Leptojulis pyrrhogrammatoides Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 167, 1862; Bleeker, 1862.",
                        "Leptojulis cyanopleura Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 289, 1862.",
                        "Halichoeres cyanopleura de Beaufort, Fish. Ind - Austr. Arch. Vol. 8, p. 183, 1940; Herre, 1953; Zheng, 1962."
                    ]

        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print("Fixed species 22 and 34 in species.json")

if __name__ == "__main__":
    fix_species()
