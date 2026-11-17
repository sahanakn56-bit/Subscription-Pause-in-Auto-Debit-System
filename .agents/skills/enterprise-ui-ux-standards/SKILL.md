---
name: enterprise-ui-ux-standards
description: >-
  Enterprise UI/UX design standards, WCAG 2.2 AA accessibility requirements, 4pt/8pt spacing grids, typography scales, design tokens, form design, error handling, state management, and pre-release review guidelines. Use this skill whenever designing, building, reviewing, or refactoring UI components, pages, forms, modals, or user flows.
---

# Enterprise UI/UX Standards

This skill defines the enterprise-grade UI/UX standards, design system rules, accessibility requirements (WCAG 2.2 AA), and usability principles that must be strictly followed across all frontend development in the **Subscription Pause in Auto-Debit System**.

---

## 1. Core Principles & Domain Rules (Subscription & Auto-Debit)

When implementing subscription and auto-debit management workflows:
- **No Deceptive / Dark Patterns**: Never use confirmshaming, hidden resumption fees, obscured cancel/pause options, or forced continuity.
- **Transparent Dates & Amounts**: Clearly state the exact date when pause begins, date when billing resumes, and next auto-debit charge amount.
- **User Control & Reversibility**: Any pause, unpause, or schedule modification must provide clear confirmation, state visibility, and easy undo/cancellation.
- **Visibility of System Status**: Always show current subscription state clearly (`Active`, `Paused`, `Pending Pause`, `Resuming`).

---

## 2. Visual Design & Design Tokens

### Layout & Spacing
- **Base Grid**: Use a **4pt / 8pt spacing grid** for all margins, paddings, gap dimensions, and component heights.
- **Responsive Breakpoints**: Design mobile-first using standard breakpoints:
  - Mobile: `< 640px`
  - Tablet: `640px - 1024px`
  - Desktop: `> 1024px`
- **Visual Hierarchy**: Exactly **one primary action button** per view/modal. Secondary actions must use outline or ghost styles.

### Typography
- **Type Scale**: Defined scale using relative units (`rem`):
  - Caption / Micro: `12px` (`0.75rem`)
  - Small / Helper: `14px` (`0.875rem`)
  - Body: `16px` (`1rem`) minimum for web readability; line-height: `1.5`
  - Subheading: `18px - 20px` (`1.125rem - 1.25rem`)
  - Heading 2: `24px` (`1.5rem`)
  - Heading 1 / Title: `32px` (`2rem`)
- **Reading Width**: Limit text blocks to `45 - 75` characters per line for optimal scanning.

### Colour & Semantic Tokens
- **Semantic Palette**:
  - Primary: Brand action color
  - Success: Positive confirmations (e.g. `Pause Scheduled`)
  - Warning: Important notices (e.g. `Auto-debit will resume in 3 days`)
  - Error: Actionable alerts and field validation errors
  - Neutral / Surface: Backgrounds, borders, muted text
- **Contrast**: Text contrast ratio of at least **4.5:1** against backgrounds (**3:1** for large text/icons).
- **Never rely on color alone**: Always pair color with an icon, badge, or descriptive text.

---

## 3. Accessibility Standards (WCAG 2.2 AA - Non-Negotiable)

1. **Keyboard Navigability**:
   - Every interactive element (buttons, toggles, date pickers, dropdowns, modals) must be operable via `Tab`, `Enter`, `Space`, and arrow keys.
   - Logical tab sequence following visual flow.
   - Trap focus inside active dialogs/modals; release focus to triggering element on close.
2. **Focus Indicators**:
   - High-visibility focus ring (`outline: 2px solid <color>` with `outline-offset: 2px`) on all interactive elements. Never set `outline: none` without providing an accessible alternative.
3. **Touch & Click Target Sizes**:
   - Minimum target size: **44×44 px** (or `48×48 dp`) for mobile touch targets and clickable icons.
4. **Screen Reader Support**:
   - Semantic HTML elements (`<main>`, `<nav>`, `<button>`, `<fieldset>`, `<label>`).
   - Descriptive `aria-label` on icon-only buttons (e.g. `<button aria-label="Close dialog">`).
   - Use `aria-live="polite"` for dynamic notifications and status banners.
5. **Reduced Motion**:
   - Honor `@media (prefers-reduced-motion: reduce)` by disabling or simplifying transitions and animations.

---

## 4. Interaction, Forms & Error Handling

### Form Design
- **Labels**: Always position labels above the input field; never use placeholders as substitutes for labels.
- **Helper & Error Text**: Persistent helper text below fields when formatting is expected (e.g., date formats).
- **Validation**:
  - Validate on blur or submit (not aggressively on first keystroke).
  - Clear, human-readable error messages explaining *what happened* and *how to fix it*.
  - Associate error message to input using `aria-describedby`.
- **Preserve User Input**: Never clear entered data when a validation or network error occurs.

### Feedback & State Management
Every asynchronous action or data container must support and render all 5 states:
1. **Initial / Empty State**: Explain what this section is and provide an onboarding action.
2. **Loading State**: Use skeleton loaders or spinners; show feedback within **100ms** of user trigger.
3. **Success State**: Clear, non-blocking toast or banner confirming the completed change.
4. **Error State**: Actionable error message with a "Retry" or recovery option.
5. **Disabled State**: Accessible styling (`aria-disabled="true"`, readable muted contrast).

### Action Buttons & Microcopy
- **Verb-First Copy**: Button labels must start with an active verb (e.g., "Pause Subscription", "Resume Auto-Debit", "Save Changes", not "OK" or "Submit").
- **Destructive Actions**: Require confirmation modal or provide an explicit "Undo" window.

---

## 5. Development & Review Checklist

Before finishing any UI component or page, verify:
- [ ] Uses 4pt/8pt spacing tokens for all margins, paddings, and heights.
- [ ] WCAG 2.2 AA contrast verified (4.5:1 text, 3:1 graphical objects).
- [ ] Visible focus ring appears on keyboard navigation.
- [ ] Tab order is natural; modal dialogs trap and return focus properly.
- [ ] Touch targets are at least 44×44 px.
- [ ] All inputs have explicit `<label>` elements linked via `htmlFor`/`id`.
- [ ] Empty, Loading, Error, and Success states are implemented.
- [ ] Action buttons use active verb-first phrasing.
- [ ] Zero deceptive or dark patterns in subscription and payment workflows.
- [ ] Responsive across mobile (360px), tablet (768px), and desktop (1024px+).

---

## 6. References
- Full enterprise guidelines reference: [enterprise-ui-ux-standards.md](./references/enterprise-ui-ux-standards.md)
