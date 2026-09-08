---
name: web-design-taste
description: tcdw's personal visual design language for web and React Native UI — semantic primary/accent color aliases over raw Tailwind palettes, rounded sans typography with no decorative English, generous radii and spacing, first-class dark mode, and restrained color used as marks rather than areas. Use when designing, styling, or restyling any page, screen, or component for tcdw, and when reviewing a visual draft before presenting it. Do NOT use for copywriting or information architecture decisions.
---

# Web Design Taste (tcdw)

> Restrained, rounded, roomy. Color is semantic and rare. Decoration that only signals "designed" gets cut.

## Reference Implementations

Read these before proposing a new visual direction; they are the baseline, not this document:

| Project | Stack | What it establishes |
| --- | --- | --- |
| `blog` | Astro + Tailwind v4 | The canonical `@theme` block, dark mode, banner/backdrop composition |
| `bilisound` | Expo + NativeWind + gluestack-ui | Semantic token roles, radius vocabulary, interaction states |
| `im.tcdw.net` | Astro + Tailwind v4 | The same `@theme`, applied to a single dense page |

Explicit instructions in the current conversation win over this file. When tcdw overrides a rule here, that is new evidence — offer to update this skill.

## Color

**Never write a raw Tailwind palette name in a component.** Define semantic aliases once, then use only those:

```css
@theme {
  --color-primary-50: var(--color-sky-50);
  /* … 100 through 950 */
  --color-accent-500: var(--color-amber-500);
  --color-secondary-500: var(--color-gray-500);
}
```

There are exactly three roles:

| Role | Base palette | Used for |
| --- | --- | --- |
| `primary-*` | per-project hue (sky / teal) | Identity, links, resting emphasis |
| `accent-*` | per-project hue (amber / blue) | A small distinct mark — the *currently playing* item, a category label, a byline |
| `secondary-*` | **always gray** | Everything neutral: body text, borders, surfaces, disabled and muted states |

- The **structure** is fixed; the **palette is per-project**. `blog` and `im.tcdw.net` map primary→sky, accent→amber; `bilisound` uses a teal primary (`#00BA9D`) with a blue accent. Retheming must be a one-line change, never a find-and-replace across templates.
- **`accent-*` is never a large area.** It marks one thing.
- `secondary-*` is the odd one out: it is essentially always a **gray ramp**, and it stays gray across projects even when primary and accent are rethemed. Naming it `secondary` rather than `gray` is deliberate — it keeps the neutral swappable in one place and lets dark mode flip the whole ramp (`bilisound` flips secondary 0↔950 exactly like primary).
- Write `secondary-*` rather than a naked `gray-*` wherever the alias exists. `blog` still writes `gray-*` directly — that is drift to clean up, not a counter-example. Never `slate`/`zinc`.
- In the RN app the same roles also appear as gluestack's finer-grained tokens (`typography-*`, `background-*`, `outline-*`); use those there.
- Color is for *text marks*, not areas. A tinted chip keeps neutral text (`bg-primary-50` + `text-secondary-800`).
- De-emphasize with `opacity-60`, not by inventing a lighter gray.
- No tinted zone backgrounds, no accent bar across the top of a card, no colored section rules.

### Dark mode is first class

Every color declaration is paired: `text-primary-600 dark:text-primary-400`, `bg-white dark:bg-gray-950`. `bilisound` goes further and **flips the entire ramp** (950↔0) rather than hand-picking dark values. A design with no dark story is unfinished — say so rather than shipping it silently.

## Typography

- **Rounded sans, never serif.** House stack: `ChillRoundF, -apple-system, "Microsoft YaHei", sans-serif`.
- **No decorative English.** No bilingual headings, no `Who` / `Now` / `Stack` micro-labels beside a Chinese title, no `A 5-Minute Intro` kickers.
- **No `uppercase` and no wide `tracking-[0.2em+]` as ornament.** Small-caps-ish label styling is a tell of template design.
- A section heading is a bold Chinese title and nothing else — no rule line, no color block, no counter.
- `body { text-autospace: normal }` wherever CJK and Latin mix.
- Where a size-token system exists (`--fs-*`), the template must not hardcode `text-sm`; one hardcoded size breaks responsive and print scaling.

## Shape & Surface

- Radii are generous. Vocabulary in frequency order: `rounded-full` for circular hit targets and pills, `rounded-lg` as the everyday default, `rounded-xl`/`rounded-2xl` for avatars and cards. **Never a hairline radius** (`rounded-[2px]`).
- Large surfaces may go squircle where supported:

  ```css
  border-radius: 1.5rem;
  @supports (corner-shape: squircle) { border-radius: 3rem; corner-shape: squircle; }
  ```

- Default page surface: white card, `rounded-2xl`, soft shadow, on a lightly tinted background.
- `backdrop-blur` is allowed **over imagery** (blog's `bg-white/80 dark:bg-gray-950/70 backdrop-blur-xl` panel over a photographic banner). It is not generic decoration — no glassmorphism on a flat background.
- No borders on images. No paper/newspaper pastiche (off-white paper tints, top rules, `#fffdfa`).
- Banned styles: glow, exaggerated gradients, SaaS-landing-page look — and **editorial print pastiche**, for the same reason. Both are costumes.
- Prefer whitespace and a single card edge over dividers; drop hairline column separators and let the grid gap work.

## Icons

- Two sets, split by role, never mixed for variety: **Simple Icons** (`simple-icons:github`, `simple-icons:x`) for brand marks, **Remix Icon** (`ri:mail-line`, `ri:global-line`) for generic UI glyphs. Both load through `astro-icon` + the matching `@iconify-json/*` package.
- Brand marks come from the brand set so they are the official logo, not a UI designer's interpretation of it. Accept that some official logos are solid badges (YouTube's rounded rectangle, Telegram's circle) while others are bare glyphs — that weight difference is inherent to the brands and is not worth "fixing" by redrawing them.
- Pick a generic glyph's `-fill` / `-line` variant to match the weight of its neighbours **in that list**: outline next to bare brand glyphs, solid next to a solid brand badge. The variant is a per-list decision, not a global one.
- Size icons in `em` (`size-[1.15em]`) so they track the surrounding type scale instead of pinning to a px value.
- An icon replacing a text label must keep the label as `sr-only` text.
- Icon names live in the data file, never inline in the template — swapping an icon should not touch markup.

## Spacing

- When in doubt, go one step looser. Density is not the goal; breathing is.
- Responsive padding comes in pairs: `p-5 md:p-6`, `px-5 md:px-6`. Vertical rhythm is generous: `my-10 md:my-12` between list items.
- Observed hand-corrections, as calibration: `gap-2 → gap-3`, `pl-3 → pl-4`, `mt-3 → mt-4`, `mt-0.5 → mt-2` between a summary and its detail line, chip `px-1.5 → px-2`.

## Interaction

- Every color change carries `transition-colors`, usually `duration-200`.
- Touch targets are `size-12` circles: `rounded-full bg-white/0 active:bg-white/10`. Feedback lives on `active:` for touch, `hover:` for pointer.
- Links change **color** on hover (`hover:text-accent-600`), not their underline. In prose, a link hover may tint its background and border with `accent-100`/`accent-300` instead.

## Units

- Stay on the Tailwind spacing scale (`px-10`, `gap-6`, `mt-4`). Arbitrary values are a smell.
- Physical units (`mm`, `cm`) appear **only** where a physical container is defined — `@page`, plus one pair of size variables:

  ```css
  :root { --sheet-w: 297mm; --sheet-h: 210mm; }
  ```

  Everything inside is px. A4 is a container size, not a design system.
- Logical properties (`ps-*`, `pe-*`, `ms-*`) are the reach-for default for horizontal insets; use `px-*` when both sides are equal.

## Copy & Chrome

- No in-page utility buttons duplicating a browser feature (a "Print / PDF" button, an unrequested theme switcher).
- Punctuation: ASCII `-`, not `—` / `–`. No trailing `。` on a short standalone line (taglines, captions, list items).
- Footer form: `© {year} tcdw | Updated {date}` — no uppercase, no `·` separators.

## Review Checklist

Before showing a design, verify each:

1. Does any component name a raw palette (`sky-600`, `orange-200`, `slate-700`)? → move it behind `primary-*` / `accent-*` / `secondary-*`.
2. Is every neutral going through `secondary-*` (a gray ramp)? A naked `gray-*` is drift to clean up; `slate`/`zinc` is a mistake.
3. Is `accent-*` covering an area rather than marking one thing? → shrink it.
4. Does every color have a `dark:` counterpart?
5. Any English decoration, `uppercase`, or wide tracking used as ornament? → delete.
6. Any serif face? → rounded sans.
7. Any hardcoded `text-*` size where a `--fs-*` token exists?
8. Any colored text inside an already-tinted chip? → neutralize it.
9. Any hairline radius, hairline divider, or tinted zone that whitespace could replace?
10. Any arbitrary spacing value, or `mm`/`cm` outside the container definition? → snap to the Tailwind scale.
11. Does every interactive element have `transition-colors` and an `active:`/`hover:` state?
12. Does it look tight? → loosen one step and re-check.

## Evidence

Consolidated from `blog` and `bilisound` (tcdw's own long-running projects) plus his hand-restyle of the `im.tcdw.net` profile sheet (commit `7bc93fc`, "Optimize style"), where an agent-produced editorial draft was pulled back to this language rule by rule. Extend this file when a new project produces a new correction; do not generalize from a single ambiguous edit.
