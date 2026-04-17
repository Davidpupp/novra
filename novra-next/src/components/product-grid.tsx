"use client";

import { motion } from "framer-motion";

const mockProducts = [
  { id: "nv-001", name: "Oversized Tee Shadow", price: 289, tag: "Drop limitado" },
  { id: "nv-002", name: "Cargo Pant Concrete", price: 499, tag: "Importado" },
  { id: "nv-003", name: "Tech Jacket Noir", price: 899, tag: "Premium" },
  { id: "nv-004", name: "Utility Hoodie Void", price: 649, tag: "Exclusivo" },
  { id: "nv-005", name: "Denim Relaxed Mist", price: 549, tag: "Lifestyle" },
  { id: "nv-006", name: "Sneaker Mono Layer", price: 1199, tag: "Streetwear" }
];

export function ProductGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {mockProducts.map((product, index) => (
        <motion.article
          key={product.id}
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.4, delay: index * 0.04 }}
          className="rounded-2xl border border-zinc-300 bg-white/70 p-4 shadow-lg shadow-black/10"
        >
          <div className="mb-3 h-52 rounded-xl bg-gradient-to-br from-zinc-200 via-zinc-100 to-zinc-300" />
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-600">{product.tag}</span>
            <span className="text-sm font-black">R$ {product.price}</span>
          </div>
          <h3 className="text-lg font-bold text-zinc-900">{product.name}</h3>
          <button className="mt-4 w-full rounded-xl bg-zinc-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-zinc-800">
            Comprar agora
          </button>
        </motion.article>
      ))}
    </div>
  );
}
