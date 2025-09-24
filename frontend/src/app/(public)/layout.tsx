// frontend/src/app/(public)/layout.tsx

import Footer from "@/components/ui/footer";
import PublicHeader from "@/components/ui/publicHeader";


export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <PublicHeader />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
