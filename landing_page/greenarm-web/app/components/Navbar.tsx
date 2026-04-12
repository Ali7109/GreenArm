"use client";

import { motion } from "framer-motion";

const links = ["Problem", "Solution", "System", "Features", "Impact"];

export default function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-5"
      style={{ background: "linear-gradient(to bottom, rgba(10,10,10,0.95), transparent)" }}
    >
      <span className="font-display text-xl tracking-widest text-white font-bold">
        GREEN<span style={{ color: "var(--accent)" }}>ARM</span>
      </span>

      <nav className="hidden md:flex items-center gap-8">
        {links.map((l) => (
          <a
            key={l}
            href={`#${l.toLowerCase()}`}
            className="text-xs tracking-[0.18em] uppercase text-gray-400 hover:text-white transition-colors duration-200"
          >
            {l}
          </a>
        ))}
      </nav>

      <a
        href="#solution"
        className="hidden md:inline-flex items-center gap-2 px-5 py-2 rounded-full text-xs tracking-widest uppercase font-semibold border transition-all duration-300"
        style={{
          borderColor: "var(--accent)",
          color: "var(--accent)",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLAnchorElement).style.background = "var(--accent)";
          (e.currentTarget as HTMLAnchorElement).style.color = "#0a0a0a";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
          (e.currentTarget as HTMLAnchorElement).style.color = "var(--accent)";
        }}
      >
        Explore
      </a>
    </motion.header>
  );
}
