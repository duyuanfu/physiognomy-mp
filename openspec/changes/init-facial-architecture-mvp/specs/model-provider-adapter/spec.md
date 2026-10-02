## ADDED Requirements

### Requirement: Multi-Provider Model Abstraction
The system SHALL provide a unified provider interface (`BaseLLMProvider`) supporting multimodal inputs (image bytes + prompt context) and returning structured report schemas.

#### Scenario: Primary provider invocation
- **WHEN** a report generation request is initiated under default configuration
- **THEN** the system calls the Google Gemini 1.5 Flash 8B provider with JSON schema enforcement.

### Requirement: Automatic Failover to Domestic Provider
The system SHALL catch timeout (over 6 seconds), network errors, or rate limit errors from the primary provider and automatically failover to the secondary provider (Aliyun Qwen-VL-Plus).

#### Scenario: Seamless failover on primary error
- **WHEN** Gemini API invocation fails or times out
- **THEN** the system logs a warning and transparently delegates the request to the Qwen-VL provider without returning an error to the frontend.

### Requirement: Schema-Strict Output Validation
The system SHALL validate the returned LLM response against a strict Pydantic model (`FacialReportResponse`), ensuring archetype, three-parts ratio, bone frame, ear evidence, features, radar scores, and modern advice are populated.

#### Scenario: Validated structured response
- **WHEN** the LLM generates a JSON string
- **THEN** the system parses and validates it against `FacialReportResponse`, returning HTTP 200 with standard response envelopes.
