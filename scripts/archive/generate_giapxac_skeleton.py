import json
import os

# 132 species parsed from Muc Luc (Pages 5 - 14) of "Động vật chí Việt Nam - Tập 1: Tôm biển" (2000)
SPECIES_TOC = [
    # Aristeidae
    {
        "idx": 1, "sci": "Aristaeomorpha foliacea", "auth": "(Risso, 1827)",
        "vn": "Tôm đỏ dẹp", "page": 32,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Đỏ Gai", "family_latin": "Aristeidae",
        "genus_vn": "Giống tôm đỏ Aristaeomorpha Wood - Mason et Alcock, 1891", "genus_latin": "Aristaeomorpha Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 2, "sci": "Plesiopenaeus edwardsianus", "auth": "(Johnson, 1867)",
        "vn": "Tôm đỏ biển sâu", "page": 34,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Đỏ Gai", "family_latin": "Aristeidae",
        "genus_vn": "Giống tôm đỏ biển sâu Plesiopenaeus Bate, 1881", "genus_latin": "Plesiopenaeus Bate, 1881"
    },
    {
        "idx": 3, "sci": "Aristeus virilis", "auth": "(Bate, 1881)",
        "vn": "Tôm đỏ gai", "page": 36,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Đỏ Gai", "family_latin": "Aristeidae",
        "genus_vn": "Giống tôm lửa gai Aristeus Duvernoy, 1840", "genus_latin": "Aristeus Duvernoy, 1840"
    },
    # Solenoceridae
    {
        "idx": 4, "sci": "Hadropenaeus lucasii", "auth": "(Bate, 1881)",
        "vn": "Tôm lửa luca", "page": 39,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa vỏ dày Hadropenaeus Perez - Farfante, 1977", "genus_latin": "Hadropenaeus Perez - Farfante, 1977"
    },
    {
        "idx": 5, "sci": "Haliporoides sibogae", "auth": "(de Man, 1907)",
        "vn": "Tôm lửa chùy dẹp", "page": 41,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa chùy dẹp Haliporoides Stebbing, 1914", "genus_latin": "Haliporoides Stebbing, 1914"
    },
    {
        "idx": 6, "sci": "Solenocera crassicornis", "auth": "(H. M. Edwards, 1837)",
        "vn": "Tôm lửa ống", "page": 43,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 7, "sci": "Solenocera koelbeli", "auth": "de Man, 1911",
        "vn": "Tôm lửa Trung Hoa", "page": 45,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 8, "sci": "Solenocera vietnamensis", "auth": "Starobogatov, 1972",
        "vn": "Tôm lửa Việt Nam", "page": 46,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 9, "sci": "Solenocera pectinata", "auth": "(Bate, 1888)",
        "vn": "Tôm lửa đất", "page": 47,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 10, "sci": "Solenocera bedokensis", "auth": "Hall, 1962",
        "vn": "Tôm lửa beđô", "page": 49,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 11, "sci": "Solenocera gurjanovae", "auth": "Starobogatov, 1972",
        "vn": "Tôm lửa gura", "page": 50,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 12, "sci": "Solenocera phuongi", "auth": "Starobogatov, 1972",
        "vn": "Tôm lửa phương gi", "page": 51,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    {
        "idx": 13, "sci": "Solenocera zarenkovi", "auth": "Starobogatov, 1972",
        "vn": "Tôm lửa zaren", "page": 52,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Lửa", "family_latin": "Solenoceridae",
        "genus_vn": "Giống tôm lửa Solenocera H. Lucas, 1849", "genus_latin": "Solenocera H. Lucas, 1849"
    },
    # Penaeidae
    {
        "idx": 14, "sci": "Miyadiella podophthalmus", "auth": "(Stimpson, 1860)",
        "vn": "Tôm he mắt dài", "page": 54,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he mắt dài Miyadiella Kubo, 1949", "genus_latin": "Miyadiella Kubo, 1949"
    },
    {
        "idx": 15, "sci": "Penaeus (Marsupenaeus) japonicus", "auth": "Bate, 1888",
        "vn": "Tôm he Nhật Bản (tôm vằn)", "page": 57,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 16, "sci": "Penaeus (Melicertus) longistylus", "auth": "Kubo, 1943",
        "vn": "Tôm he đỏ", "page": 58,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 17, "sci": "Penaeus (Melicertus) canaliculatus", "auth": "(Olivier, 1811)",
        "vn": "Tôm he rãnh sâu", "page": 60,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 18, "sci": "Penaeus (Melicertus) latisulcatus", "auth": "Kishinouye, 1896",
        "vn": "Tôm gân", "page": 61,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 19, "sci": "Penaeus (Fenneropenaeus) indicus", "auth": "H. Milne-Edwards, 1837",
        "vn": "Tôm he Ấn Độ", "page": 62,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 20, "sci": "Penaeus (Fenneropenaeus) merguiensis", "auth": "de Man, 1888",
        "vn": "Tôm bạc thẻ", "page": 64,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 21, "sci": "Penaeus (Fenneropenaeus) penicillatus", "auth": "Alcock, 1905",
        "vn": "Tôm he lông dài", "page": 66,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 22, "sci": "Penaeus (Fenneropenaeus) chinensis", "auth": "(Osbeck, 1765)",
        "vn": "Tôm nương", "page": 67,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 23, "sci": "Penaeus (Penaeus) monodon", "auth": "Fabricius, 1798",
        "vn": "Tôm sú", "page": 69,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 24, "sci": "Penaeus (Penaeus) semisulcatus", "auth": "de Haan, 1850",
        "vn": "Tôm vằn", "page": 71,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 25, "sci": "Penaeus (Melicertus) marginatus", "auth": "Randall, 1840",
        "vn": "Tôm gân rãnh bên", "page": 72,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he Penaeus Fabricius, 1798", "genus_latin": "Penaeus Fabricius, 1798"
    },
    {
        "idx": 26, "sci": "Metapenaeus ensis", "auth": "(de Haan, 1850)",
        "vn": "Tôm rảo đất", "page": 75,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 27, "sci": "Metapenaeus joyneri", "auth": "(Miers, 1880)",
        "vn": "Tôm rảo vàng", "page": 77,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 28, "sci": "Metapenaeus intermedius", "auth": "(Kishinouye, 1900)",
        "vn": "Tôm rảo đuôi xanh", "page": 79,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 29, "sci": "Metapenaeus affinis", "auth": "(H. M. Edwards, 1837)",
        "vn": "Tôm bột", "page": 80,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 30, "sci": "Metapenaeus tenuipes", "auth": "Kubo, 1949",
        "vn": "Tôm rảo nghệ", "page": 82,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 31, "sci": "Metapenaeus brevicornis", "auth": "(H. M. Edwards, 1837)",
        "vn": "Tôm nghệ", "page": 83,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 32, "sci": "Metapenaeus moyebi", "auth": "(Kishinouye, 1896)",
        "vn": "Tôm rảo cát", "page": 84,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 33, "sci": "Metapenaeus endeavouri", "auth": "(Schmitt, 1926)",
        "vn": "Tôm rảo endevu", "page": 86,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 34, "sci": "Metapenaeus dalli", "auth": "Racek, 1957",
        "vn": "Tôm rảo đan", "page": 87,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 35, "sci": "Metapenaeus dobsoni", "auth": "(Miers, 1878)",
        "vn": "Tôm rảo cađan", "page": 88,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 36, "sci": "Metapenaeus papuensis", "auth": "Racek et Dall, 1965",
        "vn": "Tôm rảo đầm", "page": 89,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 37, "sci": "Metapenaeus lysianassa", "auth": "(de Man, 1888)",
        "vn": "Tôm rảo chim", "page": 90,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm rảo Metapenaeus Wood - Mason et Alcock, 1891", "genus_latin": "Metapenaeus Wood - Mason et Alcock, 1891"
    },
    {
        "idx": 38, "sci": "Parapenaeus sextuberculatus", "auth": "Kubo, 1949",
        "vn": "Tôm he giả", "page": 92,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he giả Parapenaeus Schmitt, 1885", "genus_latin": "Parapenaeus Schmitt, 1885"
    },
    {
        "idx": 39, "sci": "Parapenaeus longipes", "auth": "Alcock, 1905",
        "vn": "Tôm he giả chân dài", "page": 93,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he giả Parapenaeus Schmitt, 1885", "genus_latin": "Parapenaeus Schmitt, 1885"
    },
    {
        "idx": 40, "sci": "Parapenaeus fissuroides", "auth": "Crosnier, 1985",
        "vn": "Tôm he giả gờ cao", "page": 94,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm he giả Parapenaeus Schmitt, 1885", "genus_latin": "Parapenaeus Schmitt, 1885"
    },
    {
        "idx": 41, "sci": "Trachypenaeus curvirostris", "auth": "(Stimpson, 1860)",
        "vn": "Tôm đanh móc", "page": 97,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm đanh Trachypenaeus Alcock, 1901", "genus_latin": "Trachypenaeus Alcock, 1901"
    },
    {
        "idx": 42, "sci": "Trachypenaeus sedili", "auth": "Hall, 1961",
        "vn": "Tôm đanh sedi", "page": 98,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm đanh Trachypenaeus Alcock, 1901", "genus_latin": "Trachypenaeus Alcock, 1901"
    },
    {
        "idx": 43, "sci": "Trachypenaeus longipes", "auth": "(Paulson, 1875)",
        "vn": "Tôm đanh chân dài", "page": 99,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm đanh Trachypenaeus Alcock, 1901", "genus_latin": "Trachypenaeus Alcock, 1901"
    },
    {
        "idx": 44, "sci": "Trachypenaeus pescadoreensis", "auth": "Schmitt, 1931",
        "vn": "Tôm đanh vòng", "page": 100,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm đanh Trachypenaeus Alcock, 1901", "genus_latin": "Trachypenaeus Alcock, 1901"
    },
    {
        "idx": 45, "sci": "Trachypenaeus malaianus", "auth": "Balss, 1933",
        "vn": "Tôm đanh Mã Lai", "page": 102,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm đanh Trachypenaeus Alcock, 1901", "genus_latin": "Trachypenaeus Alcock, 1901"
    },
    {
        "idx": 46, "sci": "Atypopenaeus stenodactylus", "auth": "(Stimpson, 1860)",
        "vn": "Tôm sắt ngón hẹp", "page": 103,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống Atypopenaeus Alcock, 1905", "genus_latin": "Atypopenaeus Alcock, 1905"
    },
    {
        "idx": 47, "sci": "Parapenaeopsis cultrirostris", "auth": "Alcock, 1906",
        "vn": "Tôm sắt rằn", "page": 105,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 48, "sci": "Parapenaeopsis gracillima", "auth": "Nobili, 1903",
        "vn": "Tôm giang giấy, tôm giang đỏ", "page": 107,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 49, "sci": "Parapenaeopsis hardwickii", "auth": "(Miers, 1878)",
        "vn": "Tôm sắt cứng", "page": 108,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 50, "sci": "Parapenaeopsis probata", "auth": "Hall, 1961",
        "vn": "Tôm sắt parô", "page": 109,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 51, "sci": "Parapenaeopsis hungerfordi", "auth": "Alcock, 1905",
        "vn": "Tôm sắt hoa", "page": 110,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 52, "sci": "Parapenaeopsis maxillipedo", "auth": "Alcock, 1905",
        "vn": "Tôm sắt choán", "page": 111,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 53, "sci": "Parapenaeopsis tenella", "auth": "(Bate, 1888)",
        "vn": "Tôm sắt láng", "page": 113,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 54, "sci": "Parapenaeopsis cornuta", "auth": "(Kishinouye, 1900)",
        "vn": "Tôm sắt cọtna", "page": 114,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 55, "sci": "Parapenaeopsis amicus", "auth": "N.V. Chung, 1971",
        "vn": "Tôm sắt Bắc Bộ", "page": 115,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 56, "sci": "Parapenaeopsis stylifera", "auth": "(H. Milne-Edwards, 1837)",
        "vn": "Tôm sắt giang", "page": 117,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm sắt Parapenaeopsis Alcock, 1901", "genus_latin": "Parapenaeopsis Alcock, 1901"
    },
    {
        "idx": 57, "sci": "Metapenaeopsis lamellata", "auth": "de Haan, 1850",
        "vn": "Tôm chùy phiến", "page": 119,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 58, "sci": "Metapenaeopsis mogiensis", "auth": "(Rathbun, 1902)",
        "vn": "Tôm vân đỏ", "page": 121,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 59, "sci": "Metapenaeopsis dalei", "auth": "(Rathbun, 1902)",
        "vn": "Tôm đỏ đali", "page": 122,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 60, "sci": "Metapenaeopsis barbata", "auth": "(de Haan, 1850)",
        "vn": "Tôm vỏ lông", "page": 124,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 61, "sci": "Metapenaeopsis stridulans", "auth": "(Alcock, 1905)",
        "vn": "Tôm gõ", "page": 125,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 62, "sci": "Metapenaeopsis toloensis", "auth": "Hall, 1962",
        "vn": "Tôm nâu tôlô", "page": 127,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    {
        "idx": 63, "sci": "Metapenaeopsis palmensis", "auth": "(Haswell, 1879)",
        "vn": "Tôm vỏ u rộng", "page": 128,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm He", "family_latin": "Penaeidae",
        "genus_vn": "Giống tôm vỏ đỏ Metapenaeopsis Bouvier, 1905", "genus_latin": "Metapenaeopsis Bouvier, 1905"
    },
    # Sicyoniidae
    {
        "idx": 64, "sci": "Sicyonia lancifer", "auth": "(Olive, 1811)",
        "vn": "Tôm đơn nhánh nhọn", "page": 130,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Đơn Nhánh", "family_latin": "Sicyoniidae",
        "genus_vn": "Giống tôm đơn nhánh Sicyonia H. Milne - Edwards, 1830", "genus_latin": "Sicyonia H. Milne - Edwards, 1830"
    },
    {
        "idx": 65, "sci": "Sicyonia ommanneyi", "auth": "Hall, 1962",
        "vn": "Tôm đơn nhánh ít gai", "page": 132,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Đơn Nhánh", "family_latin": "Sicyoniidae",
        "genus_vn": "Giống tôm đơn nhánh Sicyonia H. Milne - Edwards, 1830", "genus_latin": "Sicyonia H. Milne - Edwards, 1830"
    },
    # Nephropidae
    {
        "idx": 66, "sci": "Metanephrops thomsoni", "auth": "(Bate, 1888)",
        "vn": "Tôm rồng vạch đỏ", "page": 134,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Rồng", "family_latin": "Nephropidae",
        "genus_vn": "Giống Metanephrops Jenkins, 1972", "genus_latin": "Metanephrops Jenkins, 1972"
    },
    {
        "idx": 67, "sci": "Metanephrops andamanicus", "auth": "(Wood Mason, 1891)",
        "vn": "Tôm rồng", "page": 135,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Rồng", "family_latin": "Nephropidae",
        "genus_vn": "Giống Metanephrops Jenkins, 1972", "genus_latin": "Metanephrops Jenkins, 1972"
    },
    {
        "idx": 68, "sci": "Metanephrops sinensis", "auth": "(Bruce, 1966)",
        "vn": "Tôm rồng Trung Hoa", "page": 136,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Rồng", "family_latin": "Nephropidae",
        "genus_vn": "Giống Metanephrops Jenkins, 1972", "genus_latin": "Metanephrops Jenkins, 1972"
    },
    {
        "idx": 69, "sci": "Nephropsis stewarti", "auth": "Wood - Mason, 1873",
        "vn": "Tôm rồng stewart", "page": 138,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Rồng", "family_latin": "Nephropidae",
        "genus_vn": "Giống Nephropsis Wood Mason, 1873", "genus_latin": "Nephropsis Wood Mason, 1873"
    },
    # Palinuridae
    {
        "idx": 70, "sci": "Linuparus trigonus", "auth": "(Von Siebold, 1824)",
        "vn": "Tôm hùm kiếm ba góc", "page": 140,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm kiếm Linuparus White, 1847", "genus_latin": "Linuparus White, 1847"
    },
    {
        "idx": 71, "sci": "Panulirus homarus", "auth": "(Linnaeus, 1758)",
        "vn": "Tôm hùm đá (ghì, kẹt, xanh chân ngắn)", "page": 143,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 72, "sci": "Panulirus longipes", "auth": "(H. M. Edwards, 1869)",
        "vn": "Tôm hùm đỏ", "page": 145,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 73, "sci": "Panulirus ornatus", "auth": "(Fabricius, 1798)",
        "vn": "Tôm hùm bông (sao, hèo)", "page": 146,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 74, "sci": "Panulirus penicillatus", "auth": "(Olivier, 1791)",
        "vn": "Tôm hùm ma", "page": 148,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 75, "sci": "Panulirus polyphagus", "auth": "(Herbst, 1793)",
        "vn": "Tôm hùm bùn (chuối, tre)", "page": 150,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 76, "sci": "Panulirus stimpsoni", "auth": "Holthuis, 1963",
        "vn": "Tôm hùm sỏi (xanh chân dài, lông)", "page": 151,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    {
        "idx": 77, "sci": "Panulirus versicolor", "auth": "(Latreille, 1804)",
        "vn": "Tôm hùm sen", "page": 153,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Gai", "family_latin": "Palinuridae",
        "genus_vn": "Giống tôm hùm gai Panulirus White, 1847", "genus_latin": "Panulirus White, 1847"
    },
    # Synaxidae
    {
        "idx": 78, "sci": "Palinurellus gundlachi var. wieneckii", "auth": "(Gruwel, 1881)",
        "vn": "Tôm hùm lông đỏ", "page": 155,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Hùm Lông", "family_latin": "Synaxidae",
        "genus_vn": "Giống tôm hùm lông Palinurellus Von Martens, 1878", "genus_latin": "Palinurellus Von Martens, 1878"
    },
    # Scyllaridae
    {
        "idx": 79, "sci": "Scyllarides squammosus", "auth": "(H. M. Edwards, 1837)",
        "vn": "Tôm vỗ chấm đỏ", "page": 159,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ đỏ Scyllarides Gill, 1898", "genus_latin": "Scyllarides Gill, 1898"
    },
    {
        "idx": 80, "sci": "Scyllarides haanii", "auth": "(de Haan, 1841)",
        "vn": "Tôm vỗ đỏ", "page": 160,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ đỏ Scyllarides Gill, 1898", "genus_latin": "Scyllarides Gill, 1898"
    },
    {
        "idx": 81, "sci": "Thenus orientalis", "auth": "(Lund, 1793)",
        "vn": "Tôm vỗ dẹp trắng, tôm vỗ biển cạn", "page": 161,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ (Mũ ni) dẹp Thenus Leach, 1815", "genus_latin": "Thenus Leach, 1815"
    },
    {
        "idx": 82, "sci": "Scyllarus rugosus", "auth": "H. Milne Edwards, 1837",
        "vn": "Tôm vỗ châu chấu lưng gù", "page": 163,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ châu chấu Scyllarus Fabricius, 1775", "genus_latin": "Scyllarus Fabricius, 1775"
    },
    {
        "idx": 83, "sci": "Scyllarus bertholdii", "auth": "Paulson, 1875",
        "vn": "Tôm vỗ châu chấu hai chấm", "page": 164,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ châu chấu Scyllarus Fabricius, 1775", "genus_latin": "Scyllarus Fabricius, 1775"
    },
    {
        "idx": 84, "sci": "Scyllarus martensii", "auth": "Peffer, 1881",
        "vn": "Tôm vỗ châu chấu vằn", "page": 165,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ châu chấu Scyllarus Fabricius, 1775", "genus_latin": "Scyllarus Fabricius, 1775"
    },
    {
        "idx": 85, "sci": "Ibacus ciliatus", "auth": "(Von Siebold, 1824)",
        "vn": "Tôm vỗ biển sâu", "page": 166,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ biển sâu Ibacus Leach, 1815", "genus_latin": "Ibacus Leach, 1815"
    },
    {
        "idx": 86, "sci": "Ibacus novemdentatus", "auth": "Gibbes, 1850",
        "vn": "Tôm vỗ đuôi quạt láng", "page": 167,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ biển sâu Ibacus Leach, 1815", "genus_latin": "Ibacus Leach, 1815"
    },
    {
        "idx": 87, "sci": "Parribacus antarcticus", "auth": "(Lund, 1793)",
        "vn": "Tôm vỗ xanh", "page": 169,
        "order_vn": "Bộ Mười Chân", "order_latin": "Decapoda",
        "family_vn": "Họ Tôm Vỗ (Mũ Ni)", "family_latin": "Scyllaridae",
        "genus_vn": "Giống tôm vỗ xanh Parribacus Dana, 1852", "genus_latin": "Parribacus Dana, 1852"
    },
    # STOMATOPODA - Gonodactylidae
    {
        "idx": 88, "sci": "Gonodactylaceus gravieri", "auth": "Manning, 1995",
        "vn": "Tôm tít gravie", "page": 172,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylaceus R.B. Manning, 1995", "genus_latin": "Gonodactylaceus R.B. Manning, 1995"
    },
    {
        "idx": 89, "sci": "Gonodactylaceus mutatus", "auth": "(Lanchester, 1903)",
        "vn": "Tôm tít đổi màu", "page": 173,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylaceus R.B. Manning, 1995", "genus_latin": "Gonodactylaceus R.B. Manning, 1995"
    },
    {
        "idx": 90, "sci": "Gonodactylaceus ternatensis", "auth": "(de Man, 1902)",
        "vn": "Tôm tít ternaten", "page": 175,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylaceus R.B. Manning, 1995", "genus_latin": "Gonodactylaceus R.B. Manning, 1995"
    },
    {
        "idx": 91, "sci": "Gonodactylellus hendersoni", "auth": "(Manning, 1967)",
        "vn": "Tôm tít henđơxơn", "page": 177,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylellus Manning, 1995", "genus_latin": "Gonodactylellus Manning, 1995"
    },
    {
        "idx": 92, "sci": "Gonodactylellus incipiens", "auth": "(Lanchester, 1903)",
        "vn": "Tôm tít inxipien", "page": 178,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylellus Manning, 1995", "genus_latin": "Gonodactylellus Manning, 1995"
    },
    {
        "idx": 93, "sci": "Gonodactylellus affinis", "auth": "(de Man, 1902)",
        "vn": "Tôm tít affinis", "page": 179,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylellus Manning, 1995", "genus_latin": "Gonodactylellus Manning, 1995"
    },
    {
        "idx": 94, "sci": "Gonodactylinus viridis", "auth": "(Serene, 1954)",
        "vn": "Tôm tít xanh", "page": 180,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylinus Manning, 1995", "genus_latin": "Gonodactylinus Manning, 1995"
    },
    {
        "idx": 95, "sci": "Gonodactylus chiragra", "auth": "(Fabricius, 1781)",
        "vn": "Tôm tít ngón chiragra", "page": 181,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylus Berthold, 1827", "genus_latin": "Gonodactylus Berthold, 1827"
    },
    {
        "idx": 96, "sci": "Gonodactylus platysoma", "auth": "Wood - Mason, 1895",
        "vn": "Tôm tít thân dẹp", "page": 183,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylus Berthold, 1827", "genus_latin": "Gonodactylus Berthold, 1827"
    },
    {
        "idx": 97, "sci": "Gonodactylus smithii", "auth": "Pocock, 1893",
        "vn": "Tôm tít smith", "page": 184,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Ngón Lớn", "family_latin": "Gonodactylidae",
        "genus_vn": "Giống Gonodactylus Berthold, 1827", "genus_latin": "Gonodactylus Berthold, 1827"
    },
    # Odontodactylidae
    {
        "idx": 98, "sci": "Odontodactylus scyllarus", "auth": "(Linnaeus, 1758)",
        "vn": "Tôm tít chim công", "page": 186,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Răng", "family_latin": "Odontodactylidae",
        "genus_vn": "Giống Odontodactylus Bigelow, 1893", "genus_latin": "Odontodactylus Bigelow, 1893"
    },
    {
        "idx": 99, "sci": "Raoulius cultrifer", "auth": "(White, 1850)",
        "vn": "Tôm tít dao", "page": 187,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Răng", "family_latin": "Odontodactylidae",
        "genus_vn": "Giống Raoulius Manning, 1995", "genus_latin": "Raoulius Manning, 1995"
    },
    # Protosquillidae
    {
        "idx": 100, "sci": "Chorisquilla brooksii", "auth": "(de Man, 1888)",
        "vn": "Tôm tít brook", "page": 190,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Chorisquilla", "genus_latin": "Chorisquilla Manning, 1969"
    },
    {
        "idx": 101, "sci": "Chorisquilla spinosissima", "auth": "(Pfeffer, 1888)",
        "vn": "Tôm tít nhiều gai", "page": 191,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Chorisquilla", "genus_latin": "Chorisquilla Manning, 1969"
    },
    {
        "idx": 102, "sci": "Haptosquilla glabra", "auth": "(Lenz, 1905)",
        "vn": "Tôm tít trơn", "page": 193,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Haptosquilla", "genus_latin": "Haptosquilla Manning, 1969"
    },
    {
        "idx": 103, "sci": "Haptosquilla glyptocercus", "auth": "(Wood-Mason, 1875)",
        "vn": "Tôm tít đuôi chạm", "page": 195,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Haptosquilla", "genus_latin": "Haptosquilla Manning, 1969"
    },
    {
        "idx": 104, "sci": "Haptosquilla stoliura", "auth": "(Muller, 1886)",
        "vn": "Tôm tít đuôi sọc", "page": 196,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Haptosquilla", "genus_latin": "Haptosquilla Manning, 1969"
    },
    {
        "idx": 105, "sci": "Haptosquilla tuberosa", "auth": "(Pocock, 1893)",
        "vn": "Tôm tít u đuôi", "page": 198,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Gai Đuôi", "family_latin": "Protosquillidae",
        "genus_vn": "Giống Haptosquilla", "genus_latin": "Haptosquilla Manning, 1969"
    },
    # Pseudosquillidae
    {
        "idx": 106, "sci": "Pseudosquilla ciliata", "auth": "(Fabricius, 1787)",
        "vn": "Tôm tít giả có lông", "page": 200,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Giả", "family_latin": "Pseudosquillidae",
        "genus_vn": "Giống Pseudosquilla", "genus_latin": "Pseudosquilla Dana, 1852"
    },
    {
        "idx": 107, "sci": "Raoulserenea ornata", "auth": "(Miers, 1880)",
        "vn": "Tôm tít hoa", "page": 202,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Giả", "family_latin": "Pseudosquillidae",
        "genus_vn": "Giống Raoulserenea", "genus_latin": "Raoulserenea Manning, 1995"
    },
    # Takuiidae
    {
        "idx": 108, "sci": "Taku spinosocarinatus", "auth": "(Fukuda, 1909)",
        "vn": "Tôm tít taku gờ gai", "page": 204,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Takuiidae", "family_latin": "Takuiidae",
        "genus_vn": "Giống Taku", "genus_latin": "Taku Manning, 1995"
    },
    # Lysiosquillidae
    {
        "idx": 109, "sci": "Lysiosquilla sulcirostris", "auth": "Kemp, 1913",
        "vn": "Tôm tít rãnh chùy", "page": 207,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Bọ Ngựa", "family_latin": "Lysiosquillidae",
        "genus_vn": "Giống Lysiosquilla", "genus_latin": "Lysiosquilla Dana, 1852"
    },
    {
        "idx": 110, "sci": "Lysiosquillia tredecimdentata", "auth": "Holthuis, 1941",
        "vn": "Tôm tít mười ba răng", "page": 208,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Bọ Ngựa", "family_latin": "Lysiosquillidae",
        "genus_vn": "Giống Lysiosquilla", "genus_latin": "Lysiosquilla Dana, 1852"
    },
    {
        "idx": 111, "sci": "Lysiosquillina maculata", "auth": "(Fabricius, 1793)",
        "vn": "Tôm tít vằn bọ ngựa", "page": 210,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít Bọ Ngựa", "family_latin": "Lysiosquillidae",
        "genus_vn": "Giống Lysiosquillina", "genus_latin": "Lysiosquillina Manning, 1995"
    },
    # Nannosquillidae
    {
        "idx": 112, "sci": "Acanthosquilla acanthocarpus", "auth": "(Claus, 1871)",
        "vn": "Tôm tít gai cổ tay", "page": 212,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Nannosquillidae", "family_latin": "Nannosquillidae",
        "genus_vn": "Giống Acanthosquilla", "genus_latin": "Acanthosquilla Manning, 1963"
    },
    {
        "idx": 113, "sci": "Acanthosquilla multifasciata", "auth": "(Wood-Mason, 1895)",
        "vn": "Tôm tít nhiều dải", "page": 214,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Nannosquillidae", "family_latin": "Nannosquillidae",
        "genus_vn": "Giống Acanthosquilla", "genus_latin": "Acanthosquilla Manning, 1963"
    },
    # Heterosquillidae
    {
        "idx": 114, "sci": "Heterosquilloides insignis", "auth": "(Kemp, 1911)",
        "vn": "Tôm tít dị hình", "page": 215,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Heterosquillidae", "family_latin": "Heterosquillidae",
        "genus_vn": "Giống Heterosquilloides", "genus_latin": "Heterosquilloides Manning, 1966"
    },
    # Squillidae
    {
        "idx": 115, "sci": "Anchisquilla fasciata", "auth": "(de Haan, 1844)",
        "vn": "Tôm tít vạch", "page": 218,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Anchisquilla", "genus_latin": "Anchisquilla Manning, 1968"
    },
    {
        "idx": 116, "sci": "Carinosquilla carinata", "auth": "(Serene, 1950)",
        "vn": "Tôm tít gờ sống", "page": 220,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Carinosquilla Manning, 1968", "genus_latin": "Carinosquilla Manning, 1968"
    },
    {
        "idx": 117, "sci": "Carinosquilla multicarinata", "auth": "(White, 1848)",
        "vn": "Tôm tít nhiều gờ", "page": 221,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Carinosquilla Manning, 1968", "genus_latin": "Carinosquilla Manning, 1968"
    },
    {
        "idx": 118, "sci": "Clorida bombayensis", "auth": "(Chhapgar & Sane, 1967)",
        "vn": "Tôm tít bombay", "page": 222,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Clorida Eydoux & Souleyet, 1842", "genus_latin": "Clorida Eydoux & Souleyet, 1842"
    },
    {
        "idx": 119, "sci": "Clorida decorata", "auth": "Wood - Mason, 1875",
        "vn": "Tôm tít hoa văn", "page": 224,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Clorida Eydoux & Souleyet, 1842", "genus_latin": "Clorida Eydoux & Souleyet, 1842"
    },
    {
        "idx": 120, "sci": "Clorida latreillei", "auth": "Eydoux & Souleyet, 1842",
        "vn": "Tôm tít latrây", "page": 225,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Clorida Eydoux & Souleyet, 1842", "genus_latin": "Clorida Eydoux & Souleyet, 1842"
    },
    {
        "idx": 121, "sci": "Cloridina chlorida", "auth": "(Brooks, 1888)",
        "vn": "Tôm tít lục", "page": 227,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Cloridina", "genus_latin": "Cloridina Manning, 1995"
    },
    {
        "idx": 122, "sci": "Cloridina pelamidae", "auth": "(Blumstein, 1970)",
        "vn": "Tôm tít pelami", "page": 228,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Cloridina", "genus_latin": "Cloridina Manning, 1995"
    },
    {
        "idx": 123, "sci": "Erugosquilla woodmasoni", "auth": "(Kemp, 1911)",
        "vn": "Tôm tít vuốt đỏ", "page": 230,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Erugosquilla", "genus_latin": "Erugosquilla Manning, 1995"
    },
    {
        "idx": 124, "sci": "Keijia lirata", "auth": "(Kemp & Chopra, 1921)",
        "vn": "Tôm tít keijia", "page": 231,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Keijia", "genus_latin": "Keijia Manning, 1995"
    },
    {
        "idx": 125, "sci": "Lenisquilla lata", "auth": "(Brooks, 1886)",
        "vn": "Tôm tít bản rộng", "page": 232,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Lenisquilla", "genus_latin": "Lenisquilla Manning, 1977"
    },
    {
        "idx": 126, "sci": "Miyakea nepa", "auth": "(Latreille, 1828)",
        "vn": "Tôm tít nepa", "page": 234,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Miyakea", "genus_latin": "Miyakea Manning, 1995"
    },
    {
        "idx": 127, "sci": "Oratosquilla oratoria", "auth": "(de Haan, 1844)",
        "vn": "Tôm tít nhật", "page": 235,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Oratosquilla", "genus_latin": "Oratosquilla Manning, 1968"
    },
    {
        "idx": 128, "sci": "Oratosquillina gonypetes", "auth": "(Kemp, 1911)",
        "vn": "Tôm tít gony", "page": 237,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Oratosquillina", "genus_latin": "Oratosquillina Manning, 1995"
    },
    {
        "idx": 129, "sci": "Oratosquillina gravieri", "auth": "(Manning, 1978)",
        "vn": "Tôm tít gravieri", "page": 238,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Oratosquillina", "genus_latin": "Oratosquillina Manning, 1995"
    },
    {
        "idx": 130, "sci": "Oratosquillina interrupta", "auth": "(Kemp, 1911)",
        "vn": "Tôm tít ngắt đoạn", "page": 239,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Oratosquillina", "genus_latin": "Oratosquillina Manning, 1995"
    },
    {
        "idx": 131, "sci": "Oratosquillina perpensa", "auth": "(Kemp, 1911)",
        "vn": "Tôm tít perpen", "page": 240,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Oratosquillina", "genus_latin": "Oratosquillina Manning, 1995"
    },
    {
        "idx": 132, "sci": "Toshimitsu tiwarii", "auth": "(Blumstein, 1974)",
        "vn": "Tôm tít toshimitsu", "page": 242,
        "order_vn": "Bộ Tôm Tít", "order_latin": "Stomatopoda",
        "family_vn": "Họ Tôm Tít", "family_latin": "Squillidae",
        "genus_vn": "Giống Toshimitsu", "genus_latin": "Toshimitsu Manning, 1995"
    }
]

def main():
    rows = []
    for sp in SPECIES_TOC:
        row = {
            "id": f"giapxac-species-{sp['idx']}",
            "collection_id": "giap-xac",
            "volume": 1,
            "species_index": sp["idx"],
            "vn_name": sp["vn"],
            "scientific_name": sp["sci"],
            "authorship": sp["auth"],
            "tax_class_vn": "Lớp Giáp Xác",
            "tax_class_latin": "Malacostraca",
            "tax_order_vn": sp["order_vn"],
            "tax_order_latin": sp["order_latin"],
            "tax_family_vn": sp["family_vn"],
            "tax_family_latin": sp["family_latin"],
            "tax_genus_vn": sp["genus_vn"],
            "tax_genus_latin": sp["genus_latin"],
            "book_page": sp["page"],
            "conservation_status": "unknown",
            "synonyms": [],
            "morphology_vn": "",
            "ecology_vn": "",
            "economic_value_vn": "",
            "vn_size": "",
            "vn_distribution": "",
            "vn_specimen": "",
            "vn_status": "",
            "vn_literature": ""
        }
        rows.append(row)

    out_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ocr_batches", "giap_xac_toc_132.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã ghi nhận thành công {len(rows)} loài vào {out_file}")

if __name__ == "__main__":
    main()
