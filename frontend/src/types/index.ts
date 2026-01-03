export interface Student {
  id: number;
  student_id: string;
  name: string;
  email: string;
  program_id: number;
}

export interface Course {
  id: number;
  course_code: string;
  name: string;
  credits: number;
  description?: string;
}

export interface Program {
  id: number;
  name: string;
  code: string;
  total_credits_required: number;
}

export interface RequirementProgress {
  requirement_id: number;
  requirement_name: string;
  requirement_type: string;
  credits_required: number;
  credits_completed: number;
  percentage: number;
  is_met: boolean;
  completed_courses: Course[];
  missing_courses: Course[];
}

export interface AuditReport {
  student: Student;
  program: Program;
  total_credits_required: number;
  total_credits_completed: number;
  overall_percentage: number;
  status: 'on_track' | 'at_risk' | 'completed';
  requirements: RequirementProgress[];
  graduation_eligible: boolean;
}

export interface Substitution {
  id: number;
  student_id: number;
  original_course_id: number;
  substitute_course_id: number;
  reason?: string;
  approved: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
