export type Gym = {
  gym_id: number;
  gym_name: string;
  area: string;
  address: string;
  x_coordinate: number;
  y_coordinate: number;
  monthly_price: number;
  day_pass_price: number;
  rating: number;
  opening_time: number;
  closing_time: number;
  is_24_hours: boolean;
  gym_type: string;
  facilities: string[];
  beginner_friendly: boolean;
  female_friendly: boolean;
  student_discount: boolean;
  peak_crowd_level: string;
  parking_available: boolean;
  near_mrt: boolean;
  trainer_available: boolean;
  classes_available: boolean;
  display_hours: string;
  distance?: number;
  recommendation_score?: number;
  recommendation_reason?: string;
};

export type SearchPayload = {
  area?: string;
  max_budget?: number;
  min_rating?: number;
  required_facilities?: string[];
  open_at?: number;
  is_24_hours?: boolean;
  classes_available?: boolean;
  female_friendly?: boolean;
  gym_type?: string;
  user_x?: number;
  user_y?: number;
  sort_key?: string;
};

export type RecommendationPayload = {
  preferred_area?: string;
  max_budget?: number;
  min_rating?: number;
  preferred_facilities?: string[];
  preferred_time?: number;
  female_friendly?: boolean;
  classes_required?: boolean;
  user_x?: number;
  user_y?: number;
  fitness_goal?: string;
  skill_level?: string;
  preferred_gym_type?: string;
};
