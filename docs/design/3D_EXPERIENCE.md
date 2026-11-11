# 3D library experience

## Scene and interaction
An optional, quiet digital reading room. A low-poly/optimized architectural shell, a few distinct course shelves, soft baked/static lighting, and clear hover/focus labels. Selecting a shelf opens the same course workspace as the 2D list. Camera motion is user-triggered, bounded, and reversible; avoid simulated walking and motion-heavy transitions.

## Implementation and performance
Next.js client-only scene boundary with React Three Fiber + Drei. Lazy-load scene and assets; show semantic 2D course list immediately. Use instancing for repeated objects, compressed textures/geometry, static shadows, capped DPR (1–1.5), no post-processing by default, pause render loop while idle/hidden, dispose resources on unmount. Set a small asset budget (initial target <2MB compressed scene assets) and monitor route LCP/INP on low-end integrated graphics.

## Accessibility and fallback
Canvas is decorative/navigation enhancement, not the sole representation. Provide synchronized DOM list, keyboard-operable course selection, visible focus, screen-reader labels, reduced-motion mode, and a “Use 2D library” control. Detect WebGL/context loss and show fallback without losing selected course. Never place important text exclusively in the canvas.

## Acceptance
Core browsing works with WebGL disabled, keyboard only, reduced motion, and screen reader. Test at least one integrated-GPU/lower-tier device. Track frame time and memory; disable scene complexity if performance budget is exceeded.
