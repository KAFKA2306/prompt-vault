# DESIGN.md

## Visual Theme
- Warm editorial canvas with a paper-like feel.
- Quiet, minimal, and copy-first.
- The page should feel like a tidy knowledge tool, not a marketing site.
- Use calm contrast, soft surfaces, and restrained color.

## Palette
- Background: `#f7f4ee`
- Surface: `#ffffff` with slight warmth
- Border: soft neutral gray
- Primary accent: deep teal
- Secondary accent: muted blue
- Text: near-black
- Muted text: slate gray
- Avoid neon, saturated purple dominance, and heavy glassmorphism.

## Typography
- Use a serif display face for headings.
- Use a clean sans-serif for body text and controls.
- Headings should be compact and editorial.
- Body copy should be readable, modest in size, and relaxed in line height.
- Avoid technical or futuristic type treatments.

## Components
- Hero: short statement, one strong heading, one supporting paragraph.
- Stats cards: small, quiet, informational.
- Search field: full-width, simple, prominent.
- Filter chips: rounded, restrained, low noise.
- Content cards: white surfaces, subtle border, modest hover lift.
- Detail panel: structured blocks with clear hierarchy.
- Code-style or prompt blocks: monospaced, readable, not overly styled.
- Copy buttons: obvious but not dominant.

## Layout
- Two-column desktop layout: sidebar for browsing, main area for detail.
- Stack to one column on tablet and mobile.
- Keep the browsing column narrower than the detail column.
- Preserve generous outer padding and medium internal spacing.
- Keep the page centered with a strong max width.

## Depth
- Use light borders and soft shadows only.
- Prefer surface layering over dramatic blur or heavy glow.
- Hover states may lift slightly, but should stay subtle.
- Keep active states clear through border color and shadow, not large motion.

## Do's
- Keep the UI simple and copyable.
- Favor whitespace over decoration.
- Use warm neutrals and one calm accent.
- Make hierarchy obvious at a glance.
- Preserve the current information architecture.

## Don'ts
- Do not introduce a complex dashboard aesthetic.
- Do not add decorative noise, chrome, or dense gradients.
- Do not use strong neon, cyberpunk, or overly glossy surfaces.
- Do not expand the layout into multiple extra panels.
- Do not make actions visually louder than the content.

## Responsive
- On small screens, collapse to one column.
- Keep buttons full width where needed.
- Prevent content blocks from feeling cramped.
- Maintain readable text sizes and enough vertical spacing.

## Agent Prompt Guide
- If generating or editing UI for this project, preserve the existing copy-first static catalog structure.
- Match the warm editorial style, serif headings, and restrained teal accent.
- Keep all interactions simple: search, filter, browse, copy.
- Optimize for clarity and speed, not visual novelty.
- Treat this project as a small static utility, not a full product suite.
