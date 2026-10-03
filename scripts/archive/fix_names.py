import os, urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://cjxqogvtzrvnlsssnfob.supabase.co/rest/v1/species?collection_id=eq.thuc-vat-bien&select=id,vn_name,scientific_name,authorship,vn_alternate_names'
headers = {
    'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    'Authorization': 'Bearer ' + os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    'Accept': 'application/json'
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    
updates = []
for sp in data:
    vn_name = sp.get('vn_name') or ''
    scientific_name = sp.get('scientific_name') or ''
    authorship = sp.get('authorship') or ''
    vn_alternate_names = sp.get('vn_alternate_names') or ''
    
    needs_update = False
    
    # Fix vn_name (split by comma)
    if ',' in vn_name:
        parts = [p.strip() for p in vn_name.split(',')]
        vn_name = parts[0]
        # Append remaining to vn_alternate_names
        extra = ', '.join(parts[1:])
        if vn_alternate_names:
            vn_alternate_names = vn_alternate_names + ', ' + extra
        else:
            vn_alternate_names = extra
        needs_update = True
        
    # Fix scientific_name (if it has > 2 words or contains parenthesis)
    # Most scientific names are 2 words (Genus species). Some are 3 (Genus species var. x)
    # But if authorship is missing and sci name has parenthesis, or starts with a capital after the second word
    if not authorship:
        words = scientific_name.split()
        if len(words) > 2:
            # check if the 3rd word starts with upper case or is '('
            if words[2][0].isupper() or words[2][0] == '(':
                scientific_name = ' '.join(words[:2])
                authorship = ' '.join(words[2:])
                needs_update = True
            elif len(words) > 3 and (words[3][0].isupper() or words[3][0] == '('):
                # e.g., Caulerpa racemosa var. clavifera (Turner) Weber-van Bosse
                scientific_name = ' '.join(words[:3])
                authorship = ' '.join(words[3:])
                needs_update = True
                
    # Additional check: sometimes authorship is appended to scientific_name even if authorship field exists
    # If authorship exists, ensure scientific_name doesn't contain it
    if authorship and authorship in scientific_name:
        scientific_name = scientific_name.replace(authorship, '').strip()
        needs_update = True

    if needs_update:
        updates.append({
            'id': sp['id'],
            'vn_name': vn_name,
            'vn_alternate_names': vn_alternate_names,
            'scientific_name': scientific_name,
            'authorship': authorship
        })

print(f"Found {len(updates)} species to update.")

# Now send updates
update_url = 'https://cjxqogvtzrvnlsssnfob.supabase.co/rest/v1/species?id=eq.{}'
for u in updates:
    id = u.pop('id')
    print(f"Updating {id}: {u['vn_name']} | {u['scientific_name']} | {u['authorship']}")
    req = urllib.request.Request(update_url.format(id), data=json.dumps(u).encode('utf-8'), headers={
        'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY'],
        'Authorization': 'Bearer ' + os.environ['SUPABASE_SERVICE_ROLE_KEY'],
        'Content-Type': 'application/json'
    }, method='PATCH')
    try:
        with urllib.request.urlopen(req) as resp:
            pass
    except Exception as e:
        print(f"Error updating {id}: {e}")
