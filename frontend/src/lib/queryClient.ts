// frontend/src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query'
interface CoursesListParams {
    skip?: number
    limit?: number
    search?: string
    category_id?: string
    instructor_id?: string
    published_only?: boolean
}

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Stale time: 5 minutes
            staleTime: 1000 * 60 * 5,
            // Cache time: 10 minutes  
            gcTime: 1000 * 60 * 10,
            // Retry failed requests 1 time
            retry: 1,
            // Don't refetch on window focus by default
            refetchOnWindowFocus: false,
        },
        mutations: {
            // Retry failed mutations 0 times
            retry: 0,
        },
    },
})

// Query Keys Factory
export const queryKeys = {
    // Auth
    auth: {
        me: () => ['auth', 'me'] as const,
    },

    // Courses
    courses: {
        all: () => ['courses'] as const,
        list: (params?: CoursesListParams) => ['courses', 'list', params] as const,
        detail: (id: string) => ['courses', 'detail', id] as const,
        lessons: (courseId: string) => ['courses', courseId, 'lessons'] as const,
    },

    // Enrollments
    enrollments: {
        all: () => ['enrollments'] as const,
        list: () => ['enrollments', 'list'] as const,
        students: (courseId: string) => ['enrollments', 'students', courseId] as const,
    },

    // Categories
    categories: {
        all: () => ['categories'] as const,
        list: () => ['categories', 'list'] as const,
        detail: (id: string) => ['categories', 'detail', id] as const,
    },

    // Instructor
    instructor: {
        all: () => ['instructor'] as const,
        dashboard: () => ['instructor', 'dashboard'] as const,
        courses: () => ['instructor', 'courses'] as const,
        analytics: (courseId: string) => ['instructor', 'analytics', courseId] as const,
    },
}