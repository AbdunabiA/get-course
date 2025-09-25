// frontend/src/app/(protected)/student/layout.tsx
"use client";

import ProtectedLayout from "@/components/layouts/protectedLayout";
import StudentHeader from "@/components/student/studentHeader";
import StudentSidebar from "@/components/student/studentSidebar";

export default function StudentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedLayout requiredRole="INSTRUCTOR">
      <div className="min-h-screen bg-gray-50">
        <StudentHeader />
        <div className="flex">
          <StudentSidebar />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </ProtectedLayout>
  );
}
