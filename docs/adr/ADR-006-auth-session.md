# ADR-006: Server-managed secure sessions

- Status: Accepted for the M1 MVP; reassess before institutional launch
- Context: Browser product needs revocation and simple CSRF controls; bearer tokens in local storage raise exposure.
- Decision: M1 uses local email/password with verified email, Argon2id password hashes, opaque server-managed sessions, HttpOnly/SameSite cookies, a separate CSRF token, same-origin checks and server-side revocation. Production/staging cookies are Secure and use `__Host-` names. Reassess a maintained identity provider and MFA before institutional launch.
- Alternatives: JWT in local storage, third-party OAuth-only, enterprise SSO first.
- Consequences: PostgreSQL session storage and Redis rate limiting are required; cookie/proxy settings are environment-specific. The current direct-peer IP key is suitable only for local development until trusted proxy hops are configured. Local SMTP is only a development integration; no production identity/email provider is selected.
