# ADR-007: Personal organization tenant boundary

- Status: Accepted for MVP
- Context: Individual accounts are initial target; institutional collaboration may follow.
- Decision: Every user owns a personal organization; domain resources belong to it and access is membership-authorized. Institutional organizations remain future.
- Alternatives: User ID directly on every row; shared global course library; full multi-org administration from day one.
- Consequences: Tenant-aware constraints and policy tests are mandatory; organization ID must not be trusted from client input. RLS is optional defense-in-depth after pool-safety design.
