---
allowed-tools: Bash, BashOutput, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [idea]
description: Interactively generate a PRD for a given idea.
---
# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown format, based on an initial user prompt. The PRD should be clear, actionable, and suitable for a junior developer to understand and implement the feature.

## User Input
$1

## Process

1.  **Research:** Use the @researcher agent as needed in order to become a subject matter expert
2.  **Ask Clarifying Questions:** Before writing the PRD, the AI *must* ask clarifying questions to gather sufficient detail. The goal is to understand the "what" and "why" of the feature, not necessarily the "how" (which the developer will figure out). Make sure to provide options in letter/number lists so I can respond easily with my selections.
3.  **Repeat:** Go back to step 1 as needed 
4.  **Generate PRD:** Based on the initial prompt and the user's answers to the clarifying questions, generate a PRD using the structure outlined below
7.  **Save PRD:** Save the generated document in `/context/[nnn]-{feature|branch|question}`
8.  **Research Again:** Use the @researcher agent to determine if more research is needed for the generated PRD
9.  **Refine:** If the PRD should be adjusted based on new research, go through all the steps again before updating the generated PRD

## Research Guidance
- Use the @researcher agent to maintain research for this PRD, it will output a research file and tell you where it is saved
- For any subsequent calls to the @researcher agent, also provide it the location of the original research file and tell it to update it as needed
- Use the @researcher agent before asking clarifying questions, after asking clarifying questions, and after any changes to the PRD
- Use the @researcher agent if the PRD changes in a way where the research that you have access to is not sufficient enough to make educated decisions

## Clarifying Questions (Examples)

The AI should adapt its questions based on the prompt, but here are some common areas to explore:

*   **Problem/Goal:** "What problem does this feature solve for the user?" or "What is the main goal we want to achieve with this feature?"
*   **Target User:** "Who is the primary user of this feature?"
*   **Core Functionality:** "Can you describe the key actions a user should be able to perform with this feature?"
*   **User Stories:** "Could you provide a few user stories? (e.g., As a [type of user], I want to [perform an action] so that [benefit].)"
*   **Acceptance Criteria:** "How will we know when this feature is successfully implemented? What are the key success criteria?"
*   **Scope/Boundaries:** "Are there any specific things this feature *should not* do (non-goals)?"
*   **Data Requirements:** "What kind of data does this feature need to display or manipulate?"
*   **Design/UI:** "Are there any existing design mockups or UI guidelines to follow?" or "Can you describe the desired look and feel?"
*   **Edge Cases:** "Are there any potential edge cases or error conditions we should consider?"

## PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., "The system must allow users to upload a profile picture."). Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
7.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions (e.g., "Should integrate with the existing Auth module").
8.  **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", "Reduce support tickets related to X").
9.  **Open Questions:** List any remaining questions or areas needing further clarification.

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output
*   **Format:** Markdown (`.md`)
*   **Location:** `/context/[nnn]-{feature|branch|question}`
*   **Filename:** `prd-[nnn].md`
*   **Example:** `prd-001.md`

## Final instructions

1. Do NOT start implementing the PRD
2. Make sure to ask the user clarifying questions
3. Take the user's answers to the clarifying questions and improve the PRD