export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-gray-900 to-black">
      <div className="container mx-auto px-6 text-center">
        <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-6">
          NØVRA
        </h1>
        <p className="text-lg md:text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
          Fashion minimalista e premium para quem busca posicionamento
        </p>
        <a
          href="/catalogo"
          className="inline-block px-8 py-4 bg-white text-black font-bold rounded-lg hover:bg-gray-200 transition-all"
        >
          Explorar Coleção
        </a>
      </div>
    </section>
  );
}
