// frontend/src/types/api.ts
export interface User {
    id: string
    email: string
    role: 'STUDENT' | 'INSTRUCTOR' | 'ADMIN'
    created_at: string
    updated_at: string
}

export interface Profile {
    id?: string
    name: string
    bio?: string
    avatar?: string
    user_id?: string
    created_at?: string
    updated_at?: string
}

export interface Category {
    id: string
    name: string
}

export interface Course {
    id: string
    title: string
    description: string
    image?: string
    price?: number
    is_published: boolean
    instructor_id: string
    category_id?: string
    created_at: string
    updated_at: string
    lessons_count?: number
    enrollments_count?: number
    instructor?: User
    category?: Category
}

export interface Lesson {
    id: string
    title: string
    content: string
    video_url?: string
    order: number
    course_id: string
    created_at: string
    updated_at: string
}

export interface Enrollment {
    id: string
    student_id: string
    course_id: string
    progress: number
    created_at: string
    updated_at: string
    course?: Course
    student?: User
}

export interface Review {
    id: string
    rating: number
    comment: string
    student_id: string
    course_id: string
    created_at: string
    student?: User
}

// API Request Types
export interface LoginRequest {
    username: string // email
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    name: string
}

export interface CreateCourseRequest {
    title: string
    description: string
    image?: string
    price?: number
    is_published?: boolean
    category_id?: string
}

export interface UpdateCourseRequest {
    title?: string
    description?: string
    image?: string
    price?: number
    is_published?: boolean
    category_id?: string
}

export interface CreateLessonRequest {
    title: string
    content: string
    video_url?: string
    order: number
}

export interface UpdateLessonRequest {
    title?: string
    content?: string
    video_url?: string
    order?: number
}

export interface CreateCategoryRequest {
    name: string
}

export interface UpdateProgressRequest {
    progress: number
}

// API Response Types
export interface AuthResponse {
    user: User
    profile?: Profile
}

export interface LoginResponse {
    message: string
    user: {
        id: string
        email: string
        role: string
    }
}

export interface EnrollmentResponse {
    message: string
    enrollment: {
        id: string
        course_id: string
        course_title: string
        progress: number
        enrolled_at: string
    }
}

export interface InstructorDashboard {
    overview: {
        total_courses: number
        published_courses: number
        total_students: number
        total_lessons: number
        average_rating: number
    }
    recent_enrollments: Array<{
        student_email: string
        course_title: string
        enrolled_at: string
        progress: number
    }>
}

export interface CourseAnalytics {
    course_info: {
        id: string
        title: string
        price: number
        is_published: boolean
        lessons_count: number
    }
    enrollment_stats: {
        total_enrollments: number
        completed_enrollments: number
        average_progress: number
        completion_rate: number
    }
    review_stats: {
        total_reviews: number
        average_rating: number
        rating_distribution: {
            "5_star": number
            "4_star": number
            "3_star": number
            "2_star": number
            "1_star": number
        }
    }
    revenue_stats: {
        total_revenue: number
        revenue_per_enrollment: number
    }
}

// Query Parameters
export interface CoursesQueryParams {
    skip?: number
    limit?: number
    search?: string
    category_id?: string
    instructor_id?: string
    published_only?: boolean
}

// Error Types
export interface ApiError {
    detail: string
    status_code?: number
}

export interface ValidationError {
    detail: Array<{
        loc: string[]
        msg: string
        type: string
    }>
}

// Utility Types
export type UserRole = User['role']

export interface PaginatedResponse<T> {
    items: T[]
    total: number
    skip: number
    limit: number
}

// Form Types (for react-hook-form)
export interface LoginFormData {
    email: string
    password: string
}

export interface RegisterFormData {
    name: string
    email: string
    password: string
    confirmPassword: string
}

export interface CourseFormData {
    title: string
    description: string
    image?: string
    price?: number
    is_published: boolean
    category_id?: string
}

export interface LessonFormData {
    title: string
    content: string
    video_url?: string
    order: number
}

export interface ProfileFormData {
    name: string
    bio?: string
    avatar?: string
}