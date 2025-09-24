// frontend/src/hooks/useAuth.ts
import React from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { useAuthStore, User, Profile } from '@/stores/authStore'
import { queryKeys } from '@/lib/queryClient'
import { toast } from 'sonner'

interface LoginData {
    username: string // email
    password: string
}

interface RegisterData {
    email: string
    password: string
    name: string
}

interface AuthResponse {
    user: User
    profile?: Profile
}

export const useAuth = () => {
    const router = useRouter()
    const queryClient = useQueryClient()
    const {
        user,
        profile,
        isAuthenticated,
        isLoading,
        login: setAuthState,
        logout: clearAuthState,
        setLoading,
        setUser,
        setProfile
    } = useAuthStore()

    // Get current user info from server
    const { data: authData, error, isLoading: isQueryLoading } = useQuery({
        queryKey: queryKeys.auth.me(),
        queryFn: async () => {
            const response = await api.auth.me()
            return response.data
        },
        enabled: !isAuthenticated || !user, // Only fetch if not authenticated
        retry: false, // Don't retry failed auth requests
        staleTime: 1000 * 60 * 5, // 5 minutes
    })

    // Sync server data with local state
    React.useEffect(() => {
        if (authData) {
            setAuthState(authData.user, authData.profile)
            setLoading(false)
        } else if (error) {
            clearAuthState()
            setLoading(false)
        }
    }, [authData, error, setAuthState, clearAuthState, setLoading])

    // Login mutation
    const loginMutation = useMutation({
        mutationFn: async (data: LoginData) => {
            const response = await api.auth.login(data)
            return response.data
        },
        onSuccess: async (data) => {
            // After login, fetch user data
            try {
                const userResponse = await api.auth.me()
                const userData = userResponse.data

                setAuthState(userData.user, userData.profile)

                // Invalidate and refetch auth-related queries
                queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() })

                toast?.success('Login successful!')

                // Redirect based on role or to intended destination
                const params = new URLSearchParams(window.location.search)
                const redirect = params.get('redirect')

                if (redirect && redirect !== '/login' && redirect !== '/register') {
                    router.push(redirect)
                } else {
                    // Redirect based on user role
                    switch (userData.user.role) {
                        case 'ADMIN':
                            router.push('/admin')
                            break
                        case 'INSTRUCTOR':
                            router.push('/instructor')
                            break
                        default:
                            router.push('/student')
                    }
                }
            } catch (error) {
                console.error('Failed to fetch user data after login:', error)
                toast?.error('Login successful, but failed to load user data')
            }
        },
        onError: (error: any) => {
            console.error('Login failed:', error)
            const errorMessage = error?.response?.data?.detail || 'Login failed'
            toast?.error(errorMessage)
        }
    })

    // Register mutation
    const registerMutation = useMutation({
        mutationFn: async (data: RegisterData) => {
            const response = await api.auth.register(data)
            return response.data
        },
        onSuccess: async (data) => {
            // After registration, user should be auto-logged in
            try {
                const userResponse = await api.auth.me()
                const userData = userResponse.data

                setAuthState(userData.user, userData.profile)

                queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() })

                toast?.success('Registration successful!')

                // Redirect to appropriate dashboard
                switch (userData.user.role) {
                    case 'ADMIN':
                        router.push('/admin/dashboard')
                        break
                    case 'INSTRUCTOR':
                        router.push('/instructor/dashboard')
                        break
                    default:
                        router.push('/student/dashboard')
                }
            } catch (error) {
                console.error('Failed to fetch user data after registration:', error)
                toast?.error('Registration successful, but failed to load user data')
            }
        },
        onError: (error: any) => {
            console.error('Registration failed:', error)
            const errorMessage = error?.response?.data?.detail || 'Registration failed'
            toast?.error(errorMessage)
        }
    })

    // Logout mutation
    const logoutMutation = useMutation({
        mutationFn: api.auth.logout,
        onSuccess: () => {
            clearAuthState()
            queryClient.clear() // Clear all cached data
            toast?.success('Logged out successfully')
            router.push('/login')
        },
        onError: (error: any) => {
            // Even if logout API fails, clear local state
            clearAuthState()
            queryClient.clear()
            console.error('Logout error:', error)
            router.push('/login')
        }
    })

    // Logout from all devices
    const logoutAllMutation = useMutation({
        mutationFn: api.auth.logoutAll,
        onSuccess: () => {
            clearAuthState()
            queryClient.clear()
            toast?.success('Logged out from all devices')
            router.push('/login')
        },
        onError: (error: any) => {
            clearAuthState()
            queryClient.clear()
            console.error('Logout all error:', error)
            router.push('/login')
        }
    })

    // Helper functions
    const hasRole = (role: User['role']) => {
        return user?.role === role
    }

    const hasAnyRole = (roles: User['role'][]) => {
        return user ? roles.includes(user.role) : false
    }

    const canAccessRoute = (requiredRole?: User['role']) => {
        if (!requiredRole) return isAuthenticated
        if (!user) return false

        // Admin can access everything
        if (user.role === 'ADMIN') return true

        // Exact role match
        if (user.role === requiredRole) return true

        // Instructors can access student routes
        if (requiredRole === 'STUDENT' && user.role === 'INSTRUCTOR') return true

        return false
    }

    return {
        // State
        user,
        profile,
        isAuthenticated,
        isLoading: isLoading || isQueryLoading,

        // Actions
        login: loginMutation.mutate,
        register: registerMutation.mutate,
        logout: logoutMutation.mutate,
        logoutAll: logoutAllMutation.mutate,

        // Mutation states
        isLoggingIn: loginMutation.isPending,
        isRegistering: registerMutation.isPending,
        isLoggingOut: logoutMutation.isPending,

        // Utility functions
        hasRole,
        hasAnyRole,
        canAccessRoute,

        // Manual state setters (for edge cases)
        setUser,
        setProfile,
    }
}

// Hook for protecting routes
export const useRequireAuth = (requiredRole?: User['role']) => {
    const { isAuthenticated, isLoading, canAccessRoute, user } = useAuth()
    const router = useRouter()

    React.useEffect(() => {
        if (!isLoading) {
            if (!isAuthenticated) {
                const currentPath = window.location.pathname
                router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
            } else if (requiredRole && !canAccessRoute(requiredRole)) {
                // Redirect to appropriate dashboard if user doesn't have required role
                switch (user?.role) {
                    case 'ADMIN':
                        router.push('/admin')
                        break
                    case 'INSTRUCTOR':
                        router.push('/instructor')
                        break
                    default:
                        router.push('/student')
                }
            }
        }
    }, [isAuthenticated, isLoading, canAccessRoute, requiredRole, router, user])

    return { isAuthenticated, isLoading, hasAccess: canAccessRoute(requiredRole) }
}