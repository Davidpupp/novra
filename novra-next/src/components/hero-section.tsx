"use client";

import { motion } from "framer-motion";

const highlights = [
  "Status",
  "Exclusividade",
  "Lifestyle",
  "Streetwear premium",
  "Drop limitado",
  "Importados selecionados"
];

export function HeroSection() {
  return (
    <section className="mx-auto flex max-w-7xl flex-col gap-8 px-6 pb-10 pt-24">
      <motion.p
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-fit rounded-full border border-zinc-300 bg-white/70 px-4 py-1 text-xs font-semibold tracking-[0.25em] text-zinc-700"
      >
        NØVRA DROP 01
      </motion.p>

      <motion.h1
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, delay: 0.08 }}
        className="text-gradient max-w-4xl text-4xl font-black leading-tight md:text-6xl"
      >
        Não vendemos roupa. Vendemos identidade.
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, delay: 0.16 }}
        className="max-w-2xl text-base text-zinc-700 md:text-lg"
      >
        A NØVRA posiciona você com curadoria de peças premium para um lifestyle urbano de alto impacto.
      </motion.p>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex flex-wrap gap-3"
      >
        {highlights.map((item) => (
          <span key={item} className="rounded-full border border-zinc-300 bg-white/60 px-4 py-2 text-sm font-medium text-zinc-800">
            {item}
          </span>
        ))}
      </motion.div>
    </section>
  );
}
