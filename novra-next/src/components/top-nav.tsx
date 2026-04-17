export function TopNav() {
  return (
    <nav className="border-b border-zinc-800 bg-black/50 backdrop-blur-xl">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-wider">NØVRA</h1>
        <div className="flex gap-6 text-sm">
          <a href="/" className="hover:text-zinc-300 transition-colors">Home</a>
          <a href="/catalogo" className="hover:text-zinc-300 transition-colors">Catálogo</a>
          <a href="/carrinho" className="hover:text-zinc-300 transition-colors">Carrinho</a>
        </div>
      </div>
    </nav>
  );
}
