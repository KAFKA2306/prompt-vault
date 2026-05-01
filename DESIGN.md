# DESIGN.md

## Visual Theme
- Warm editorial canvas with a paper-like feel.
- Quiet, minimal, and copy-first.
- The page should feel like a tidy knowledge tool, not a marketing site.
- Use calm contrast, soft surfaces, and restrained color.

## Palette

- UI Background: `#f4f1ea` to `#f7f4ee` (Warm editorial canvas / 疲労の少ない紙のような温かみ)
- UI Surface: `#ffffff` (Clean white negative space)
- Brand Accents (from DB): Pastel Blue, Lavender, Soft Cyan, Light Navy, with small Pink details.
- UI Primary: Deep Teal (`#0f766e`) / UI Secondary: Muted Blue (`#2563eb`)
- Text: Near-black (`#111827`) for readability.
- Muted text: Slate gray (`#5b6472`).
- Avoid: Neon, dark cyberpunk, saturated purple dominance, and heavy glassmorphism.


## Typography

- Use a serif display face for headings.
- Use a clean sans-serif for body text and controls.
- Headings should be compact and editorial.
- Body copy should be readable, modest in size, and relaxed in line height.
- Avoid technical or futuristic type treatments.


## Components

- Hero: short statement, one strong heading, one supporting paragraph.
- Search field: full-width, simple, prominent.
- Gallery: image-first tile grid, clean and browsable.
- Gallery tiles: hover effects that subtly lift to indicate clickability.
- Modal: focused overlay for viewing the full image and copying the prompt instantly.
- Copy buttons: prominent, placed at the top of the modal for zero-friction copying.
- Prompt blocks: monospaced, readable, but secondary to the one-click copy action.


## Layout

- Two-column desktop layout: sidebar for searching/filtering, main area for the Image Gallery.
- Stack to one column on tablet and mobile.
- Keep the sidebar narrower than the gallery column.
- Preserve generous outer padding and medium internal spacing.
- Keep the page centered with a strong max width.


## Depth

- Use light borders and soft shadows only.
- Prefer surface layering over dramatic blur or heavy glow.
- Hover states may lift slightly, but should stay subtle.
- Keep active states clear through border color and shadow, not large motion.


## Do's

- Keep the UI simple, image-first, and instantly copyable.
- Favor whitespace over decoration.
- Use warm neutrals and one calm accent.
- Make hierarchy obvious at a glance.
- Preserve the "Gallery -> Modal -> Copy" flow. User experience must prioritize copying the full prompt without scrolling.


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

- If generating or editing UI for this project, preserve the image-first gallery and modal copy flow.
- Match the warm editorial style, serif headings, and restrained teal accent.
- Users do not read complex documentation or perform granular copy-pasting. Always provide a single, obvious "Copy Full Prompt" button at the top of the modal.
- Optimize for clarity and speed, not visual novelty.
- Treat this project as a small static utility, not a full product suite.

