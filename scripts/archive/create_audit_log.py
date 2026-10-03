import os
import sys
import urllib.request
import urllib.error
import json

sys.stdout.reconfigure(encoding='utf-8')

# Supabase Management API
# Ref: https://supabase.com/docs/reference/management-api
# We need the project ref and access token

PROJECT_REF = "cjxqogvtzrvnlsssnfob"

# Try to get the access token from env
ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")

if not ACCESS_TOKEN:
    print("No SUPABASE_ACCESS_TOKEN found.")
    print("Alternative: Create the table via Supabase Dashboard SQL Editor.")
    print()
    print("Navigate to: https://supabase.com/dashboard/project/cjxqogvtzrvnlsssnfob/sql/new")
    print("And run this SQL:")
    print()
    print("""CREATE TABLE IF NOT EXISTS public.audit_log (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),
    user_email text,
    action text not null,
    collection_id text,
    species_id text,
    details text,
    old_data jsonb,
    new_data jsonb
);

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "service_role_all" ON public.audit_log
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Allow authenticated users to read
CREATE POLICY "authenticated_read" ON public.audit_log
  FOR SELECT
  TO authenticated
  USING (true);
""")
    sys.exit(0)

url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

sql = """
CREATE TABLE IF NOT EXISTS public.audit_log (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),
    user_email text,
    action text not null,
    collection_id text,
    species_id text,
    details text,
    old_data jsonb,
    new_data jsonb
);

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON public.audit_log
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "authenticated_read" ON public.audit_log
  FOR SELECT
  TO authenticated
  USING (true);
"""

data = json.dumps({"query": sql}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        print("Success!", result)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Error {e.code}: {body}")
