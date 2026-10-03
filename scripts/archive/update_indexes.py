import re
import os

def update_index_file(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update the Volume III card
    old_card = """        <!-- TAP III -->
        <a href="tap-3.html" class="volume-card v3 pending">
            <div class="vc-header">
                <span class="vc-volume-num">Tập III</span>
            </div>
            <h2 class="vc-title">Lớp Cá Xương (Phần 2)</h2>
            <p class="vc-desc">
                Osteichthyes (tiếp). Các bộ cá xương cơ trục như cá Ngựa, cá Mú, cá Hồng và các nhóm cá rạn san hô đặc trưng của vùng biển nhiệt đới.
            </p>
            <div class="vc-meta" style="opacity: 0;">
                <span class="vc-meta-item"><strong>---</strong> loài</span>
                <span class="vc-meta-item"><strong>---</strong> trang</span>
            </div>
        </a>"""
        
    new_card = """        <!-- TAP III -->
        <a href="tap-3.html" class="volume-card v3">
            <div class="vc-header">
                <span class="vc-volume-num">Tập III</span>
                <span class="vc-status ready">Đã số hóa (15 loài đầu)</span>
            </div>
            <h2 class="vc-title">Lớp Cá Xương (Phần 2)</h2>
            <p class="vc-desc">
                Osteichthyes (tiếp). Các bộ cá xương cơ bản như cá Ngựa, cá Mú, cá Hồng và các nhóm cá rạn san hô đặc trưng của vùng biển nhiệt đới.
            </p>
            <div class="vc-meta">
                <span class="vc-meta-item"><strong>15</strong> loài</span>
                <span class="vc-meta-item"><strong>607</strong> trang</span>
            </div>
            <div class="vc-action ready-btn">
                <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
                Xem chi tiết
            </div>
        </a>"""

    # We do a flexible whitespace replacement to handle line ending differences
    # Let's clean both patterns and look for a match
    cleaned_content = content.replace("\r\n", "\n")
    cleaned_old = old_card.replace("\r\n", "\n")
    cleaned_new = new_card.replace("\r\n", "\n")
    
    if cleaned_old in cleaned_content:
        cleaned_content = cleaned_content.replace(cleaned_old, cleaned_new)
        print(f"Updated Volume III card in {filepath}")
    else:
        # Fallback regex replacement if whitespace differed
        # Search for pending v3 volume-card
        pattern = r'<!-- TAP III -->\s*<a href="tap-3\.html" class="volume-card v3 pending">.*?</a>'
        match = re.search(pattern, cleaned_content, re.DOTALL)
        if match:
            cleaned_content = re.sub(pattern, cleaned_new, cleaned_content, flags=re.DOTALL)
            print(f"Updated Volume III card using Regex in {filepath}")
        else:
            print(f"Could not find Volume III card pattern in {filepath}")

    # 2. Update search index JS loader to fetch tap-3.html
    old_js = """        // Dynamically build search index from Vol II
        fetch('tap-2.html')
            .then(r => r.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const cards = doc.querySelectorAll('.species-card');
                cards.forEach(card => {
                    const vnName = card.querySelector('.species-vn-name');
                    const sciName = card.querySelector('.species-scientific-name');
                    const id = card.id;
                    if (vnName && sciName && id) {
                        searchIndex.push({
                            vn: vnName.textContent.trim(),
                            sci: sciName.textContent.trim(),
                            id: id,
                            vol: 2,
                            file: 'tap-2.html'
                        });
                    }
                });
                console.log(`Loaded ${searchIndex.length} species into search index after Vol II.`);
            })
            .catch(err => console.warn('Could not load Vol II:', err));"""

    new_js = """        // Dynamically build search index from Vol II
        fetch('tap-2.html')
            .then(r => r.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const cards = doc.querySelectorAll('.species-card');
                cards.forEach(card => {
                    const vnName = card.querySelector('.species-vn-name');
                    const sciName = card.querySelector('.species-scientific-name');
                    const id = card.id;
                    if (vnName && sciName && id) {
                        searchIndex.push({
                            vn: vnName.textContent.trim(),
                            sci: sciName.textContent.trim(),
                            id: id,
                            vol: 2,
                            file: 'tap-2.html'
                        });
                    }
                });
                console.log(`Loaded ${searchIndex.length} species into search index after Vol II.`);
            })
            .catch(err => console.warn('Could not load Vol II:', err));

        // Dynamically build search index from Vol III
        fetch('tap-3.html')
            .then(r => r.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const cards = doc.querySelectorAll('.species-card');
                cards.forEach(card => {
                    const vnName = card.querySelector('.species-vn-name');
                    const sciName = card.querySelector('.species-scientific-name');
                    const id = card.id;
                    if (vnName && sciName && id) {
                        searchIndex.push({
                            vn: vnName.textContent.trim(),
                            sci: sciName.textContent.trim(),
                            id: id,
                            vol: 3,
                            file: 'tap-3.html'
                        });
                    }
                });
                console.log(`Loaded ${searchIndex.length} species into search index after Vol III.`);
            })
            .catch(err => console.warn('Could not load Vol III:', err));"""

    cleaned_old_js = old_js.replace("\r\n", "\n")
    cleaned_new_js = new_js.replace("\r\n", "\n")

    if cleaned_old_js in cleaned_content:
        cleaned_content = cleaned_content.replace(cleaned_old_js, cleaned_new_js)
        print(f"Added Vol III search index loader in {filepath}")
    else:
        print(f"Could not find JS indexer pattern in {filepath}")

    with open(filepath, "w", encoding="utf-8") as f:
        # Convert LF back to CRLF on Windows for safety
        f.write(cleaned_content.replace("\n", "\r\n"))

update_index_file("index.html")
update_index_file("public/index.html")
print("Finished updating index files.")
