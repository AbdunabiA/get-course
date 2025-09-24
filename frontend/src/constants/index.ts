// frontend/src/constants/index.ts

// API Configuration
export const API_CONFIG = {
    BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    TIMEOUT: 10000, // 10 seconds
} as const

// Application Routes
export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    COURSES: '/courses',
    STUDENT: {
        DASHBOARD: '/student',
        PROFILE: '/student/profile',
        COURSES: '/student/courses',
        COURSE_DETAIL: (id: string) => `/student/courses/${id}`,
    },
    INSTRUCTOR: {
        DASHBOARD: '/instructor',
        COURSES: '/instructor/courses',
        CREATE_COURSE: '/instructor/courses/new',
        EDIT_COURSE: (id: string) => `/instructor/courses/${id}/edit`,
        COURSE_ANALYTICS: (id: string) => `/instructor/courses/${id}/analytics`,
        PROFILE: '/instructor/profile',
    },
    ADMIN: {
        DASHBOARD: '/admin',
        USERS: '/admin/users',
        COURSES: '/admin/courses',
        CATEGORIES: '/admin/categories',
    },
} as const

// User Roles
export const USER_ROLES = {
    STUDENT: 'STUDENT',
    INSTRUCTOR: 'INSTRUCTOR',
    ADMIN: 'ADMIN',
} as const

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES]

// Role Display Names
export const ROLE_DISPLAY_NAMES = {
    [USER_ROLES.STUDENT]: 'Student',
    [USER_ROLES.INSTRUCTOR]: 'Instructor',
    [USER_ROLES.ADMIN]: 'Administrator',
} as const

// Role-based Route Access
export const ROLE_ROUTES = {
    [USER_ROLES.STUDENT]: ['/student'],
    [USER_ROLES.INSTRUCTOR]: ['/instructor', '/student'], // Instructors can access student routes
    [USER_ROLES.ADMIN]: ['/admin', '/instructor', '/student'], // Admins can access all routes
} as const

// Query Configuration
export const QUERY_CONFIG = {
    STALE_TIME: 1000 * 60 * 5, // 5 minutes
    CACHE_TIME: 1000 * 60 * 10, // 10 minutes
    RETRY_ATTEMPTS: 1,
} as const

// Pagination
export const PAGINATION = {
    DEFAULT_LIMIT: 20,
    DEFAULT_SKIP: 0,
    MAX_LIMIT: 100,
} as const

// File Upload
export const FILE_UPLOAD = {
    MAX_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
    ALLOWED_VIDEO_TYPES: ['video/mp4', 'video/webm'],
} as const

// Form Validation
export const VALIDATION = {
    EMAIL: {
        REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        MESSAGE: 'Please enter a valid email address',
    },
    PASSWORD: {
        MIN_LENGTH: 8,
        MESSAGE: 'Password must be at least 8 characters long',
    },
    COURSE: {
        TITLE: {
            MIN_LENGTH: 3,
            MAX_LENGTH: 100,
        },
        DESCRIPTION: {
            MIN_LENGTH: 10,
            MAX_LENGTH: 1000,
        },
        PRICE: {
            MIN: 0,
            MAX: 999999,
        },
    },
    LESSON: {
        TITLE: {
            MIN_LENGTH: 3,
            MAX_LENGTH: 100,
        },
        CONTENT: {
            MIN_LENGTH: 10,
        },
    },
} as const

// Toast Messages
export const TOAST_MESSAGES = {
    AUTH: {
        LOGIN_SUCCESS: 'Welcome back!',
        LOGIN_ERROR: 'Login failed. Please check your credentials.',
        REGISTER_SUCCESS: 'Account created successfully!',
        REGISTER_ERROR: 'Registration failed. Please try again.',
        LOGOUT_SUCCESS: 'Logged out successfully',
        SESSION_EXPIRED: 'Your session has expired. Please log in again.',
    },
    COURSE: {
        CREATE_SUCCESS: 'Course created successfully!',
        CREATE_ERROR: 'Failed to create course. Please try again.',
        UPDATE_SUCCESS: 'Course updated successfully!',
        UPDATE_ERROR: 'Failed to update course. Please try again.',
        DELETE_SUCCESS: 'Course deleted successfully!',
        DELETE_ERROR: 'Failed to delete course. Please try again.',
        PUBLISH_SUCCESS: 'Course published successfully!',
        UNPUBLISH_SUCCESS: 'Course unpublished successfully!',
    },
    ENROLLMENT: {
        ENROLL_SUCCESS: 'Successfully enrolled in course!',
        ENROLL_ERROR: 'Failed to enroll in course. Please try again.',
        UNENROLL_SUCCESS: 'Successfully unenrolled from course!',
        UNENROLL_ERROR: 'Failed to unenroll from course. Please try again.',
        PROGRESS_UPDATED: 'Progress updated successfully!',
    },
    LESSON: {
        CREATE_SUCCESS: 'Lesson created successfully!',
        CREATE_ERROR: 'Failed to create lesson. Please try again.',
        UPDATE_SUCCESS: 'Lesson updated successfully!',
        UPDATE_ERROR: 'Failed to update lesson. Please try again.',
        DELETE_SUCCESS: 'Lesson deleted successfully!',
        DELETE_ERROR: 'Failed to delete lesson. Please try again.',
    },
    GENERAL: {
        LOADING: 'Loading...',
        ERROR: 'Something went wrong. Please try again.',
        NETWORK_ERROR: 'Network error. Please check your connection.',
        UNAUTHORIZED: 'You are not authorized to perform this action.',
        FORBIDDEN: 'Access denied.',
        NOT_FOUND: 'The requested resource was not found.',
        SERVER_ERROR: 'Server error. Please try again later.',
    },
} as const

// Course Status
export const COURSE_STATUS = {
    DRAFT: 'draft',
    PUBLISHED: 'published',
} as const

// Progress Thresholds
export const PROGRESS = {
    COMPLETED_THRESHOLD: 100,
    ALMOST_COMPLETE_THRESHOLD: 90,
    HALFWAY_THRESHOLD: 50,
    STARTED_THRESHOLD: 1,
} as const

// Rating System
export const RATING = {
    MIN: 1,
    MAX: 5,
    STARS: [1, 2, 3, 4, 5],
} as const

// Date Formats
export const DATE_FORMATS = {
    FULL: 'MMMM dd, yyyy',
    SHORT: 'MMM dd, yyyy',
    TIME: 'HH:mm',
    DATETIME: 'MMM dd, yyyy HH:mm',
    ISO: 'yyyy-MM-dd',
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
    AUTH: 'auth-storage',
    THEME: 'theme',
    LANGUAGE: 'language',
    PREFERENCES: 'user-preferences',
} as const

// Error Codes
export const ERROR_CODES = {
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    VALIDATION_ERROR: 422,
    SERVER_ERROR: 500,
} as const