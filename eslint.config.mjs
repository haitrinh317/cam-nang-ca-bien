import { defineConfig, globalIgnores } from 'eslint/config'
import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // Remaining mount-time setState are disabled inline with a reason; new ones should be fixed, not disabled
      'react-hooks/set-state-in-effect': 'warn',
      // ponytail: plain <img> on purpose — species photos are already WebP in Supabase Storage;
      // next/image would route thousands of source images through Vercel Image Optimization (billed quota).
      // Upgrade path: custom loader (Supabase image transform) if LCP becomes an issue.
      '@next/next/no-img-element': 'off',
      // Vietnamese UI copy uses literal quotes in JSX text; React renders them safely
      'react/no-unescaped-entities': 'off',
      // `({ books, ...col }) => col` is an intentional omit pattern
      '@typescript-eslint/no-unused-vars': ['warn', { ignoreRestSiblings: true }],
    },
  },
  globalIgnores([
    // Default ignores of eslint-config-next
    '.next/**',
    'out/**',
    'build/**',
    'next-env.d.ts',
    // Project folders that are not app source
    '_offline/**',
    '.backups/**',
    'scratch/**',
    'scripts/**',
    'data/**',
    'Documents/**',
    'public/**',
    '.agents/**',
  ]),
])

export default eslintConfig
