---
name: managing-brand-identity
description: Provides the single source of truth for brand guidelines, design tokens, technology choices, and voice/tone. Use this skill whenever generating UI components, styling applications, writing copy, or creating user-facing assets to ensure brand consistency.
---

# Brand Identity & Guidelines

**Brand Name:** Inceptum Consilatio / Digimedi Health

This skill defines the core constraints for visual design and technical implementation for the brand. Adhere to these guidelines strictly to maintain consistency across all user-facing products and communications.

## When to use this skill
- Generating UI components or styling applications.
- Writing marketing copy, error messages, or documentation.
- Creating assets or designs for a specific brand persona.
- Choosing technical frameworks and libraries for a project.

## Workflow

1.  **Identify Brand**: Determine if the task is for Inceptum Consilatio, Digimedi Health, or a generic placeholder.
2.  **Consult Tokens**: Load `resources/design-tokens.json` for colors and typography.
3.  **Check Tech Stack**: Read `resources/tech-stack.md` to ensure correct frameworks are used.
4.  **Align Voice**: Consult `resources/voice-tone.md` before generating any text.

## Reference Documentation

### For Visual Design & UI Styling
Consult for exact colors, fonts, border radii, or spacing values:
👉 **[`resources/design-tokens.json`](resources/design-tokens.json)**

### For Coding & Component Implementation
Consult for technical constraints and mandatory frameworks:
👉 **[`resources/tech-stack.md`](resources/tech-stack.md)**

### For Copywriting & Content Generation
Consult for persona guidelines and terminology:
👉 **[`resources/voice-tone.md`](resources/voice-tone.md)**

## Instructions

- **No Placeholders**: Never use generic colors (red, blue) when brand tokens are available.
- **Strict Tech Stack**: If the stack is Tailwind, do not use CSS-in-JS.
- **Active Voice**: Always prefer direct, active voice in copywriting.
- **Validation**: Before finishing a UI task, verify the design tokens match the implementation.
