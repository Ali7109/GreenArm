"use client";

import { motion } from "framer-motion";

const team = [
  "Khawaja Faiza Qaisar",
  "Omkumar Miteshbhai Patel",
  "Thi Thanh Thuy Nguyen",
  "Michael Murphy",
  "Ali Hassan Amin",
];

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="py-16 px-6 border-t"
      style={{ borderColor: "var(--border)" }}
    >
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-10">
        {/* Brand */}
        <div className="flex flex-col gap-3">
          <span className="font-display text-2xl font-bold tracking-widest">
            GREEN<span style={{ color: "var(--accent)" }}>ARM</span>
          </span>
          <p
            className="text-xs max-w-xs leading-relaxed"
            style={{ color: "var(--text-muted)" }}
          >
            Autonomous waste sorting powered by AI and robotics. EECS 4421 / EECS 5324.
          </p>
          <div className="flex items-center gap-2 mt-1">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: "var(--accent)" }}
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 2.5, repeat: Infinity }}
            />
            <span
              className="text-[10px] tracking-widest uppercase"
              style={{ color: "var(--accent)" }}
            >
              Course Research Project
            </span>
          </div>
        </div>

        {/* Team */}
        <div className="flex flex-col gap-3">
          <span
            className="text-[10px] tracking-[0.2em] uppercase font-semibold mb-1"
            style={{ color: "var(--text-muted)" }}
          >
            Team
          </span>
          {team.map((name) => (
            <span key={name} className="text-xs text-white font-medium">
              {name}
            </span>
          ))}
        </div>

        {/* Links */}
        <div className="flex flex-col gap-3">
          <span
            className="text-[10px] tracking-[0.2em] uppercase font-semibold mb-1"
            style={{ color: "var(--text-muted)" }}
          >
            Resources
          </span>
          <a
            href="https://github.com/Ali7109/GreenArm"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs transition-colors duration-200 hover:text-white"
            style={{ color: "var(--text-muted)" }}
          >
            GitHub Repository ↗
          </a>
        </div>
      </div>

      <div
        className="max-w-6xl mx-auto mt-12 pt-6 border-t flex items-center justify-between"
        style={{ borderColor: "var(--border)" }}
      >
        <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
          © {currentYear} GreenArm. York University — EECS 4421 / 5324.
        </span>
        <span
          className="text-[11px] font-display"
          style={{ color: "var(--accent)" }}
        >
          Built with precision.
        </span>
      </div>
    </footer>
  );
}