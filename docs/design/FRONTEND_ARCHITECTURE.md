# Frontend architecture

Next.js App Router, React, TypeScript strict mode, Tailwind CSS and shared shadcn/ui-inspired primitives; feature-oriented modules under `components`, shared API/types under `lib`, server components for route setup and client components only for interaction. M1 uses a small hand-maintained typed API client; it is not generated from OpenAPI yet. Keep contracts aligned with FastAPI and enforce authorization only on the API.

Implemented M1 routes: `/`, `/login`, `/register`, `/verify-email`, `/reset-password`, `/app/library`, `/app/courses/[courseId]`, and `/app/settings/profile`. The authenticated client shell resolves the server session and redirects unauthenticated users; API authorization is still mandatory. Other planned routes include `/app/courses/[courseId]/read/[documentId]`, `/app/courses/[courseId]/tutor`, `/app/courses/[courseId]/exams/[examId]`, `/app/courses/[courseId]/cards`, and `/app/analytics`; they are not implemented.

Server state uses a query/cache layer only when justified; local ephemeral state stays in components. Forms validate with shared contracts; loading/error/empty states are designed first. Avoid persisting sensitive document text or tokens in local storage. Uploads use resumable/presigned flow later. Three.js is lazy-loaded and isolated; WebGL must never block initial route render.

## Quality
Strict TS, ESLint, formatter, component tests for state/keyboard behavior, Playwright smoke flows, axe checks, visual review for reading and library at narrow/wide viewports. Observe Core Web Vitals by route. Bundle budgets and image/scene optimization are CI checks once baseline is measured.
