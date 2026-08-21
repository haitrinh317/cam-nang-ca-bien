import os, urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')
url = 'https://cjxqogvtzrvnlsssnfob.supabase.co/rest/v1/species?collection_id=eq.thuc-vat-bien&select=id,vn_name,scientific_name,authorship'
headers = {
    'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    'Authorization': 'Bearer ' + os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    'Accept': 'application/json'
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    with open('check_names.txt', 'w', encoding='utf-8') as f:
        for sp in data:
            f.write(f"{sp['id']} | {sp['vn_name']} | {sp['scientific_name']} | {sp['authorship']}\n")
