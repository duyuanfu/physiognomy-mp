## ADDED Requirements

### Requirement: Design System Token Adherence
The mini-program frontend SHALL implement the Minimalist Luxury design tokens (`--bg-primary: #0C0D0E`, `--bg-surface: #141518`, 4px grid, and micro-radii <= 6px) across all views.

#### Scenario: Visual styling consistency
- **WHEN** any page or modal renders
- **THEN** it strictly uses obsidian dark background, cold silver typography, and 0.5px subtle hairline borders.

### Requirement: Camera Guide Alignment Mask
The system SHALL provide an interactive camera capture view featuring an elliptical guide overlay, inner canthi horizontal crosshairs, and ear alignment guides.

#### Scenario: User captures or selects photo
- **WHEN** the capture screen is active
- **THEN** the guide mask assists the user in aligning their face, forehead, and ears within the calibrated boundary.

### Requirement: Scanning Ceremony & Latency Concealment
The system SHALL display a dynamic scanning ceremony overlay upon photo submission, featuring a moving hairline laser and progressive status text updates.

#### Scenario: Ceremony during inference
- **WHEN** the image is being processed by the backend (2-4 seconds)
- **THEN** the screen animates progressive verification steps (`Aligning Three-Parts...`, `Measuring Jaw Angle...`) to conceal network latency.

### Requirement: Caliper Overlay & Editorial Report Rendering
The system SHALL render the final report in an editorial magazine layout, displaying calibrated geometric calipers directly onto the greyscale photo and presenting structured card sections.

#### Scenario: Displaying report with calipers
- **WHEN** analysis completes successfully
- **THEN** the report view shows the photo with caliper overlay (canthal tilt angle, aspect ratio tags), three-parts proportions, ear evidence, radar chart, and advice cards.

### Requirement: Poster Canvas Generation
The system SHALL support exporting a 9:16 high-resolution aesthetic poster via Canvas 2D containing key metrics, archetype stamp, and mini-program QR code.

#### Scenario: Exporting poster
- **WHEN** the user taps "保存高清海报"
- **THEN** the frontend draws the editorial poster on Canvas and prompts the user to save it to their photo album.
