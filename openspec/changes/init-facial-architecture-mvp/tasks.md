## 1. Backend Infrastructure & CV Geometry Engine

- [x] 1.1 Initialize FastAPI backend structure with dependencies (FastAPI, OpenCV, MediaPipe, Pydantic, Uvicorn)
- [x] 1.2 Implement facial landmark detection and 2D roll angle leveling (de-roll) in `FaceMeshService`
- [x] 1.3 Implement facial aspect ratio calculation (Face Length / Bizygomatic Width)
- [x] 1.4 Implement mandibular jaw convergence angle calculation (Chin to Gonion vector angle)
- [x] 1.5 Implement canthal tilt angle and palpebral fissure length/width ratio calculation
- [x] 1.6 Add face posture validation and error handling for missing/extreme-angle faces

## 2. RAG Knowledge Base & Prompt Engineering

- [x] 2.1 Set up embedded vector store (ChromaDB) and local data persistence
- [x] 2.2 Curate and index structured corpus chunks (Bing Jian, Ma Yi, modern craniofacial aesthetics & micro-expression psychology)
- [x] 2.3 Implement dynamic query synthesizer mapping detected CV metrics to domain queries
- [x] 2.4 Build prompt injection template formatting retrieved knowledge chunks and strict JSON output instructions

## 3. Model Provider Adapter & Failover

- [x] 3.1 Define `BaseLLMProvider` abstract interface and `FacialReportResponse` Pydantic models
- [x] 3.2 Implement `GeminiFlashProvider` for Gemini 1.5 Flash 8B with proxy support and JSON Schema
- [x] 3.3 Implement `QwenVLProvider` for Aliyun Qwen-VL-Plus as domestic secondary fallback
- [x] 3.4 Implement `ProviderManager` with automatic timeout handling (6s) and seamless failover logic
- [x] 3.5 Expose POST `/api/v1/analyze` endpoint accepting image and returning validated report schema with caliper coordinates

## 4. Frontend Project Setup & Design System

- [x] 4.1 Scaffold Uni-app (Vue 3 + TypeScript + Vite + UnoCSS) project
- [x] 4.2 Configure Design Tokens in UnoCSS/Tailwind (Obsidian background `#0C0D0E`, hairline border `#24262B`, typography, and 4px grid)
- [x] 4.3 Create base UI components (hairline cards, tags, monochrome buttons, typography headers)

## 5. Core Views & Interactive Ceremonies

- [x] 5.1 Build Hero / Landing page with title typography, privacy disclaimer, and capture trigger
- [x] 5.2 Build `CameraGuideMask` component with elliptical guide overlay, inner canthi crosshairs, and ear alignment indicators
- [x] 5.3 Build `ScanCeremonyOverlay` with moving hairline laser and progressive status calculation logs
- [x] 5.4 Build `FacialCaliperCanvas` rendering geometric calipers, angle marks, and anchor points over the greyscale photo
- [x] 5.5 Build `EditorialReportCard` layout displaying archetype stamp, three-parts ratio, ear evidence, radar chart, and advice cards

## 6. Poster Generation & Verification

- [x] 6.1 Implement `PosterCanvas` exporting 9:16 high-resolution aesthetic long image with mini-program QR code
- [x] 6.2 Connect Uni-app frontend to FastAPI backend `/api/v1/analyze` endpoint
- [x] 6.3 Perform end-to-end testing with sample portrait images and verify automatic failover between Gemini and Qwen-VL
