import json

def update_species():
    filepath = "scratch/tap4_species_11_to_50.json"
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # Find and update species 22
    for sp in data:
        if sp["speciesIndex"] == 22:
            sp["specs"]["vn"]["size"] = "130 - 140 mm. Lớn nhất 160 mm."
            sp["specs"]["vn"]["distribution"] = "Đông Phi, Hồng Hải, Srilanca, Ấn Độ, Indonesia, Philippin, Melanesia, Samoa, Macsan, Việt Nam. Trung Bộ, Nam Bộ."
            sp["specs"]["vn"]["specimen"] = "Viện Hải Dương Học (Nha Trang)."
            sp["specs"]["vn"]["status"] = "Thường gặp."
            sp["specs"]["vn"]["literature"] = "de Beaufort, 1940. Myers, 1991."

            sp["specs"]["en"]["size"] = "130 - 140 mm. Maximum 160 mm"
            sp["specs"]["en"]["distribution"] = "Eastern Africa, Red sea, Srilanca, India, Indonesia, Philippines, Melanesia, Samoa, Marshall, Vietnam. Central and Southern Vietnam."
            sp["specs"]["en"]["specimen"] = "Institute of Oceanography (Nhatrang)."
            sp["specs"]["en"]["status"] = "Common."
            sp["specs"]["en"]["literature"] = "de Beaufort, 1940. Myers, 1991"

            sp["synonyms"].extend([
                "Julis (Halichoeres) annularis Bleeker, Nat. Tijds. Ned. Ind., Vol. 5, p. 513, 1853.",
                "Platyglossus marginatus Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 283, 1862. Gunther, 1862; Day, 1878; Jordan and Seale, 1906."
            ])
            break
            
    new_species = [
        {
          "id": "tap4-species-23",
          "volume": 4,
          "speciesIndex": 23,
          "vnName": "Cá Bàng Chài mini",
          "scientificName": "Halichoeres miniatus",
          "authorship": "(Cuvier and Valenciennes, 1839)",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "80 - 83 mm.",
              "distribution": "Madagasca, Australia, Indonesia, Philippin, Trung Quốc, Việt Nam. Trung Bộ.",
              "specimen": "Bảo tàng động vật Pari (Pháp).",
              "status": "Rất hiếm.",
              "literature": "de Beaufort, 1940. Durand, 1940. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Circle cheek wrasse",
              "size": "80 - 83 mm.",
              "distribution": "Madagascar, Australia, Indonesia, Philippines, China, Vietnam. Central Vietnam.",
              "specimen": "Zoological Museum of Paris (France).",
              "status": "Very rare.",
              "literature": "de Beaufort, 1940. Durand, 1940. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Julis miniatus Cuvier and Valenciennes, Hist. Nat. Poiss., Vol. 13, p. 337 (460), 1839.",
            "Julis (Halichoeres) miniatus Bleeker, Verh. Bat. Gen., Vol. 22, Bijdr. Ichth. Bali, p. 8, 1849.",
            "Halichoeres miniatus Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 287, 1862; Jordan and Seale, 1905; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Carcasson, 1977.",
            "Platyglossus miniatus Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 150, 1862.",
            "Choerojulis miniata Martens, Preuss. Exped. Ost - Asien, Vol. 1, p. 397, 1876.",
            "Octocynodon miniatus Whitley, Great Barrier Reef Exped., Vol. 4, p. 294, 1932.",
            "Halichoeres (Octocynodon) miniatus Fowler, Jour. Acad. Nat. Sci. Phila., Ser. 2, Vol. 12, p. 535, 1904."
          ]
        },
        {
          "id": "tap4-species-24",
          "volume": 4,
          "speciesIndex": 24,
          "vnName": "Cá Bàng Chài ba đốm",
          "scientificName": "Halichoeres trimaculatus",
          "authorship": "(Quoy and Gaimard, 1834)",
          "status": "common",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "87 - 154 mm.",
              "distribution": "Australia, Indonesia, Philippin, Trung Quốc, Nhật Bản, Micronesia, Polynesia, Việt Nam. Trung Bộ, Nam Bộ, Hoàng Sa, Trường Sa.",
              "specimen": "Viện Hải Dương Học (Nha Trang).",
              "status": "Thường gặp.",
              "literature": "de Beaufort, 1940. Orsi, 1974. Nguyễn Hữu Phụng, 1991. Myers, 1991."
            },
            "en": {
              "commonName": "Three - spot Wrasse",
              "size": "87 - 154 mm.",
              "distribution": "Australia, Indonesia, Philippines, China, Japan, Micronesia, Polynesia, Vietnam. Central and Southern Vietnam, Paracels and Spratly islands.",
              "specimen": "Institute of Oceanography (Nhatrang).",
              "status": "Common.",
              "literature": "de Beaufort, 1940. Orsi, 1974. Nguyen Huu Phung, 1991. Myers, 1991."
            }
          },
          "synonyms": [
            "Julis trimaculatus Quoy and Gaimard, Voyage Astrolabe Poissons, Vol. 3, p. 705, pl. 20, fig. 1, 1834.",
            "Guntheria trimaculata Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 291, 1862; Jordan and Snyder, 1902. Witley, 1932.",
            "Julis (Halichoeres) spilurus Bleeker, Nat. Tijds. Ned. Ind., Vol.-2, p. 252, 1851.",
            "Platyglossus trimaculatus Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 153, 1862.",
            "Choerojulis trimaculatus Martens, Preuss. Exped. Ost - Aasian, Vol. 1, p. 397, 1876.",
            "Halichoeres trimaculatus Seale, Occas. Papers. Bishop Mus., Vol. 4, p. 56, 1906; Jordan and Seale, 1906; Jordan and Richardon, 1908; de Beaufort, 1940; Herre, 1953; Matsubara, 1955; Zheng, 1962; Carcasson, 1977; Myers, 1991."
          ]
        },
        {
          "id": "tap4-species-25",
          "volume": 4,
          "speciesIndex": 25,
          "vnName": "Cá Bàng Chài vân mây",
          "scientificName": "Halichoeres nebulosus",
          "authorship": "(Cuvier and Valenciennes, 1839)",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "130 - 150 mm.",
              "distribution": "Australia, Indonesia, Philippin, Fiji, Samoa, Melanesia, Việt Nam. Trung Bộ.",
              "specimen": "Viện Hải Dương Học (Nha Trang).",
              "status": "Ít gặp.",
              "literature": "de Beaufort, 1940. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Clouded Wrasse",
              "size": "130 - 150 mm.",
              "distribution": "Australia, Indonesia, Philippines, Fiji, Samoa, Melanesia, Vietnam. Central Vietnam.",
              "specimen": "Institute of Oceanography (Nhatrang).",
              "status": "Uncommon.",
              "literature": "de Beaufort, 1940. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Julis nebulosus Cuvier and Valenciennes, Hist. Nat. Poiss., Vol. 13, p. 461, 1839.",
            "Julis poecila Lay and Bennett, Zool. Capt. Beechey's Voyage, p.66, pl. 39, fig. 1, 1839.",
            "Platyglossus nebulosus Gunther, cat. Fish. Brit. Mus., Vol. 4, p. 151, 1862; Klunzinger, 1871; Day, 1878; Weber, 1913.",
            "Julis (Halichoeres) harloffii Bleeker, Nat. Geneesk. Arch. Ned. Ind., Ser. 2, Vol. 4, p. 159, 1847.",
            "Halichoeres poecila Bleeker, Versl. Akad. Amst., Vol. 13, p. 288, 1862.",
            "Platyglossus poecilus Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 152, 1862; Peters, 1868.",
            "Halichoeres nebulosus Seale, Occas. Papers. Bishop Mus., Vol. 1, p. 88, 1901; Jordan and Richardson, 1908; McCulloch, 1910; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Matsubara, 1955; Carcasson, 1977.",
            "Choejulis poecila Martens, Preuss. Exped. Ost - Asien, p. 397, 1876.",
            "Halichoeres annulatus Fowler, Jour. Acad. Nat. Sci. Philad. , ser. 2, Vol. 12, p. 535, pl. 20, 1904.",
            "Halichoeres poecilus Jordan and Seale, Proc. U. S. Nat. Mus., Vol. 28, p. 785, 1905; Evermann and Seale, 1907."
          ]
        },
        {
          "id": "tap4-species-26",
          "volume": 4,
          "speciesIndex": 26,
          "vnName": "Cá Bàng Chài chấm đen",
          "scientificName": "Halichoeres melanochir",
          "authorship": "Fowler and Bean, 1928",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "55 - 106 mm. Lớn nhất 120 mm.",
              "distribution": "Philippin, Trung Quốc, Việt Nam. Vịnh Bắc Bộ, Trung Bộ, Nam Bộ",
              "specimen": "Viện Hải Dương Học (Nha Trang).",
              "status": "Ít gặp.",
              "literature": "Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Orange fin wrasse",
              "size": "55 - 106 mm. Maximum 120 mm.",
              "distribution": "Philippines, China, Vietnam. Gulf of Tonkin, Central and Southern Vietnam.",
              "specimen": "Institute of Oceanography (Nhatrang).",
              "status": "Uncommon.",
              "literature": "Zheng, 1962. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Halichoeres melanochir Fowler and Bean, Bull. 100, U.S. Nat. Mus., Vol. 7, p. 264, pl. 25, 1928; Herre, 1953; Zheng, 1962; Carcasson, 1977."
          ]
        },
        {
          "id": "tap4-species-27",
          "volume": 4,
          "speciesIndex": 27,
          "vnName": "Cá Bàng Chài hai chấm",
          "scientificName": "Halichoeres bimaculatus",
          "authorship": "(Ruppell)",
          "status": "rare",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "200 mm.",
              "distribution": "Vùng biển tây Ấn Độ Dương, Việt Nam. Trung Bộ.",
              "specimen": "Viện Hải Dương Học (Nha Trang).",
              "status": "Rất hiếm.",
              "literature": "Carcasson, 1977. Orsi, 1974."
            },
            "en": {
              "commonName": "Two - spoted wrasse",
              "size": "200 mm.",
              "distribution": "Western Indian Ocean, Vietnam. Central Vietnam.",
              "specimen": "Institute of Oceanography (Nhatrang).",
              "status": "Very rare.",
              "literature": "Carcasson, 1977. Orsi, 1974."
            }
          },
          "synonyms": [
            "Halichoeres bimaculatus Ruppell, Neue Wirbelt., Fische Rothen Meeres, p. 10, 1835 (type of Halichoeres); Carcasson, 1977."
          ]
        },
        {
          "id": "tap4-species-28",
          "volume": 4,
          "speciesIndex": 28,
          "vnName": "Cá Bàng Chài macga",
          "scientificName": "Halichoeres margaritaceus",
          "authorship": "(Cuvier and Valeenciennes, 1839)",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "100 - 102 mm.",
              "distribution": "Natan, Zanziba, Australia, Indonesia, Philippin, Melanesia, Nhật Bản, Việt Nam. Trung Bộ.",
              "specimen": "Bảo tàng Động vật Pari (Pháp).",
              "status": "Ít gặp.",
              "literature": "Herre, 1953. Orsi, 1974."
            },
            "en": {
              "commonName": "Weedy surg wrasse, Pearly wrasse",
              "size": "100 - 102 mm.",
              "distribution": "Natan, Zanzibar, Australia, Indonesia, Philippines, Melanesia, Japan, Vietnam. Central Vietnam.",
              "specimen": "Zoological Museum of Paris (France).",
              "status": "Uncommon.",
              "literature": "Herre, 1953. Orsi, 1974"
            }
          },
          "synonyms": [
            "Julis margaritaceus Cuvier and Valenciennes, Hist. Nat. Poiss., Vol. 13, p. 484, 1839.",
            "Halichoeres opercularis Seale, Occas. Papers Bishop Mus. , Vol. 1, p. 89, 1901; Jordan and Seal, 1906; McCulloch, 1910.",
            "Julis (Halichoeres) pseudominiatus Bleeker, Acta Soc. Sci. Indo - Neerl., Vol. 1, 1856, vischssen Amboina, p. 62.",
            "Halichoeres pseudominiatus Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 288, 1862. Jordan and Seale, 1906.",
            "Plastyglossus pseudominiatus Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 151, 1862; Barnard, 1927.",
            "Platyglossus opercularis Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 148, 1862.",
            "Halichoeres margaritaceus Jordan and Seale, Bull. U. S. Bur. Fisheries, Vol. 25, p. 302, 1906; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Matsubara, 1955; Carcasson, 1977; Myers, 1991."
          ]
        },
        {
          "id": "tap4-species-29",
          "volume": 4,
          "speciesIndex": 29,
          "vnName": "Cá Bàng Chài trung",
          "scientificName": "Halichoeres prosopeion",
          "authorship": "(Bleeker, 1853)",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "100 mm. Lớn nhất 135 mm.",
              "distribution": "Indonesia, Philippin, Nhật Bản, Việt Nam. Trung Bộ.",
              "specimen": "Viện Hải Dương Học (Nha Trang).",
              "status": "Rất ít gặp.",
              "literature": "Herre, 1953. Orsi, 1974. Myers, 1991."
            },
            "en": {
              "commonName": "Half grey wrasse, Twotone wrasse",
              "size": "100 mm. Maximum 135 mm.",
              "distribution": "Indonesia, Philippines, Japan, Vietnam. Central Vietnam.",
              "specimen": "Institute of Oceanography (Nhatrang).",
              "status": "Very uncommon.",
              "literature": "Herre, 1953. Orsi,1974. Myers, 1991."
            }
          },
          "synonyms": [
            "Julis (Halichoeres) prosopeion Bleeker, Nat. Tijds. Ned. -Ind., Vol. 5 p. 347, 1853.",
            "Plastyglossus prosopeion Gunther, Cat. Fish. Brit. Mus. , Vol. 4, p. 155, 1862.",
            "Halichoeres prosopion Fowler and Bean, Bull. 100. U. S. Nat. Mus., Vol. 7, p. 290, 1928; Bleeker, 1928; Schmidt, 1930; de Beaufort, 1940; Herre, 1953; Matsubara, 1955; Myers, 1991.",
            "Platyglossus (Paraplatyglossus) prosopeion Bleeker, Arch. Neerl. Sci. Nat., Vol. 13, p. 40, 1878."
          ]
        },
        {
          "id": "tap4-species-30",
          "volume": 4,
          "speciesIndex": 30,
          "vnName": "Cá Bàng Chài sọc sáng",
          "scientificName": "Halichoeres argus",
          "authorship": "(Bloch and Schneider, 1828)",
          "status": "rare",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "110 mm.",
              "distribution": "Australia, Indonesia, Malaysia, Philippin, Trung Quốc, Việt Nam. Trung Bộ.",
              "specimen": "Bảo tàng động vật Pari (Pháp).",
              "status": "Rất hiếm.",
              "literature": "de Beaufort, 1940. Durand, 1940. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Peacock wrasse",
              "size": "110 mm.",
              "distribution": "Australia, Indonesia, Malaysia, Philippines, China, Vietnam. Central Vietnam.",
              "specimen": "Zoological Museum of Paris (France).",
              "status": "Very rare.",
              "literature": "de Beaufort, 1940. Durand, 1940. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Labrus argus Bloch and Schneider, Syst. Ichth. , p. 263, 1801.",
            "Julis argus Bennett, Zool. Jour., Vol. 3, p. 577, pl. 13, fig. 7, 1828; Bleeker, 1849; de Beaufort, 1940.",
            "Julis (Halichoeres) polyophthalmus Bleeker, Nat. Tijds. Ned. Ind., Vol. 3, p. 731, 1852.",
            "Julis (Halichoeres) argus Bleeker, Acta Soc. Sci. Indo. Neerl., p. 37, 1860.",
            "Platyglossus guttatus Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 155, 1862; Meyer, 1885.",
            "Halichoeres guttatus Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 286, 1862; Evermann and Seale, 1906.",
            "Halichoeres argus Lordan and Seale, Proc. U. S. Nat. Mus., Vol. 28, p. 787, 1905; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Carcasson, 1977.",
            "Halichoeres leparensis Fowler, Copeia, No. 58, p. 64, 1918."
          ]
        },
        {
          "id": "tap4-species-31",
          "volume": 4,
          "speciesIndex": 31,
          "vnName": "Cá Bàng Chài 2 sọc đen",
          "scientificName": "Halichoeres bicolor",
          "authorship": "(Bloch and Schneidr, 1801)",
          "status": "common",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "74 - 94 mm. Lớn nhất 133 mm.",
              "distribution": "Indonesia, Philippin, Trung Quốc, Việt Nam. Vịnh Bắc Bộ.",
              "specimen": "Phân viện Hải Dương Học Hải Phòng.",
              "status": "Thường gặp.",
              "literature": "de Beaufort, 1940. Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Bicolor wrasse",
              "size": "74 - 94 mm. Maximum 133 mm.",
              "distribution": "Indonesia, Philippines, China, Vietnam. Gulf of Tonkin.",
              "specimen": "Haiphong Branch of Institute of Oceanography.",
              "status": "Common.",
              "literature": "de Beaufort, 1940. Zheng, 1962. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Labrus bicolor Bloch and Schneider, Syst. Ichth. , p. 267, 1801.",
            "Julis mola Cantor, Jour. Asiatic Soc. Bngal, Vol. 18, p. 1220, 1850.",
            "Julis (Halichoeres) margaritophorus Bleeker, Nat. Tijds. Ned. Ind., Vol. 4, p. 487, 1853.",
            "Julis (Halichoeres) cantori Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 70, 1861.",
            "Platyglossus bicolor Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 145, 1862.",
            "Halichoeres bicolor Fowler and Bean, Bull. 100, U. S. Nat. Mus., Vol. 7, p. 282, 1928; Bleeker, 1862; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Zheng, 1962; Carcasson, 1977."
          ]
        },
        {
          "id": "tap4-species-32",
          "volume": 4,
          "speciesIndex": 32,
          "vnName": "Cá Bàng Chài xám",
          "scientificName": "Halichoeres nigrescens",
          "authorship": "(Bloch and Schneider, 1801)",
          "status": "common",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "84 - 110 mm. Lớn nhất 160 mm.",
              "distribution": "Zanziba, vịnh Persian, Ấn Độ, Miến Điện, Malaysia, Australia, Indonesia, Philippin, Trung Quốc, Nhật Bản, Việt Nam. Vịnh Bắc Bộ, Trung Bộ.",
              "specimen": "Phân viện Hải Dương Học Hải Phòng.",
              "status": "Thường gặp.",
              "literature": "de Beaufort, 1940. Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Nigrescens wrasse",
              "size": "84 - 110 mm. Maximum 160 mm",
              "distribution": "Zanzibar, Persian Gulf, India, Mianma, Malaysia, Australia, Indonesia, Philippines, China, Japan, Vietnam. Gulf of Tonkin, Central Vietnam.",
              "specimen": "Haiphong Branch of Institute of Oceanography.",
              "status": "Common.",
              "literature": "de Beaufort, 1940. Zheng,1962. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Labrus nigrescens Bloch and Schneider, Syst. Ichth. , p. 263, 1801.",
            "Julis (Halichoeres) notophthalmus Bleeker, Verh. Bat. Gen., Vol. 22, p. 20, 1849.",
            "Julis dussumieri Cuvier and Valencinnes, Hist. Nat. Poiss. Vol. 13, p. 478, 1839.",
            "Julis (Halichoeres) mola Bleeker, Acta Soc. Sci. Indo - Neerl. , Vol. 6, p. 98, 1859.",
            "Julis exornatus Richardson, Ichth. China Japan, p. 258, 1846.",
            "Platyglossus dussumieri Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 143, 1862; Day, 1878; Klunzinger, 1879; Regan, 1906.",
            "Halichoeres nigrescens Bleeker, Versl. Akad. Amsterdam, Vol. 13, p. 287, 1862; Jordan and Seale, 1907; Fowler and Bean, 1928; de Beaufort, 1940; Herre, 1953; Matsubara, 1955; Zheng, 1962; Carcasson, 1977.",
            "Choerojulis dussumieri Martens, Pruss. Exped. Ost Asien, Vol. 1, p. 397, 1876.",
            "Halichoeres dussumieri Seale, Philippine Jour. Sci. , Vol. 9, Sec. D, p. 70, 1914."
          ]
        },
        {
          "id": "tap4-species-33",
          "volume": 4,
          "speciesIndex": 33,
          "vnName": "Cá Bàng Chài chấm đuôi",
          "scientificName": "Halichoeres hyrtli",
          "authorship": "(Bleeker, 1856)",
          "status": "common",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "61 - 79 mm. Lớn nhất 110 mm.",
              "distribution": "Vịnh Persian, Srilanca, Ấn Độ, Indonesia, Philippin, Trung Quốc, Việt Nam. Vịnh Bắc Bộ, Trung Bộ.",
              "specimen": "Viện Hải Dương Học (Nha Trang). Phân viện Hải Dương Học Hải Phòng",
              "status": "Thường gặp.",
              "literature": "de Beaufort, 1940. Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977."
            },
            "en": {
              "commonName": "Hyrtli wrasse",
              "size": "61 - 79 mm. Maximum 110 mm",
              "distribution": "Persian Gulf, Srilanca, India, Indonesia, Philippines, China, Vietnam. Gulf of Tonkin, Central Vietnam.",
              "specimen": "Institute of Oceanography (Nhatrang). Haiphong Branch of Institute of Oceanography.",
              "status": "Common.",
              "literature": "de Beaufort, 1940. Zheng, 1962. Orsi, 1974. Carcasson, 1977."
            }
          },
          "synonyms": [
            "Julis (Halichoeres) hyrtli Bleeker, Acta. Soc. Sci. Indo - Neerl., Vol. 1, 1856, Vischfauna, Menado, p. 60.",
            "Platyglossus hyrtelii Gunther, Cat. Fish. Brit. Mus., Vol. 4, p. 149, 1862; Day, 1878.",
            "Platyglossus pseudogramma Cartier, Verh. Phys. Med. Gesell. Wurzburg, Vol., p. 103, 1874.",
            "Halichoeres hyrtli Jordan and Seale, Bull. U. S. Bur. Fish. Vol. 26, p. 29, 1907; de Beaufort, 1940; Herre, 1953; Zheng 1962; Carcasson, 1977.",
            "Halichoeres hyrtlii Fowler and Bean, Bull. 100, U. S. Nat. Mus., Vol. 7, p. 285, 1928."
          ]
        },
        {
          "id": "tap4-species-34",
          "volume": 4,
          "speciesIndex": 34,
          "vnName": "Cá Bàng Chài sọc chấm",
          "scientificName": "Halichoeres cyanopleura",
          "authorship": "(Bleeker 1853)",
          "status": "uncommon",
          "taxonomy": {
            "order": { "vn": "Cá Vược", "latin": "Perciformes" },
            "family": { "vn": "Cá Bàng Chài", "latin": "Labridae" },
            "genus": { "vn": "Giống Cá Bàng Chài Halichoeres Ruppell, 1835", "latin": "Halichoeres Ruppell, 1835" }
          },
          "specs": {
            "vn": {
              "alternateNames": "",
              "size": "",
              "distribution": "",
              "specimen": "",
              "status": "",
              "literature": ""
            },
            "en": {
              "commonName": "Cyanopleura wrasse",
              "size": "",
              "distribution": "",
              "specimen": "",
              "status": "",
              "literature": ""
            }
          },
          "synonyms": [
            "Julis (Halichoeres) cyanopleura Bleeker, Nat. Tijds. Ned."
          ]
        }
    ]

    data.extend(new_species)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_species()
    print("Updated species 22 and appended 23-34.")
