// middleware.ts (root level, same as package.json)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define route patterns
const publicRoutes = [
    '/',
    '/login',
    '/register',
    '/courses', // Public course browsing
    '/api/health', // Health check
]

const protectedRoutes = [
    '/student',
    '/instructor',
    '/admin',
    '/profile',
    '/dashboard',
]

const roleBasedRoutes = {
    admin: ['/admin'],
    instructor: ['/instructor'],
    student: ['/student'],
}

interface UserPayload {
    sub: string // user id
    email: string
    role: 'STUDENT' | 'INSTRUCTOR' | 'ADMIN'
    exp: number
}

// Verify JWT token without secret (just decode and check structure)
function verifyTokenStructure(token: string): UserPayload | null {
    try {
        // Split JWT token
        const parts = token.split('.')
        if (parts.length !== 3) return null

        // Decode payload (base64)
        const payload = JSON.parse(atob(parts[1]))

        // Check if token has required fields and isn't expired
        if (!payload.sub || !payload.email || !payload.role || !payload.exp) {
            return null
        }

        // Check expiration (exp is in seconds, Date.now() is in milliseconds)
        if (payload.exp * 1000 < Date.now()) {
            return null
        }

        return payload as UserPayload
    } catch (error) {
        console.error('Token verification failed:', error)
        return null
    }
}

// Check if user has access to route based on role
function hasRoleAccess(userRole: string, pathname: string): boolean {
    // Admin has access to everything
    if (userRole === 'ADMIN') return true

    // Check role-specific routes
    for (const [role, routes] of Object.entries(roleBasedRoutes)) {
        if (userRole.toLowerCase() === role) {
            return routes.some(route => pathname.startsWith(route))
        }
    }

    return false
}

export async function middleware(request: NextRequest) {

    const { pathname } = request.nextUrl
    // Skip middleware for static files and API routes
    if (
        pathname.startsWith('/_next/') ||
        pathname.startsWith('/api/') ||
        pathname.includes('.') // Static files (images, etc.)
    ) {
        return NextResponse.next()
    }

    // Get access token from cookies
    const accessToken = request.cookies.get('access_token')?.value
    const refreshToken = request.cookies.get('refresh_token')?.value

    console.log(`[Middleware] ${pathname} - Token exists: ${!!accessToken}`)

    // Check if route is public
    const isPublicRoute = publicRoutes.some(route =>
        pathname === route || (route === '/' && pathname === '/')
    )

    // Check if route requires authentication
    const isProtectedRoute = protectedRoutes.some(route =>
        pathname.startsWith(route)
    )

    // Public routes - allow access
    if (isPublicRoute && !isProtectedRoute) {
        // If user is logged in and trying to access login/register, redirect to dashboard
        if ((pathname === '/login' || pathname === '/register') && accessToken) {
            const userPayload = verifyTokenStructure(accessToken)
            if (userPayload) {
                // Redirect based on role
                const redirectUrl = new URL(request.url)
                switch (userPayload.role) {
                    case 'ADMIN':
                        redirectUrl.pathname = '/admin/reports'
                        break
                    case 'INSTRUCTOR':
                        redirectUrl.pathname = '/instructor/courses'
                        break
                    default:
                        redirectUrl.pathname = '/student/dashboard'
                }
                return NextResponse.redirect(redirectUrl)
            }
        }

        return NextResponse.next()
    }

    // Protected routes - require authentication
    if (isProtectedRoute || !isPublicRoute) {
        // No access token - redirect to login
        if (!accessToken) {
            console.log('[Middleware] No access token, redirecting to login')
            const loginUrl = new URL('/login', request.url)
            loginUrl.searchParams.set('redirect', pathname)
            return NextResponse.redirect(loginUrl)
        }

        // Verify token structure
        const userPayload = verifyTokenStructure(accessToken)

        // Invalid token - try to refresh or redirect to login
        if (!userPayload) {
            console.log('[Middleware] Invalid access token')

            // If we have a refresh token, let the page try to refresh
            if (refreshToken) {
                console.log('[Middleware] Refresh token exists, allowing page load for refresh attempt')
                return NextResponse.next()
            }

            // No refresh token - redirect to login
            const loginUrl = new URL('/login', request.url)
            loginUrl.searchParams.set('redirect', pathname)
            return NextResponse.redirect(loginUrl)
        }

        // Check role-based access
        if (!hasRoleAccess(userPayload.role, pathname)) {
            console.log(`[Middleware] Role ${userPayload.role} denied access to ${pathname}`)

            // Redirect to appropriate dashboard based on role
            const dashboardUrl = new URL(request.url)
            switch (userPayload.role) {
                case 'ADMIN':
                    dashboardUrl.pathname = '/admin/reports'
                    break
                case 'INSTRUCTOR':
                    dashboardUrl.pathname = '/instructor/courses'
                    break
                default:
                    dashboardUrl.pathname = '/student/dashboard'
            }

            return NextResponse.redirect(dashboardUrl)
        }

        // Add user info to headers for pages to use
        const response = NextResponse.next()
        response.headers.set('x-user-id', userPayload.sub)
        response.headers.set('x-user-email', userPayload.email)
        response.headers.set('x-user-role', userPayload.role)

        console.log(`[Middleware] Access granted to ${userPayload.role} for ${pathname}`)
        return response
    }

    // Default - allow access
    return NextResponse.next()
}

// Configure which routes middleware should run on
export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - public files (images, etc.)
         */
        '/((?!_next/static|_next/image|favicon.ico|.*\\.).*)',
    ],
}

