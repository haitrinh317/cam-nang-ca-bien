-- Migration 009: Fix 2 lỗ hổng bảo mật
-- Date: 2026-09-07
--
-- #1: user_roles — policy tự tham chiếu gây đệ quy vô tận (42P17)
-- #2: audit_log  — RLS chưa bật, anon key đọc/ghi thoải mái
--
-- Chạy trên Supabase SQL Editor:
--   https://supabase.com/dashboard/project/cjxqogvtzrvnlsssnfob/sql/new

-- ╔══════════════════════════════════════════════════════════════╗
-- ║  PHẦN 1: Fix user_roles — Xóa đệ quy, dùng SECURITY DEFINER║
-- ╚══════════════════════════════════════════════════════════════╝

-- 1a. Drop policy gây đệ quy
DROP POLICY IF EXISTS "Admins can manage all roles" ON user_roles;

-- 1b. Tạo function is_admin() — SECURITY DEFINER bypass RLS
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER   -- chạy với quyền owner, bỏ qua RLS
STABLE             -- kết quả ổn định trong 1 transaction
AS $$
  SELECT EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = auth.uid() AND role = 'admin'
  )
$$;

-- 1c. Tạo lại policy dùng function (không đệ quy)
CREATE POLICY "Admins can manage all roles" ON user_roles
  USING (is_admin());

-- 1d. Update current_user_role() cũng dùng SECURITY DEFINER
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS TEXT
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT role FROM user_roles WHERE user_id = auth.uid()
$$;


-- ╔══════════════════════════════════════════════════════════════╗
-- ║  PHẦN 2: Secure audit_log — Bật RLS + policy chặt           ║
-- ╚══════════════════════════════════════════════════════════════╝

-- 2a. Bật RLS (nếu chưa bật — idempotent)
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- 2b. Drop policy cũ nếu có (idempotent)
DROP POLICY IF EXISTS "Service role can insert audit logs" ON audit_log;
DROP POLICY IF EXISTS "Admins can read audit logs" ON audit_log;

-- 2c. Chỉ service_role được INSERT (server-side API routes)
CREATE POLICY "Service role can insert audit logs"
  ON audit_log FOR INSERT
  TO service_role
  WITH CHECK (true);

-- 2d. Chỉ admin đọc được (dùng is_admin() đã fix ở trên)
CREATE POLICY "Admins can read audit logs"
  ON audit_log FOR SELECT
  TO authenticated
  USING (is_admin());

-- Không tạo UPDATE/DELETE policy = mặc định bị chặn khi RLS bật
-- → Audit log bất khả xâm phạm (immutable)


-- ╔══════════════════════════════════════════════════════════════╗
-- ║  VERIFY                                                      ║
-- ╚══════════════════════════════════════════════════════════════╝

-- Kiểm tra RLS đã bật
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND tablename IN ('audit_log', 'user_roles');

-- Kiểm tra policies
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public' AND tablename IN ('audit_log', 'user_roles');
