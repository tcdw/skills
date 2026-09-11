---
name: web-design-taste
description: tcdw's personal visual design language for web and React Native UI — semantic primary/accent color aliases over raw Tailwind palettes (accent opt-in, often zero), system sans-serif typography with no decorative English, generous radii and spacing, per-breakpoint recomposition, print-aware links, low-alpha identity artwork, and launch assets (favicon, OG card) reused from the blog. Use when designing, styling, or restyling any page, screen, or component for tcdw, when preparing a page to ship, and when reviewing a visual draft before presenting it. Do NOT use for copywriting or information architecture decisions.
---

# Web Design Taste (tcdw)

> Restrained, rounded, roomy. Color is semantic and rare. Decoration that only signals "designed" gets cut; decoration that carries identity stays, faintly.

## Reference Implementations

Read these before proposing a new visual direction; they are the baseline, not this document:

| Project | Stack | What it establishes |
| --- | --- | --- |
| `blog` | Astro + Tailwind v4 | The canonical `@theme` block, dark mode, banner/backdrop composition, the favicon set |
| `bilisound` | Expo + NativeWind + gluestack-ui | Semantic token roles, radius vocabulary, interaction states |
| `im.tcdw.net` | Astro + Tailwind v4 | The same `@theme` on a single dense page: responsive recomposition, print, decorative artwork, OG card |

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
| `primary-*` | per-project hue (sky / teal) | Identity, links, hover, list markers, every emphasis by default |
| `accent-*` | per-project hue (amber / blue) | Optional. A second kind of emphasis that must be told apart from primary on the same screen — the *currently playing* item |
| `secondary-*` | **always gray** | Everything neutral: body text, borders, surfaces, disabled and muted states |

- The **structure** is fixed; the **palette is per-project**. `blog` and `im.tcdw.net` map primary→sky, accent→amber; `bilisound` uses a teal primary (`#00BA9D`) with a blue accent. Retheming must be a one-line change, never a find-and-replace across templates.
- **`accent-*` is opt-in, and zero is a normal outcome.** Reach for `primary-*` first. On `im.tcdw.net` accent went from orange-everywhere (first draft) → three marks (motto, project kind, hover) → **none**: the shipped page is primary + secondary only. Keep the alias defined so it is one line away, but don't spend it unless there are genuinely two kinds of emphasis to distinguish.
- When accent is used it is **never a large area**. It marks one thing.
- `secondary-*` is essentially always a **gray ramp**, and it stays gray across projects even when primary and accent are rethemed. Naming it `secondary` rather than `gray` keeps the neutral swappable in one place and lets dark mode flip the whole ramp (`bilisound` flips secondary 0↔950 exactly like primary).
- Write `secondary-*` rather than a naked `gray-*` wherever the alias exists. `blog` still writes `gray-*` directly — that is drift to clean up, not a counter-example. Never `slate`/`zinc`.
- In the RN app the same roles also appear as gluestack's finer-grained tokens (`typography-*`, `background-*`, `outline-*`); use those there.
- Color is for *text marks*, not areas. A tinted chip keeps neutral text (`bg-primary-50` + `text-secondary-800`).
- De-emphasize with `opacity-60`, not by inventing a lighter gray.
- No tinted zone backgrounds, no accent bar across the top of a card, no colored section rules.

### Dark mode is first class

Every color declaration is paired: `text-primary-600 dark:text-primary-400`, `bg-white dark:bg-gray-950`. `bilisound` goes further and **flips the entire ramp** (950↔0) rather than hand-picking dark values. A design with no dark story is unfinished — say so rather than shipping it silently.

The one shipped exception is the print-first `im.tcdw.net` sheet, which is light-only and says so with `html { color-scheme: light }`. If a page is going light-only, make it that explicit and mention it when presenting; don't let it happen by omission.

## Typography

- **System sans-serif by default.** Unless tcdw names a font for the project, don't add a web font or override Tailwind's default `--font-sans`. Don't reach for a serif display face to look "designed" — that was part of the editorial costume stripped from the first `im.tcdw.net` draft.
- **When a web font is requested, it must actually load.** Putting a face in `--font-sans` does nothing on machines without it installed. Ship its stylesheet, at low priority so the system fallback paints first (`<link rel="stylesheet" fetchpriority="low" … crossorigin>`), and keep system fonts (`-apple-system`, `"Microsoft YaHei"`, `sans-serif`) at the end of the stack.

- **No decorative English.** No bilingual headings, no `Who` / `Now` / `Stack` micro-labels beside a Chinese title, no `A 5-Minute Intro` kickers.
- **No `uppercase` and no wide `tracking-[0.2em+]` as ornament.** Small-caps-ish label styling is a tell of template design. Light tracking (`0.12–0.16em`) on tiny CJK labels has survived every pass and is fine.
- A section heading is a bold Chinese title and nothing else — no rule line, no color block, no counter.
- `body { text-autospace: normal }` wherever CJK and Latin mix.
- Where a size-token system exists (`--fs-*`), the template must not hardcode `text-sm`; one hardcoded size breaks responsive and print scaling.

## Shape & Surface

- Radii are generous. Vocabulary in frequency order: `rounded-full` for circular hit targets, pills and small avatars, `rounded-lg` as the everyday default, `rounded-xl`/`rounded-2xl` for large avatars and cards. **Never a hairline radius** (`rounded-[2px]`).
- Large surfaces may go squircle where supported:

  ```css
  border-radius: 1.5rem;
  @supports (corner-shape: squircle) { border-radius: 3rem; corner-shape: squircle; }
  ```

- Default page surface: white card, `rounded-2xl`, soft shadow, on a lightly tinted background — **at wide breakpoints only**. On a phone the card chrome is dropped (`sheet:rounded-2xl sheet:shadow-2xl`) and the page is full-bleed white; a floating card in a 400px viewport just wastes the narrowest dimension.
- `backdrop-blur` is allowed **over imagery** (blog's `bg-white/80 dark:bg-gray-950/70 backdrop-blur-xl` panel over a photographic banner). It is not generic decoration — no glassmorphism on a flat background.
- No borders on images. No paper/newspaper pastiche (off-white paper tints, top rules, `#fffdfa`).
- Banned styles: glow, exaggerated gradients, SaaS-landing-page look — and **editorial print pastiche**, for the same reason. Both are costumes.
- Prefer whitespace and a single card edge over dividers; drop hairline column separators and let the grid gap work.
- A thin left rule on a list item (`border-l-2 border-primary-200 pl-4`) is a mark, not a zone, and has survived every pass. What stays banned is a colored bar across a card's top or a rule under a heading.

## Imagery

- **Raster images go through the framework's image pipeline**, never raw from `public/`. In Astro: `src/assets/` + `<Image>` from `astro:assets`, `width` set to the displayed CSS size, `densities={[1, 2]}`. The corner artwork's 6MB source ships as 11KB/28KB webp.
- Binaries — `*.png`, `*.jpg`, `*.ico`, and design sources like `*.af` — go in Git LFS. Keep the design source (`design/open-graph.af`) committed next to its export.
- Once a real asset exists, delete its placeholder branch (the dashed "Avatar" box). Scaffolding is not a feature.

### Identity artwork

Decoration is allowed when it **carries identity** — tcdw's persona illustration (雪乃碗) — never as generic ornament. Recipe, as shipped:

```astro
<div class="sheet relative isolate overflow-hidden …">
  <Image
    src={corner} alt="" aria-hidden="true" width={480} densities={[1, 2]}
    class="pointer-events-none absolute right-4 bottom-12 -z-10 w-60 opacity-7 sheet:w-120"
  />
```

- **Watermark opacity.** Tuned by hand 10 → 5 → 8 → **7%**. Start at 7 and move in 1% steps; above ~10% it competes with text.
- **Size it large.** Desktop width went 300 → 540 → **480px**. A small corner sticker reads as clip-art; a large faint figure reads as atmosphere.
- **Transparent cut-out, not a scene.** A JPG with a floor and wall shadow was replaced by an RGBA PNG of the figure alone.
- `isolate` + `-z-10` puts it above the card's white but below the text; `overflow-hidden` keeps it inside the rounded corner; `alt=""` + `aria-hidden` + `pointer-events-none` make it inert.
- Use the **same illustration** across the page and its OG card so the share preview and the landing agree.

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
- Content sits at the top of a column (`justify-start`); don't `justify-between` a sidebar to smear its groups across the full height.
- Observed hand-corrections, as calibration: `gap-2 → gap-3`, `pl-3 → pl-4`, `mt-3 → mt-4`, `mt-0.5 → mt-2` between a summary and its detail line, chip `px-1.5 → px-2`, paired columns `gap-0 → gap-6`, sidebar `justify-between → justify-start`.

## Responsive: recompose, don't just stack

- An element may **move** between breakpoints. The avatar is a small `rounded-full w-16` beside the name in the mobile header, and a large `rounded-xl w-26` at the top of the sidebar on wide. Render it twice (`sheet:hidden` / `hidden sheet:block`) rather than contorting one element into both roles.
- Wide-layout devices get the breakpoint prefix: right alignment (`sheet:text-end`), the rule under a header row (`sheet:border-b`), card chrome. On mobile, text is start-aligned and flows.
- Test the phone layout as its own design, not as the desktop squeezed.

## Print

Only when a page has a print form (the `im.tcdw.net` sheet is A4 landscape, strictly one page).

- One custom variant covers "the wide composition" on both wide screens and paper, so print never falls back to the mobile single column:

  ```css
  @custom-variant sheet {
    @media screen and (width >= 64rem) { @slot; }
    @media print { @slot; }
  }
  ```

  Layout is shared; font-size tokens are not — `--fs-*` has three sets (mobile / wide / print).
- **Every interactive affordance needs a paper form.** A link prints as its bare address: label and arrow get `print:hidden`, button chrome gets `print:rounded-none print:border-0 print:px-0 print:py-0`, and the URL is shown with protocol and trailing slash stripped:

  ```ts
  const printableUrl = (url: string) => url.replace(/^https?:\/\//, '').replace(/\/$/, '');
  ```

## Interaction

- Every color change carries `transition-colors`, usually `duration-200`.
- Touch targets are `size-12` circles: `rounded-full bg-white/0 active:bg-white/10`. Feedback lives on `active:` for touch, `hover:` for pointer.
- Hover changes **color** — of the text, or of an existing underline's decoration — and never toggles an underline on or off. On `im.tcdw.net` hover goes to `primary-*`, consistent with accent being unused.
- Link vocabulary, from quietest to loudest:

  | Tier | Look | Example |
  | --- | --- | --- |
  | Title link | neutral text that tints on hover: `text-secondary-900 hover:text-primary-500` | a project name |
  | Identity link | `text-primary-800 underline decoration-primary-300 underline-offset-2`, decoration darkens on hover | `@tcdw` |
  | Inline action | `text-primary-700` + leading Remix icon, no chrome | 看看我的简历 |
  | Action chip | `rounded-md border border-primary-200 px-2 py-0.5 text-primary-700 hover:bg-primary-50` + `ri:arrow-right-up-line` | 了解更多 |

- External links carry `target="_blank" rel="noopener noreferrer"`.
- In prose, a link hover may tint its background and border with a `100`/`300` pair instead.
- Unordered notes use a small primary dot (`mt-[0.5em] size-1.5 shrink-0 rounded-full bg-primary-300`), not `01`/`02` mono counters.

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
- **Subtract before styling.** A section that repeats information found elsewhere gets deleted, not restyled — `im.tcdw.net` dropped 也做过, 其他 and 适合和我聊 in turn. When a section goes, its layout wrapper and its now-unused tokens (`--fs-num`) go in the same change.
- Punctuation: ASCII `-`, not `—` / `–`. No trailing `。` on a short standalone line (taglines, captions, list items).
- Footer form: `© {year} tcdw | Updated {date}` — no uppercase, no `·` separators.

## Shipping

A page isn't done until its launch assets are tcdw's, not the framework's:

- **Favicon set copied from `blog`**: `favicon.svg`, `favicon.ico` with `sizes="any"`, and `apple-touch-icon.png`. Never ship Astro's default icon.
- **OG card**: hand-made 1200×630 PNG — kicker, big name, role and a one-line stack on the left, the persona illustration on the right, domain at the bottom. A short amber dash above the kicker is the card's only accent mark. Declare `og:image:width/height/alt` (alt describes the illustration), `og:type=profile`, `twitter:card=summary_large_image`, `twitter:creator=@tcdwww`.
- Absolute URLs come from `site` in `astro.config.mjs` (`new URL(path, Astro.site)`); add `<link rel="canonical">`.
- `<title>` and `og:title` are the same string, built from the page's kicker + name (`5 分钟了解 tcdw`).

## Review Checklist

Before showing a design, verify each:

1. Does any component name a raw palette (`sky-600`, `orange-200`, `slate-700`)? → move it behind `primary-*` / `accent-*` / `secondary-*`.
2. Is every neutral going through `secondary-*` (a gray ramp)? A naked `gray-*` is drift to clean up; `slate`/`zinc` is a mistake.
3. Is `accent-*` used at all? If so, is there a second kind of emphasis that justifies it, and is it marking one thing rather than an area? Otherwise → `primary-*`.
4. Does every color have a `dark:` counterpart — or is the page explicitly light-only with `color-scheme: light`?
5. Any English decoration, `uppercase`, or wide tracking used as ornament? → delete.
6. Any web font or serif face nobody asked for? → system sans-serif. If a font was requested, is it actually loaded, not just named?
7. Any hardcoded `text-*` size where a `--fs-*` token exists?
8. Any colored text inside an already-tinted chip? → neutralize it.
9. Any hairline radius, hairline divider, or tinted zone that whitespace could replace?
10. Any arbitrary spacing value, or `mm`/`cm` outside the container definition? → snap to the Tailwind scale.
11. Does every interactive element have `transition-colors` and an `active:`/`hover:` state — and, if the page prints, a paper form?
12. On a phone: is the card chrome gone, is text start-aligned, did elements move to where they belong rather than just stacking?
13. Is every raster image going through `<Image>` with `densities`, and is decorative art inert (`alt=""`, `aria-hidden`, `pointer-events-none`) and faint (~7%)?
14. Favicon, apple-touch-icon and OG card replaced with tcdw's?
15. Does it look tight? → loosen one step and re-check.

## Evidence

Consolidated from `blog` and `bilisound` (tcdw's own long-running projects) plus the `im.tcdw.net` profile sheet, from the agent's first draft (`e1b9360`: serif name, orange top bar, `#fffdfa` paper, `mm` everywhere, English kickers) to the shipped site (`c6e9ada`). Commit `7bc93fc` ("Optimize style") is tcdw's hand-restyle that pulled the editorial draft back to this language; `c1a8b70` through `c6e9ada` then removed accent entirely, subtracted three sections, added print-aware links, the corner artwork (hand-tuned in `64122ea`/`40b0633`/`68db419`/`b1cc1c0`), mobile recomposition (`68db419`, `cca76f8`), the image pipeline, actually loading the web font (`aec23b6`), and the blog favicon + OG card (`096a501`, `9b2c66e`). Extend this file when a new project produces a new correction; do not generalize from a single ambiguous edit.
