// frontend/src/stores/authStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface User {
    id: string
    email: string
    role: 'STUDENT' | 'INSTRUCTOR' | 'ADMIN'
    created_at: string
    updated_at: string
}

export interface Profile {
    name: string
    bio?: string
    avatar?: string
}

interface AuthState {
    // State
    user: User | null
    profile: Profile | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    setUser: (user: User | null) => void
    setProfile: (profile: Profile | null) => void
    setLoading: (loading: boolean) => void
    login: (user: User, profile?: Profile) => void
    logout: () => void
    updateProfile: (profile: Partial<Profile>) => void
}

export const useAuthStore = create<AuthState>()(
    devtools(
        persist(
            (set) => ({
                // Initial state
                user: null,
                profile: null,
                isAuthenticated: false,
                isLoading: true,

                // Actions
                setUser: (user) => set({
                    user,
                    isAuthenticated: !!user
                }),

                setProfile: (profile) => set({ profile }),

                setLoading: (loading) => set({ isLoading: loading }),

                login: (user, profile) => set({
                    user,
                    profile: profile || null,
                    isAuthenticated: true,
                    isLoading: false
                }),

                logout: () => set({
                    user: null,
                    profile: null,
                    isAuthenticated: false,
                    isLoading: false
                }),

                updateProfile: (newProfile) => set((state) => ({
                    profile: state.profile ? { ...state.profile, ...newProfile } : null
                }))
            }),
            {
                name: 'auth-storage',
                // Only persist non-sensitive user data
                partialize: (state) => ({
                    user: state.user,
                    profile: state.profile,
                    isAuthenticated: state.isAuthenticated
                })
            }
        ),
        { name: 'auth-store' }
    )
)