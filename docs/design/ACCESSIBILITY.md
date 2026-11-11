# Accessibility

Target WCAG 2.2 AA and test against real keyboard and assistive technology users before beta. Semantic HTML, landmarks, heading hierarchy, labels, accessible names, clear error association, skip link, visible focus, and logical focus management are required. No keyboard traps; dialogs return focus; drag interactions have buttons/keyboard alternatives.

Contrast target 4.5:1 normal text and 3:1 large text/UI boundaries; do not encode mastery or processing state by color alone. Support 200% zoom/reflow, 320px width, reduced motion, high contrast, and OS text scaling. Respect user-configured timers and allow pause in non-exam study. Announce async upload/job changes politely without repeating progress noise.

3D canvas has accessible name and companion DOM controls; every scene action can be completed in 2D. Charts provide data table/summary. Timed exams expose time clearly and offer an accommodation policy; no timer starts before explicit consent. Reading view supports keyboard navigation, selectable text, adjustable type size/line width, and citation links.

Automated axe checks are necessary but insufficient; perform manual keyboard, NVDA/VoiceOver, zoom, reduced motion, contrast and WebGL-disabled checks.
