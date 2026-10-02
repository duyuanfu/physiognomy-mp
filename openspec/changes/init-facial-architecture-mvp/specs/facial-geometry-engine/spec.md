## ADDED Requirements

### Requirement: Facial Landmark Detection & Pose Calibration
The system SHALL use MediaPipe Face Mesh (478 dense landmarks) to detect facial landmarks and perform 2D roll angle calibration (de-roll) based on the inner canthi axis.

#### Scenario: Face successfully detected and calibrated
- **WHEN** an image containing a frontal face is submitted
- **THEN** the system extracts 478 landmarks and levels the face coordinates such that the horizontal line connecting inner canthi has roll angle 0.

#### Scenario: Face not found or extreme tilt
- **WHEN** an image has no face or pose pitch/yaw exceeds 20 degrees
- **THEN** the system returns a validation error indicating face posture or visibility is inadequate.

### Requirement: Facial Aspect Ratio Calculation
The system SHALL calculate the facial aspect ratio using the vertical distance from trichion (landmark 10) to menton (landmark 152), divided by the bizygomatic distance between landmarks 234 and 454.

#### Scenario: Aspect ratio classification
- **WHEN** face length and width are calculated after leveling
- **THEN** the system computes ratio `length / width` and tags as long-face (>1.45), balanced-face (1.30-1.45), or broad-face (<1.30).

### Requirement: Mandibular Jaw Angle Calculation
The system SHALL calculate the mandibular convergence angle (jaw angle) formed by the chin apex (landmark 152) and the bilateral gonion inflection points (landmarks 397 and 172).

#### Scenario: Sharp vs square jaw angle
- **WHEN** the 2D vector angle between chin-to-left-gonion and chin-to-right-gonion is calculated
- **THEN** the system outputs the angle in degrees and classifies it as sharp (<85°), gentle (85°-100°), or grounded square (>100°).

### Requirement: Canthal Tilt & Palpebral Fissure Measurement
The system SHALL calculate the canthal tilt angle (outer canthus elevation) and the palpebral fissure length-to-height ratio for both eyes.

#### Scenario: Canthal tilt angle calculation
- **WHEN** outer canthus (landmark 263) and inner canthus (landmark 362) coordinates are evaluated on the leveled face
- **THEN** the system outputs the elevation angle in degrees, marking positive (>+3°), neutral (-2° to +3°), or downward (<-2°).
