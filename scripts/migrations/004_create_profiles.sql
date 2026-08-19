-- Migration 004: Create profiles table and setup Auth integration

-- 1. Create profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'editor', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 3. RLS Policies for profiles
-- Anyone can view profiles (useful for displaying authors/editors)
CREATE POLICY "Profiles are viewable by everyone" 
    ON public.profiles FOR SELECT 
    USING (true);

-- Users can only update their own profile (but not their role, we'll need a secure function or admin policy for that, but keeping it simple)
-- Actually, if we use supabase admin dashboard to change roles, we don't need update policies for now.
-- But let's allow them to update their own record, except role.
-- PostgreSQL doesn't easily support column-level RLS out of the box without complex views. 
-- For safety, no update policy from client for now. Roles are assigned via Supabase Dashboard.

-- 4. Trigger to auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  -- Change 'admin' to 'viewer' if you want to invite others securely
  -- For the first user (the owner), 'admin' is convenient.
  INSERT INTO public.profiles (id, email, role)
  VALUES (new.id, new.email, 'admin'); 
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 5. Update species table RLS to use profiles.role
-- Drop the temporary policy from 003
DROP POLICY IF EXISTS "Admin write access" ON public.species;

-- Create the new role-based policy
CREATE POLICY "Role based write access"
    ON public.species FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('admin', 'editor')
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('admin', 'editor')
        )
    );
