# DESIGN.md (2026 Edition)

## Visual Theme

- **Quiet UI**: A minimal, sophisticated knowledge tool aesthetic inspired by Linear, Notion, and Apple.
- **Editorial Paper**: The UI should feel like a tidy canvas with warm, muted tones that reduce eye strain.
- **Hierarchy-First**: Visual prominence is achieved through spacing and tone differences rather than heavy shadows or motion.

## Palette

- **Background**: `#f5f4ef` (Global warmth)
- **Paper Tones**:
  - Sidebar/Secondary: `#fcfbf8`
  - Main Area: `#f8fafc`
  - Code/Pre Blocks: `#f5f7fb`
- **Surface**: `#ffffff` (Clean white for primary cards)
- **Accents**: Deep Teal (`#0f766e`) and Soft Teal (`rgba(15,118,110,0.05)`)
- **Text**: Near-black (`#1a1c20`) for sharp readability.
- **Muted text**: Slate gray (`#64748b`).

## Typography

- **Headings**: Use "Outfit" or a similar geometric/editorial sans/serif.
- **Body**: "Inter" or "Noto Sans JP" for high-legibility.
- **Sizing**:
  - Body: 15px - 17px
  - UI Controls: 14px
  - Sub-labels: 12px - 13px
  - *Avoid font sizes below 12px.*

## Components

- **Gallery Tiles**: Static borders that shift in color on focus/hover. No lift (`translateY`).
- **Integrated Modal**: Backdrop using `blur(12px)` and `rgba(255,255,255,0.7)` to maintain background context.
- **Navigable History**: Detail views support "Back" navigation when hopping through nodes (tags). Maintain a breadcrumb or history stack to avoid user disorientation.
- **Copy Buttons**: Large, obvious, and prioritized at the top of the detail view.
- **Pre Blocks**: Mono fonts (JetBrains Mono) with relaxed line height (1.8).

## Layout

- Single centered column (`width: min(1200px, 95%)`) for the main gallery.
- Master-Detail flow: Seamless transition from gallery list to focused modal.
- Generous white space: whitespace is a design element, not "empty space".

## Depth & Motion

- **Shadow**: Lightest possible (`0 8px 24px rgba(0,0,0,0.06)`).
- **Animations**:
  - Hover/Active: 120ms
  - UI transitions: 240ms
  - Page entries: 320ms
- **Transitions**: Smooth easing (`cubic-bezier(0.4, 0, 0.2, 1)`).

## Do's

- Prioritize the "Copy Full Prompt" action.
- Use subtle border color changes to indicate interactivity.
- Keep the interface "Quiet" and professional.

## Don'ts

- Do not use dramatic shadows or neon glows.
- Do not use `transform` for hover states unless essential.
- Do not make the UI louder than the content (images/prompts).

## Agent Prompt Guide

- Maintain the "Quiet UI" aesthetic: thin borders, paper tones, soft shadows.
- Ensure all copy-paste actions are single-click and prominent.
- Optimize for high-legibility typography and generous spacing.
