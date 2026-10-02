## ADDED Requirements

### Requirement: Structured Knowledge Base Indexing
The system SHALL maintain a structured corpus of de-mystified traditional physiognomy (Bing Jian, Ma Yi) and modern craniofacial aesthetic psychology in an embedded vector store (ChromaDB) with categorical metadata.

#### Scenario: Knowledge chunk retrieval initialization
- **WHEN** the RAG service starts up
- **THEN** it validates that knowledge chunks for bone structure, eye aesthetics, ear evidence, and facial proportions are properly indexed.

### Requirement: Geometric Feature Query Synthesis
The system SHALL automatically synthesize retrieval queries based on detected CV metrics without requiring textual user prompts.

#### Scenario: Query synthesis from facial metrics
- **WHEN** CV analysis outputs specific tags (e.g., canthal tilt > 3.0, jaw angle < 85, face ratio > 1.45)
- **THEN** the system generates targeted semantic query terms matching bone sharpness, eye focus, and ear grounding.

### Requirement: Top-K Context Injection
The system SHALL retrieve the top 3-4 most relevant knowledge snippets and format them as an authoritative reference block in the LLM prompt.

#### Scenario: Injection into prompt context
- **WHEN** synthesized queries are executed against the knowledge base
- **THEN** the retrieved texts are deduplicated and appended under the `【参考专业相法与美学权威典籍知识】` prompt section.
