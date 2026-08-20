-- Migration 003: User roles table
-- Run AFTER enabling Supabase Auth in Dashboard
-- Date: 2026-08-19

-- User roles: admin | editor | viewer
CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role    TEXT NOT NULL DEFAULT 'viewer'
    CHECK (role IN ('admin', 'editor', 'viewer')),
  granted_at TIMESTAMPTZ DEFAULT now()
);

-- Only admins can see all roles; users can see their own
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own role" ON user_roles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all roles" ON user_roles
  USING (
    EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin')
  );

-- ╔══════════════════════════════════════════════════════════════╗
-- ║  BƯỚC 2 — Chạy SAU KHI đã login lần đầu tại /login         ║
-- ║  (để Supabase tạo record trong auth.users trước)            ║
-- ╚══════════════════════════════════════════════════════════════╝
INSERT INTO user_roles (user_id, role)
SELECT id, 'admin' FROM auth.users WHERE email = 'haitrinh082@gmail.com'
ON CONFLICT (user_id) DO UPDATE SET role = 'admin';


-- Helper function: get current user role
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS TEXT LANGUAGE sql SECURITY DEFINER AS $$
  SELECT role FROM user_roles WHERE user_id = auth.uid()
$$;

-- RLS update: species writes require editor+ role
-- (Reads remain open to anon for public browsing)
CREATE POLICY "Editors can insert species" ON species
  FOR INSERT WITH CHECK (current_user_role() IN ('admin', 'editor'));

CREATE POLICY "Editors can update species" ON species
  FOR UPDATE USING (current_user_role() IN ('admin', 'editor'));

CREATE POLICY "Admins can delete species" ON species
  FOR DELETE USING (current_user_role() = 'admin');
