import Footer from "@/components/homePage/footer";
import HeroSection from "@/components/homePage/heroSection";
import PublicHeader from "@/components/homePage/publicHeader";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <PublicHeader />
      <main className="flex-1">{children}</main>
      <HeroSection />
      <Footer />
    </div>
  );
}
