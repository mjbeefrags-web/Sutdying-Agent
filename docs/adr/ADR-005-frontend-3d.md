# ADR-005: Optional React Three Fiber library

- Status: Accepted with progressive enhancement constraint
- Context: Immersive library differentiates product but must not impair access or performance.
- Decision: Next.js/React with client-only lazy R3F/Drei scene and equal semantic 2D library path.
- Alternatives: Three.js imperative scene, DOM-only library, WebGL-only navigation.
- Consequences: WebGL capability, reduced motion, keyboard and context loss need explicit handling; scene cannot gate learning tasks or initial rendering.
