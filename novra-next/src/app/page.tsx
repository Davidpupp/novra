import { HeroSection } from "@/components/hero-section";
import { ProductGrid } from "@/components/product-grid";
import { TopNav } from "@/components/top-nav";

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <TopNav />
      <HeroSection />
      <section className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="mb-4 text-3xl font-black tracking-tight text-white md:text-4xl">Drop Limitado</h2>
        <p className="mb-8 max-w-2xl text-sm text-zinc-200 md:text-base">
          Pecas importadas selecionadas para quem veste posicionamento. Quantidades reduzidas e alta rotatividade.
        </p>
        <ProductGrid />
      </section>
    </main>
  );
}
