import { defineConfig, globalIgnores } from 'eslint/config'
import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // ponytail: 14 existing mount-time setState (localStorage/theme reads) — warn, refactor gradually
      'react-hooks/set-state-in-effect': 'warn',
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
