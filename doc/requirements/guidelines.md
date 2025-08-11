# Requirements Authoring Guidelines

## General Principles
- All requirements must be written in individual markdown files within the appropriate directory (`/product`, `/customer`, `/technical`).
- The three-tier structure **Product (PRQ)** -> **Customer (CRQ)** -> **Technical (TRQ)** must be followed.
- Each requirement file must strictly adhere to its specified naming schema and template.
- Requirements must be linked using the `Up-stream` and `Down-stream` reference fields to ensure full traceability.

## Product Requirements (PRQ)
- **Objective:** Defines *what* the system does from a high-level, functional perspective. It describes a core capability.
- **File Naming:**
    - **Pattern:** `prqXX-titleInCamelCase.md`
    - **Example:** `prq01-singleUserOperation.md`
- **Template:**
    ```markdown
    # PRQ-XXX: <Title>

    **In order to** <Why we are doing this>
    **As** <Who wants this>
    **I want to** <What I want to do>

    ## Description
    <A full-sentence, descriptive paragraph explaining the requirement's purpose and scope.>

    ## Details
    - <Compact detail point 1>
    - <Compact detail point 2>

    ## Risks
    - <Compact risk point 1>
    - <Compact risk point 2>

    ## Concept
    - <Compact concept point 1>
    - <Compact concept point 2>

    ## Test Scenarios
    - <Compact test scenario 1>
    - <Compact test scenario 2>

    ## Down-stream references
    - [<CRQ title>](../customer/crqXXX-title.md)
    ```

## Customer Requirements (CRQ)
- **Objective:** Describes a requirement from the end-user's perspective. It answers *why* a user wants a particular feature.
- **File Naming:**
    - **Pattern:** `crqXXX-titleInCamelCase.md`
    - **Example:** `crq001-frictionlessStartup.md`
- **Template:**
    ```markdown
    # CRQ-XXX: <Title>

    **In order to** <Why we are doing this>
    **As** <Who wants this>
    **I want to** <What I want to do>

    ## Description
    <A full-sentence, descriptive paragraph explaining the requirement's purpose and scope.>

    ## Details
    - <Compact detail point 1>
    - <Compact detail point 2>

    ## Risks
    - <Compact risk point 1>
    - <Compact risk point 2>

    ## Concept
    - <Compact concept point 1>
    - <Compact concept point 2>

    ## Test Scenarios
    - <Compact test scenario 1>
    - <Compact test scenario 2>

    ## Up-stream references
    - [<PRQ title>](../product/prqXXX-title.md)
    ```

## Technical Requirements (TRQ)
- **Objective:** Defines *how* a feature will be implemented. It specifies technologies, standards, or other non-functional constraints.
- **File Naming:**
    - **Pattern:** `trqXXX-titleInCamelCase.md`
    - **Example:** `trq001-localWebServiceArchitecture.md`
- **Template:**
    ```markdown
    # TRQ-XXX: <Title>

    **In order to** <Why we are doing this>
    **As** <Who wants this (e.g., a developer)>
    **I want to** <What I want to do>

    ## Description
    <A full-sentence, descriptive paragraph explaining the requirement's purpose and scope.>

    ## Details
    - <Compact detail point 1>
    - <Compact detail point 2>

    ## Risks
    - <Compact risk point 1>
    - <Compact risk point 2>

    ## Concept
    - <Compact concept point 1>
    - <Compact concept point 2>

    ## Test Scenarios
    - <Compact test scenario 1>
    - <Compact test scenario 2>

    ## Up-stream references
    - [<CRQ title>](../customer/crqXXX-title.md)

    ## External references
    - [<Website or document name>](<URL>)
    ```

## Traceability
- **Purpose:** To create a clear, auditable link from high-level product goals down to specific technical implementations.
- **Rules:**
    - A **PRQ** must link *down* to one or more CRQs via its `Down-stream references` field.
    - A **CRQ** must link *up* to one or more PRQs via its `Up-stream references` field.
    - A **TRQ** must link *up* to one or more CRQs via its `Up-stream references` field.
- **Flow Diagram:**
    ```mermaid
    graph TD
        PRQ -- "is fulfilled by" --> CRQ
        CRQ -- "is implemented by" --> TRQ
    ```
