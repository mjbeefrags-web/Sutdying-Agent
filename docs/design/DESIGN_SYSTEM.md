# Design system

## Experience intent
Premium, calm, academic: warm paper surfaces against midnight ink, restrained brass/teal accents, generous spacing, readable typography, and one dominant task per screen. Avoid faux parchment textures that reduce legibility and avoid novelty motion in study tasks.

## Tokens (initial, to validate with contrast tooling)
- Background: `#F7F5F0`; surface: `#FFFFFF`; primary ink: `#17212B`; muted ink: `#52616B`.
- Accent: deep teal `#1C625C`; accent hover `#154B47`; focus ring `#155EEF`; danger `#B42318`; success `#1A7F5A`.
- 4px spacing scale; 8px base rhythm; radii 8/12/20px; subtle elevation only for layered panels.
- Display serif for editorial headings; neutral sans-serif for UI; tabular numerals for timers/progress. Prefer self-hosted licensed fonts or system stack.

## Components and states
Use semantic shadcn/ui primitives backed by Radix where suitable: buttons, inputs, dialog, menu, tabs, tooltip, toast, progress, skeleton. Every async component has loading, empty, error, retry, and success states. Buttons have clear verb labels and disabled reason; destructive actions confirm scope.

## Motion
Motion communicates navigation or state only. Use short opacity/transform transitions; honor `prefers-reduced-motion`; no autoplay, parallax, continuous camera drift, or animated score pressure. GSAP is not a default dependency; consider only for a single authored landing sequence after performance/accessibility review.

## Responsive behavior
Desktop-first study canvas, functional at 320px width. Library provides list on small screens; side panels become drawers. Preserve reading width and controls at 200% zoom. Tokens are centralized as CSS variables and Tailwind theme mappings.
