// frontend/src/components/layouts/ProtectedLayout.tsx
"use client";

import { useAuth } from "@/hooks/useAuth";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface ProtectedLayoutProps {
  children: React.ReactNode;
  requiredRole?: "STUDENT" | "INSTRUCTOR" | "ADMIN";
  fallback?: React.ReactNode;
}

function ProtectedLayout({
  children,
  requiredRole,
  fallback,
}: ProtectedLayoutProps) {
  const { isAuthenticated, isLoading, canAccessRoute, user } = useAuth();
  const router = useRouter();

  // Handle authentication and authorization
  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        // User not authenticated - redirect to login
        const currentPath = window.location.pathname;
        router.push(`/login?redirect=${encodeURIComponent(currentPath)}`);
        return;
      }

      if (requiredRole && !canAccessRoute(requiredRole)) {
        // User doesn't have required role - redirect to their appropriate dashboard
        switch (user?.role) {
          case "ADMIN":
            router.push("/admin/reports");
            break;
          case "INSTRUCTOR":
            router.push("/instructor/courses");
            break;
          case "STUDENT":
          default:
            router.push("/student/dashboard");
            break;
        }
      }
    }
  }, [isAuthenticated, isLoading, canAccessRoute, requiredRole, router, user]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show fallback if provided and user doesn't have access
  if (!isAuthenticated || (requiredRole && !canAccessRoute(requiredRole))) {
    if (fallback) {
      return <>{fallback}</>;
    }

    // Show loading while redirecting (middleware and useEffect will handle redirect)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  // User is authenticated and authorized - render children
  return <>{children}</>;
}


export default ProtectedLayout