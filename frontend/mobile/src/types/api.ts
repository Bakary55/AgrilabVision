export type AuthUser = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  age: number;
  user_type: string;
  created_at: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type SoilAnalysisResult = {
  soil_type: string;
  moisture_estimate: string;
  recommended_crops: string[];
  fertilizer_recommendations: string[];
  notes: string[];
  photo_quality_score: number;
  photo_quality_label: "low" | "medium" | "high";
  photo_quality_notes: string[];
};

export type WeatherCurrent = {
  description: string;
  temp_c: number;
  humidity: number;
  wind_speed_ms: number;
  location_name: string | null;
};

export type FarmingInsight = {
  advisory_text: string;
  weather_summary: string;
};

export type SoilImportReport = {
  inserted_count: number;
  failed_count: number;
  inserted_ids: number[];
  errors: string[];
};
