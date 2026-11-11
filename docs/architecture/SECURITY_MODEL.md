# Security and privacy model

## Assets and trust boundaries
Assets: credentials/sessions, lecture bytes and extracted text, embeddings, prompts/answers, learning history, billing identity, and operational secrets. Boundaries: browser↔edge proxy, API↔database/cache/storage, worker↔providers, CI↔registry/deployment. Threat actors include malicious authenticated students, compromised accounts, hostile uploaded documents, third-party provider compromise, and accidental operator access.

## Controls
- TLS end-to-end where supported; M1 uses an opaque random session token in an HttpOnly, SameSite=Lax cookie and stores only its SHA-256 hash. A separate readable CSRF cookie is checked against both the request header and stored hash. Production/staging cookie names use the `__Host-` prefix and Secure; session secrets never enter local storage.
- M1 password hashes use the maintained `pwdlib` Argon2id configuration; email must be verified before login. Password reset and logout revoke active sessions. MFA and third-party identity remain future decisions.
- Deny-by-default authorization at every course access; derive scope through authenticated organization membership and conceal foreign IDs with 404. Cross-tenant negative tests are release-blocking. PostgreSQL RLS is not enabled.
- Rate quotas use Redis and fail closed when Redis is unavailable. Current IP-based auth limits use the direct request peer; do not enable untrusted `X-Forwarded-For` parsing. Configure explicit trusted proxy hops before production IP-aware quotas.
- Verification/reset tokens are stored as hashes; only the encrypted token copy needed by the email outbox is persisted, and successful outbox delivery clears the payload. `OUTBOX_ENCRYPTION_KEY` must be a stable Fernet key; rotation requires a planned re-encryption/drain procedure.
- Validate upload extension, MIME and file signature; size/page/time limits; quarantine before parse; malware scanning where supported; isolate parsers with resource limits and no network access. Never execute document content.
- Treat retrieved text as untrusted data, not instructions. Separate system policy from quoted evidence, delimit sources, disallow tool selection from content, and screen for prompt injection. Model output never grants authority or performs sensitive actions.
- Secrets through deployment secret manager; `.env` local-only and ignored. Least-privilege DB/service accounts; no secrets in logs; rotate/revoke procedure.
- Minimize retained prompts/content; define deletion propagation to object store, DB, vectors, caches and provider retention. Audit administrative access without capturing sensitive payloads.
- Rate limits, upload quotas, per-user AI token/cost budgets, concurrency limits, idempotency, abuse monitoring, dependency patching, backups encrypted and access-logged.

## Security headers and browser
The local Nginx proxy sets basic content-type, referrer, and frame headers only. Production edge supplies HSTS after HTTPS termination and a CSP with nonce/asset allowlists (Three.js assets considered); establish nonce handling before enabling CSP. Do not enable broad CORS; allow only configured frontend origin. Cookie domain and proxy trust must be explicit.

## Incident and compliance
Maintain incident severity/escalation, provider breach response, key rotation, deletion/export procedures, and tested restore. Complete DPIA/privacy counsel review, regional residency and FERPA/GDPR applicability before institutional or regulated claims. No compliance certification is claimed by this foundation.

## Threat scenarios
| Threat | Main mitigation | Verification |
|---|---|---|
| IDOR across courses | tenant-scoped query and policy | cross-tenant integration suite |
| Prompt injection in PDF | untrusted-evidence boundary; no document-driven tools | adversarial retrieval eval |
| Malicious parser file | isolated parsers, resource/time limits | malformed corpus + container limits |
| Cost exhaustion | quotas, max tokens, rate and concurrency controls | load/abuse tests |
| Stolen session | secure cookies, rotation, revocation | auth lifecycle tests |
| Backup disclosure | encryption, least privilege, restore auditing | access review and restore drill |

## M1 verification and remaining controls
Automated tests cover CSRF rejection, wrong-origin auth mutation, password reset and session revocation, expired/used token behavior, and cross-user organization/course access. A live local flow was verified through Compose and Mailpit. Production proxy trust, MFA, data export/deletion, upload scanning/parser isolation, provider data controls, CSP/HSTS deployment, security monitoring and privacy/legal review remain incomplete.
