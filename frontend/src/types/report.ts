export interface ThreePartsLevels {
  trichion_y: number;
  brow_y: number;
  subnasale_y: number;
  menton_y: number;
}

export interface FacialCaliperPoints {
  trichion: [number, number];
  menton: [number, number];
  zygoma_left: [number, number];
  zygoma_right: [number, number];
  jaw_left: [number, number];
  jaw_right: [number, number];
  left_eye_inner: [number, number];
  left_eye_outer: [number, number];
  right_eye_inner: [number, number];
  right_eye_outer: [number, number];
  nose_tip: [number, number];
  subnasale: [number, number];
  nasion?: [number, number];
  alar_left?: [number, number];
  alar_right?: [number, number];
  brow_peak_left?: [number, number];
  brow_peak_right?: [number, number];
  lip_left?: [number, number];
  lip_right?: [number, number];
  lip_top?: [number, number];
  contour_polygon: [number, number][];
  three_parts_levels: ThreePartsLevels;
}

export interface FacialMetrics {
  face_ratio: number;
  jaw_angle_degree: number;
  canthal_tilt_degree: number;
  palpebral_ratio: number;
  roll_angle_degree: number;
  three_parts_ratio: string;
  intercanthal_ratio: number;
  nasal_width_ratio: number;
  lip_thickness_ratio: number;
  face_type: string;
  jaw_type: string;
  eye_tilt_type: string;
  intercanthal_type: string;
  caliper_points: FacialCaliperPoints;
}

export interface FeatureItem {
  title: string;
  desc: string;
}

export interface FeaturesSection {
  eyebrows?: FeatureItem;
  eyes: FeatureItem;
  glabella?: FeatureItem;
  nose: FeatureItem;
  mouth: FeatureItem;
  jaw?: FeatureItem;
}

export interface LLMReportContent {
  summary: {
    archetype: string;
    aura_title: string;
    tags: string[];
  };
  structure: {
    three_parts: {
      ratio: string;
      verdict: string;
      analysis: string;
    };
    bone_frame: {
      title: string;
      analysis: string;
    };
    ear_evidence: {
      title: string;
      analysis: string;
    };
  };
  features: FeaturesSection;
  radar_scores: {
    intellect: number;
    presence: number;
    wealth_affinity: number;
    equanimity: number;
  };
  modern_advice: {
    style: string;
    expression: string;
    mindset: string;
  };
}

export interface FacialReportResponse {
  code: number;
  message: string;
  provider_used: string;
  metrics: FacialMetrics;
  report: LLMReportContent;
}
