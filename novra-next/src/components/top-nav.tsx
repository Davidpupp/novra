"use client";

import { motion } from "framer-motion";

const navLinks = ["Drops", "Exclusivos", "Lifestyle", "Conta"];

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/80 glass">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xl font-black tracking-[0.28em]">
          NØVRA
        </motion.div>

        <nav className="hidden items-center gap-6 md:flex">
          {navLinks.map((link) => (
            <a key={link} href="#" className="text-sm font-medium text-zinc-700 transition hover:text-zinc-950">
              {link}
            </a>
          ))}
        </nav>

        <button className="rounded-full bg-zinc-950 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white">
          Entrar
        </button>
      </div>
    </header>
  );
}
