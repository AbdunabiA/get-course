// frontend/src/lib/api.ts
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/authStore'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

console.log('[API] Base URL:', API_BASE_URL)

// Create axios instance
const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Important: sends HTTP-only cookies automatically
    timeout: 10000, // 10 second timeout
    headers: {
        'Content-Type': 'application/json',
    },
})

interface FailedRequest {
    resolve: (value?: unknown) => void
    reject: (error?: unknown) => void
}

// Track if we're currently refreshing to prevent multiple refresh calls
let isRefreshing = false
let failedQueue: FailedRequest[] = []

// Process queued requests after refresh
const processQueue = (error: unknown = null) => {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) {
            reject(error)
        } else {
            resolve()
        }
    })
    failedQueue = []
}


// Request interceptor for logging
apiClient.interceptors.request.use(
    (config) => {
        const method = config.method?.toUpperCase()
        const url = config.url
        console.log(`[API] ${method} ${url}`)
        return config
    },
    (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
    }
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
    // Success response - pass through
    (response) => {
        console.log(`[API] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`)
        return response
    },

    // Error response - handle 401 and refresh
    async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

        // console?.error(`[API] ${error?.response?.status} ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`)

        // If error is 401 and we haven't already tried to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            console.log('[API] 401 error detected, attempting token refresh')

            // If we're already refreshing, queue this request
            if (isRefreshing) {
                console.log('[API] Refresh in progress, queuing request')
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                }).then(() => {
                    return apiClient(originalRequest)
                }).catch((err) => {
                    return Promise.reject(err)
                })
            }

            // Mark original request as retried
            originalRequest._retry = true
            isRefreshing = true

            try {
                console.log('[API] Calling refresh endpoint')

                // Call refresh endpoint
                await apiClient.post('/api/auth/refresh')

                console.log('[API] Token refresh successful')

                // Process queued requests
                processQueue(null)
                isRefreshing = false

                // Retry original request
                return apiClient(originalRequest)

            } catch (refreshError) {
                console.error('[API] Token refresh failed:', refreshError)

                // Refresh failed - clear auth and redirect to login
                processQueue(refreshError)
                isRefreshing = false

                // Clear auth state using Zustand store
                if (typeof window !== 'undefined') {
                    const { logout } = useAuthStore.getState()
                    logout()

                    // Redirect to login with current path as redirect
                    const currentPath = window.location.pathname
                    if (currentPath !== '/login' && currentPath !== '/register' && currentPath !== '/') {
                        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
                    } else {
                        window.location.href = '/login'
                    }
                }

                return Promise.reject(refreshError)
            }
        }

        // For all other errors, just pass through
        return Promise.reject(error)
    }
)

// API Methods with proper TypeScript types
export const api = {
    // Auth endpoints
    auth: {
        register: (data: { email: string; password: string; name: string }) =>
            apiClient.post('/api/auth/register', data),

        login: (data: { username: string; password: string }) =>
            apiClient.post('/api/auth/login', data, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            }),

        logout: () => apiClient.post('/api/auth/logout'),

        logoutAll: () => apiClient.post('/api/auth/logout-all'),

        me: () => apiClient.get('/api/auth/me'),

        refresh: () => apiClient.post('/api/auth/refresh')
    },

    // Course endpoints
    courses: {
        list: (params?: {
            skip?: number
            limit?: number
            search?: string
            category_id?: string
            instructor_id?: string
            published_only?: boolean
        }) => apiClient.get('/api/courses', { params }),

        get: (id: string) => apiClient.get(`/api/courses/${id}`),

        create: (data: {
            title: string
            description: string
            image?: string
            price?: number
            is_published?: boolean
            category_id?: string
        }) => apiClient.post('/api/courses', data),

        update: (id: string, data: Partial<{
            title: string
            description: string
            image: string
            price: number
            is_published: boolean
            category_id: string
        }>) => apiClient.put(`/api/courses/${id}`, data),

        delete: (id: string) => apiClient.delete(`/api/courses/${id}`),

        // Lessons
        lessons: {
            list: (courseId: string) => apiClient.get(`/api/courses/${courseId}/lessons`),

            create: (courseId: string, data: {
                title: string
                content: string
                video_url?: string
                order: number
            }) => apiClient.post(`/api/courses/${courseId}/lessons`, data)
        }
    },

    // Enrollment endpoints
    enrollments: {
        enroll: (courseId: string) =>
            apiClient.post(`/api/enrollments/courses/${courseId}/enroll`),

        list: () => apiClient.get('/api/enrollments/me'),

        updateProgress: (courseId: string, progress: number) =>
            apiClient.put(`/api/enrollments/courses/${courseId}/progress`, { progress }),

        unenroll: (courseId: string) =>
            apiClient.delete(`/api/enrollments/courses/${courseId}`),

        students: (courseId: string) =>
            apiClient.get(`/api/enrollments/courses/${courseId}/students`)
    },

    // Category endpoints
    categories: {
        list: () => apiClient.get('/api/categories'),

        get: (id: string) => apiClient.get(`/api/categories/${id}`),

        create: (data: { name: string }) => apiClient.post('/api/categories', data),

        update: (id: string, data: { name?: string }) =>
            apiClient.put(`/api/categories/${id}`, data),

        delete: (id: string) => apiClient.delete(`/api/categories/${id}`)
    },

    // Instructor endpoints
    instructor: {
        dashboard: () => apiClient.get('/api/instructor/dashboard'),

        courses: () => apiClient.get('/api/instructor/courses'),

        analytics: (courseId: string) =>
            apiClient.get(`/api/instructor/courses/${courseId}/analytics`),

        upgradeRequest: () => apiClient.post('/api/instructor/upgrade-request')
    }
}

export default apiClient