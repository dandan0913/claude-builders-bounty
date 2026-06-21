# CLAUDE.md

This file provides project context and rules for Claude Code (claude-code.ai) when working on this Next.js 15 SaaS project with SQLite.

## Stack & Versions

- **Framework**: Next.js 15 (App Router, Turbopack for dev)
- **Language**: TypeScript 5.x (strict mode enabled)
- **Database**: SQLite via `better-sqlite3` driver with Drizzle ORM
- **Styling**: Tailwind CSS 4 with `@theme` config in `src/app/globals.css`
- **Font**: Geist Sans + Geist Mono (via `next/font/google`)
- **Package Manager**: npm
- **Linting**: ESLint with `eslint-config-next`

### Key Dependencies
```
next@^15.x.x
react@^19.x.x
react-dom@^19.x.x
better-sqlite3@^11.x.x
drizzle-orm@^0.x.x
drizzle-kit@^0.x.x
tailwindcss@^4.x.x
```

## Folder Structure

```
src/
├── app/                    # Next.js App Router (routes, layouts, pages)
│   ├── layout.tsx          # Root layout (font setup, metadata)
│   ├── page.tsx            # Home page
│   ├── globals.css         # Tailwind + CSS variables
│   └── ...                 # Route groups, nested routes
├── components/             # React components (UI + business)
│   ├── ui/                 # Primitive UI components (buttons, inputs, cards)
│   └── ...                 # Feature components
├── lib/                    # Shared utilities & config
│   ├── db/                 # Database layer
│   │   ├── schema.ts       # Drizzle table definitions (source of truth)
│   │   ├── index.ts        # Database connection singleton + drizzle instance
│   │   └── migrations/     # Drizzle Kit migration files (generated)
│   ├── utils.ts            # General helpers (clsx, cn, formatDate, etc.)
│   └── validation.ts       # Zod schemas for form/API validation
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript type definitions
├── middleware.ts           # Next.js middleware (auth guards, redirects)
└── styles/                 # Additional CSS (rarely needed — use Tailwind)
public/                     # Static assets (images, favicon, manifest)
```

### Naming Conventions

- **Files**: kebab-case for components and pages (`user-profile.tsx`, `dashboard-page.tsx`)
- **Components**: PascalCase, co-located with their route or placed in `components/`
- **Hooks**: camelCase with `use` prefix (`useAuth.ts`, `useLocalStorage.ts`)
- **Types/Interfaces**: PascalCase, prefixed with `I` only when distinguishing from values is necessary
- **Database tables**: snake_case in schema (`user_accounts`, `sessions`)
- **Database columns**: snake_case in schema (`first_name`, `created_at`), camelCase in TS types
- **Lib files**: kebab-case (`utils.ts`, `validation.ts`)
- **Imports**: always use `@/` alias (e.g., `@/lib/db/schema`, `@/components/ui/button`)

## Database & Migration Rules

### Schema Definition (`src/lib/db/schema.ts`)

- Define ALL tables in a single schema file using Drizzle's `pg`/`sqlite` schema DSL
- Every table MUST have: `id` (text/uuid primary key), `created_at` (datetime, default now), `updated_at` (datetime)
- Use `sqliteTable` from `drizzle-orm/better-sqlite3`
- Index frequently queried columns (`email`, `slug`, `status`)
- Use `relations()` API for foreign keys and belongs-to/has-many relationships
- Export a `DatabaseSchema` type that maps table names to their row types

### Connection (`src/lib/db/index.ts`)

- Create a **singleton** database connection using `new Database(':memory:')` or a file path from `DATABASE_URL` env var
- Export a `db` instance from `drizzle(dbInstance)` — this is the ONLY place to call `db.execute()`
- Never create multiple connections; use the exported singleton everywhere
- Wrap the connection in a try/catch with a clear error message if the DB file is missing

### Migrations

- Use `drizzle-kit push` for development (auto-sync schema to DB)
- Use `drizzle-kit generate` + `drizzle-kit migrate` for production deployments
- Migration files live in `src/lib/db/migrations/` — never edit them manually
- All schema changes MUST go through `schema.ts` first, then regenerate migrations
- Before pushing to production, always run `drizzle-kit push --dry-run` to review changes

### Query Patterns

- Use Drizzle's query builder (`select()`, `insert()`, `update()`, `delete()`) — never raw SQL except for complex analytics
- For reads: prefer `db.select().from(table).where(...).limit(...)`
- For writes: always wrap in transactions for multi-table operations
- Use `sql` template from `drizzle-orm` only when the query builder cannot express the operation
- Cache frequent reads with in-memory Map (TTL-based) — SQLite is fast but not free

## Development Commands

```bash
npm run dev            # Start dev server with Turbopack
npm run build          # Production build
npm run start          # Start production server
npm run lint           # Run ESLint
npm run lint:fix       # Auto-fix linting issues
npm run db:push        # Push schema to DB (development)
npm run db:generate    # Generate migration files
npm run db:migrate     # Run pending migrations (production)
npm run db:studio      # Open Drizzle Studio (GUI)
```

## Component Patterns

### Server Components (Default)

- All components in `app/` are **Server Components by default** (no `"use client"` directive)
- Only add `"use client"` when you need: event handlers, `useState`/`useEffect`, browser APIs
- Server components fetch data directly — no prop drilling for data

### Client Components

- Place in `components/ui/` for primitives (Button, Input, Modal)
- Place in `components/features/` for interactive feature components
- Keep client components thin — delegate logic to hooks in `hooks/`

### Component Structure

```tsx
// src/components/ui/button.tsx
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({ className, variant = "primary", size = "md", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-colors",
        // ... variant and size classes
        className
      )}
      {...props}
    />
  );
}
```

### Data Fetching

- Fetch data in Server Components or Route Handlers
- Use `async` page components: `export default async function Page() { const data = await fetchData(); }`
- For shared data, use React Context or a lightweight store (Zustand for client-side state)
- Never fetch data in a Client Component — move to Server Component or API route

### API Routes (Route Handlers)

- Place in `src/app/api/` using the App Router route handler convention
- All API routes MUST validate input with Zod schemas in `src/lib/validation.ts`
- All API routes MUST return JSON with a consistent envelope: `{ success: boolean; data?: T; error?: string }`
- Use `NextResponse.json()` for responses
- Middleware (`src/middleware.ts`) handles auth checks — API routes should NOT re-check auth

## What We Do NOT Do (And Why)

### No `pages/` directory
We use the App Router exclusively. The legacy `pages/` directory is not needed and causes confusion.

### No class components
All components are functional. Class components are legacy React and add unnecessary boilerplate.

### No prop drilling for data
Pass data via Server Components or React Context. Don't pass props through 4+ levels of components.

### No raw SQL queries in the application layer
Drizzle ORM abstracts SQL. Raw SQL leaks into tests and migrations only. This prevents vendor lock-in and ensures type safety.

### No `.env` files committed to git
Environment variables go in `.env.local` (gitignored). Use `dotenv` only for local dev scripts, never in production code.

### No `any` types
Strict TypeScript is enforced. If you need `any`, the type definition is incomplete — fix the type instead.

### No `console.log` in production code
Use a proper logger (e.g., `pino` or `console` filtered by `NODE_ENV`). Debug logs leak sensitive data.

### No server-side `useState` or `useEffect`
These hooks are client-only. If a Server Component needs state, lift it to a parent Client Component.

### No `useMemo`/`useCallback` without profiling
React 18+ handles optimization well. Premature memoization adds complexity. Profile first, optimize second.

### No manual CSS files alongside components
Use Tailwind utility classes. One global `globals.css` for CSS variables and Tailwind imports. No SCSS, no CSS Modules.

## Error Handling

- Wrap async route handlers in try/catch, returning 400/401/403/404/500 with descriptive messages
- Use `zod` for all input validation — return `400 Bad Request` with field-level errors
- Database errors: never expose raw SQLite errors to the client. Map to user-friendly messages.
- Authentication failures: always return `401 Unauthorized` with a generic message (don't reveal if user exists)

## Testing Strategy

- Unit tests for `lib/` utilities (pure functions) using Vitest
- Integration tests for API routes using `@testing-library/react` + MSW
- Component tests for `components/ui/` primitives
- No e2e tests in this template — use Playwright separately if needed

## Security Checklist

- [ ] All user input validated with Zod before reaching the database
- [ ] SQL injection prevented by Drizzle ORM parameterized queries
- [ ] CSRF protection via SameSite cookies
- [ ] Rate limiting on auth endpoints (middleware or route handler)
- [ ] Secrets never logged or exposed in error messages
- [ ] `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY` headers set
