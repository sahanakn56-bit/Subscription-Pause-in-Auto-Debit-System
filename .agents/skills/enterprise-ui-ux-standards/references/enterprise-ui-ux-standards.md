# UI/UX Standards Followed by Large Enterprises

A practical reference to the standards, principles, and practices that large companies (including Fortune 500 firms) commonly follow when designing digital products. Most of these are published, public frameworks, so you can adopt them directly.

---

## 1. Foundational Frameworks

| Framework | Origin | Use |
|---|---|---|
| **Nielsen's 10 Usability Heuristics** | Nielsen Norman Group | Standard checklist for usability reviews |
| **ISO 9241 (esp. Part 210, Part 11)** | ISO | Human-centred design process; defines usability as effectiveness, efficiency, satisfaction |
| **WCAG 2.2 (Level AA)** | W3C | De facto accessibility baseline |
| **Core Web Vitals** | Google | Performance metrics tied to UX and SEO |
| **Double Diamond / Design Thinking** | Design Council / IDEO | Discover → Define → Develop → Deliver process |

### Nielsen's 10 Heuristics
1. Visibility of system status
2. Match between system and the real world
3. User control and freedom (undo, cancel, back)
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use (shortcuts, defaults)
8. Aesthetic and minimalist design
9. Help users recognise, diagnose, and recover from errors
10. Help and documentation

---

## 2. Design Systems (the Enterprise Norm)

Large organisations almost always maintain a single design system as the source of truth for components, tokens, and guidelines. Well-known public examples:

- **Material Design**: Google
- **Human Interface Guidelines (HIG)**: Apple
- **Fluent**: Microsoft
- **Carbon**: IBM
- **Lightning Design System**: Salesforce
- **Polaris** (Shopify) and **Atlassian Design System**: widely referenced, even though the companies are not Fortune 500 US firms

**What a mature design system contains**
- Design tokens (colour, type, spacing, elevation, motion)
- Component library with variants and states (default, hover, focus, active, disabled, error, loading)
- Usage guidelines (do / don't)
- Accessibility notes per component
- Code parity: the same components in Figma and in production code (React, Angular, Web Components)
- Versioning, changelog, and contribution process

---

## 3. Visual Design Standards

### Layout and Spacing
- Use a **4pt or 8pt spacing grid**; all spacing is a multiple of the base unit
- **12-column responsive grid** for web; consistent gutters and margins
- Define breakpoints (commonly ~360, 768, 1024, 1280, 1440px) and design mobile-first
- Keep a clear visual hierarchy: one primary action per view

### Typography
- Limit to **1-2 typefaces**; define a type scale (e.g. 12/14/16/20/24/32/40)
- Body text **16px minimum** on web; line height **1.4-1.6**
- Line length of roughly **45-75 characters**
- Use relative units (`rem`) so users can scale text

### Colour
- Defined palette: primary, secondary, neutral, and semantic (success, warning, error, info)
- Never rely on colour alone to convey meaning
- Support **dark mode** and, where needed, high-contrast themes
- Brand colours are applied through tokens, not hard-coded values

### Iconography and Imagery
- One consistent icon set (stroke weight, grid, corner radius)
- Icons paired with text labels unless universally understood
- Provide alt text for meaningful images; mark decorative images as such

---

## 4. Accessibility (Non-Negotiable at Scale)

Legal exposure (ADA in the US, Section 508 for government work, EN 301 549 and the European Accessibility Act in the EU) makes accessibility a requirement, not an enhancement.

**WCAG 2.2 Level AA essentials**
- **Contrast**: 4.5:1 for normal text, 3:1 for large text and UI components/graphics
- **Keyboard**: every function usable without a mouse; logical tab order; no keyboard traps
- **Focus**: visible focus indicator on all interactive elements
- **Target size**: at least 24×24 CSS px (WCAG 2.2 AA); many teams use **44×44 px** (Apple) or **48×48 dp** (Material) as the practical standard
- **Screen readers**: semantic HTML first, ARIA only where needed; labels on every form control
- **Text resize**: content works at 200% zoom and with reflow at 320px width
- **Motion**: respect `prefers-reduced-motion`; no content flashing more than 3 times/second
- **Time**: allow users to extend or disable time limits
- **Forms**: clear labels, instructions, error identification, and suggestions
- **Language**: set the page language; support RTL where relevant

**Testing**: automated tools (axe, Lighthouse) catch only a portion of issues; combine with manual keyboard testing, screen readers (NVDA, JAWS, VoiceOver, TalkBack), and testing with users with disabilities.

---

## 5. Interaction and Usability Patterns

### Navigation
- Consistent global navigation; maximum 7±2 top-level items
- Clear current-location indication (active state, breadcrumbs)
- Search is prominent for content-heavy products
- Avoid deep nesting; keep important tasks within 3 clicks/taps where feasible

### Forms
- Single-column layouts perform best
- Labels above fields; do not use placeholder text as a label
- Inline validation on blur, with specific, human-readable messages
- Mark optional fields rather than required where most fields are required
- Preserve user input on error; support autofill and appropriate input types
- Ask only for what is needed (progressive disclosure)

### Feedback and System Status
- Respond to every action within **~100 ms** (perceived instant), show progress for anything over **~1 s**
- Use skeleton screens or progress indicators instead of blank screens
- Confirm success; make destructive actions reversible (undo) or require confirmation

### Error Handling
- Say what happened, why, and how to fix it, in plain language
- Never blame the user; avoid error codes as the only message
- Provide a path forward (retry, contact support)

### Empty, Loading, and Edge States
- Design every state: empty, loading, partial, error, offline, no-permission
- Empty states should explain value and offer the next action

---

## 6. Content and Microcopy

- Plain language, active voice, consistent terminology
- Documented **voice and tone** guidelines; sentence case for UI text is common
- Button labels start with a verb ("Save changes", not "OK")
- Localisation-ready: avoid concatenated strings, allow ~30-40% text expansion
- Respect regional formats for dates, numbers, currency, and names

---

## 7. Performance as UX

**Core Web Vitals (good thresholds, 75th percentile)**
- **LCP** (Largest Contentful Paint): ≤ 2.5 s
- **INP** (Interaction to Next Paint): ≤ 200 ms
- **CLS** (Cumulative Layout Shift): ≤ 0.1

Common practices: image optimisation and lazy loading, code splitting, caching/CDN, font-loading strategy, and performance budgets enforced in CI.

---

## 8. Responsive and Cross-Platform Design

- Mobile-first, with progressive enhancement
- Touch-friendly spacing; thumb-zone-aware placement of primary actions on mobile
- Follow platform conventions: HIG on iOS, Material on Android, native patterns where users expect them
- Support a defined browser/device matrix and test against it
- Design for varied network conditions and offline behaviour where relevant

---

## 9. Security, Privacy, and Trust in UX

- Clear, granular consent flows (GDPR, CCPA/CPRA); no dark patterns
- Transparent data use explanations at the point of collection
- Secure-by-default patterns: MFA, passkeys, masked sensitive fields, session timeout warnings
- Visible trust signals for payments and account actions
- Avoid deceptive patterns such as forced continuity, hidden costs, confirmshaming, or hard-to-find cancellation. Regulators (FTC, EU) increasingly enforce against these.

---

## 10. Process and Governance

### Research and Validation
- User research: interviews, surveys, contextual inquiry, analytics review
- Usability testing (5 users per round surfaces most major issues; repeat iteratively)
- A/B and multivariate testing for measurable decisions
- Personas, journey maps, and jobs-to-be-done to align teams

### Design Workflow
1. Discovery and research
2. Problem definition and success metrics
3. Wireframes → prototypes (low- to high-fidelity)
4. Usability testing and iteration
5. Design review and accessibility review
6. Developer handoff (specs, tokens, component references)
7. QA against design (visual regression testing)
8. Post-launch measurement and iteration

### Governance
- Design system team with contribution and deprecation process
- Design critiques and cross-functional reviews
- Definition of Done includes accessibility, responsiveness, and all states
- Documentation in a shared, searchable place (Figma, Storybook, Zeroheight, Confluence)

---

## 11. Metrics Commonly Tracked

| Category | Metrics |
|---|---|
| Usability | Task success rate, time on task, error rate |
| Satisfaction | SUS (System Usability Scale), CSAT, NPS, CES |
| Engagement | Adoption, retention, feature usage, drop-off per funnel step |
| Business | Conversion rate, support ticket volume, cost to serve |
| Performance | Core Web Vitals, page load, crash rate |
| Accessibility | Audit pass rate, open accessibility defects |

Frameworks like Google's **HEART** (Happiness, Engagement, Adoption, Retention, Task success) are used to structure these.

---

## 12. Quick Pre-Release Checklist

- [ ] Uses design system components and tokens only
- [ ] WCAG 2.2 AA verified (automated + manual + screen reader)
- [ ] Contrast, focus states, and keyboard navigation checked
- [ ] All states designed: empty, loading, error, success, disabled
- [ ] Forms have labels, validation, and helpful errors
- [ ] Responsive at all defined breakpoints; touch targets adequate
- [ ] Core Web Vitals within thresholds
- [ ] Copy reviewed for clarity, tone, and localisation
- [ ] Consent and privacy flows reviewed; no dark patterns
- [ ] Analytics events and success metrics defined
- [ ] Usability tested with representative users

---

## 13. Further Reading

- Nielsen Norman Group: nngroup.com (heuristics, research articles)
- W3C WCAG 2.2: w3.org/TR/WCAG22
- Apple Human Interface Guidelines: developer.apple.com/design
- Material Design: m3.material.io
- Microsoft Fluent: fluent2.microsoft.design
- IBM Carbon: carbondesignsystem.com
- Salesforce Lightning Design System: lightningdesignsystem.com
- web.dev (Core Web Vitals and performance)
- *Don't Make Me Think* (Steve Krug), *The Design of Everyday Things* (Don Norman), *Refactoring UI* (Wathan & Schoger)

> Note: Thresholds and standards (WCAG, Core Web Vitals, platform guidelines) evolve. Verify against the current official documentation before using them in formal requirements.
