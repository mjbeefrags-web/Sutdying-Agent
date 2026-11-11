# CI/CD

GitHub Actions workflow runs on pull requests and main: Python format/lint/type/test, frontend lint/typecheck/test/build, Compose config validation, dependency audit and container build. Use pinned action SHAs in production hardening, minimal `permissions`, no production secrets in pull-request jobs, and OIDC for deploy. Main deployment requires protected environment approval and successful artifacts built from the same commit.

Release process: semantic version/release notes → immutable image digest → migration dry-run/backup confirmation → staged deploy → health/smoke checks → promotion. Rollback application image independently; database migrations must remain backward-compatible. Dependency and base-image updates are scheduled; critical CVEs trigger expedited patch and rebuild.

Phase 1 workflow is intentionally a validation skeleton; publishing, registry, scanning policies, deploy credentials and release automation are not enabled.
