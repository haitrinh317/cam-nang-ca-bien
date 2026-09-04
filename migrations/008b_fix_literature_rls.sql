-- Fix RLS infinite recursion: user_roles has its own RLS that causes loop
-- when literature_sources policy references it.
-- Solution: Drop the recursive policy, keep simple public SELECT,
-- and add a permissive policy for all authenticated users (admin uses auth).

-- Drop the problematic policy
DROP POLICY IF EXISTS "Admin full access to literature" ON literature_sources;
DROP POLICY IF EXISTS "Public can read visible literature" ON literature_sources;

-- Public (anon) can read all visible literature
CREATE POLICY "Anyone can read visible literature"
  ON literature_sources FOR SELECT
  USING (is_visible = true);

-- Authenticated users can read ALL literature (including hidden) 
CREATE POLICY "Authenticated can read all literature"
  ON literature_sources FOR SELECT
  TO authenticated
  USING (true);

-- Authenticated users can insert/update/delete
CREATE POLICY "Authenticated can modify literature"
  ON literature_sources FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);
