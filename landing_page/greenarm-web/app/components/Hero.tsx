"use client";

import { motion } from "framer-motion";

function RoboticArm({ flip = false }: { flip?: boolean }) {
  return (
    <motion.svg
      viewBox="0 0 220 360"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-40 md:w-56 lg:w-64 opacity-90"
      style={{ transform: flip ? "scaleX(-1)" : undefined }}
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: flip ? 0.8 : 0 }}
    >
      {/* Base */}
      <rect x="75" y="320" width="70" height="14" rx="7" fill="#1a1a1a" stroke="rgba(74,222,128,0.4)" strokeWidth="1.5" />
      <rect x="95" y="306" width="30" height="16" rx="4" fill="#151515" stroke="rgba(74,222,128,0.3)" strokeWidth="1" />

      {/* Lower arm */}
      <rect x="103" y="220" width="14" height="90" rx="7" fill="#181818" stroke="rgba(74,222,128,0.35)" strokeWidth="1.5" />

      {/* Joint 1 */}
      <circle cx="110" cy="218" r="14" fill="#1f1f1f" stroke="rgba(74,222,128,0.5)" strokeWidth="1.5" />
      <circle cx="110" cy="218" r="6" fill="rgba(74,222,128,0.15)" stroke="rgba(74,222,128,0.6)" strokeWidth="1" />

      {/* Upper arm — angled */}
      <rect
        x="107"
        y="130"
        width="14"
        height="92"
        rx="7"
        fill="#181818"
        stroke="rgba(74,222,128,0.35)"
        strokeWidth="1.5"
        style={{ transformOrigin: "114px 218px", transform: "rotate(-18deg)" }}
      />

      {/* Joint 2 */}
      <circle cx="110" cy="128" r="14" fill="#1f1f1f" stroke="rgba(74,222,128,0.5)" strokeWidth="1.5" />
      <circle cx="110" cy="128" r="6" fill="rgba(74,222,128,0.15)" stroke="rgba(74,222,128,0.6)" strokeWidth="1" />

      {/* Forearm */}
      <rect
        x="107"
        y="50"
        width="12"
        height="82"
        rx="6"
        fill="#181818"
        stroke="rgba(74,222,128,0.35)"
        strokeWidth="1.5"
        style={{ transformOrigin: "113px 128px", transform: "rotate(22deg)" }}
      />

      {/* Wrist joint */}
      <circle cx="126" cy="56" r="10" fill="#1f1f1f" stroke="rgba(74,222,128,0.5)" strokeWidth="1.5" />

      {/* Gripper left */}
      <rect x="116" y="28" width="6" height="30" rx="3" fill="#1a1a1a" stroke="rgba(74,222,128,0.6)" strokeWidth="1.2" />
      {/* Gripper right */}
      <rect x="128" y="28" width="6" height="30" rx="3" fill="#1a1a1a" stroke="rgba(74,222,128,0.6)" strokeWidth="1.2" />

      {/* Scan line glow */}
      <motion.line
        x1="100" y1="43" x2="142" y2="43"
        stroke="rgba(74,222,128,0.6)"
        strokeWidth="1"
        strokeDasharray="4 4"
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 2, repeat: Infinity }}
      />

      {/* Circuit lines on base */}
      <line x1="75" y1="327" x2="60" y2="327" stroke="rgba(74,222,128,0.2)" strokeWidth="1" />
      <line x1="60" y1="327" x2="60" y2="310" stroke="rgba(74,222,128,0.2)" strokeWidth="1" />
      <circle cx="60" cy="310" r="2" fill="rgba(74,222,128,0.4)" />

      <line x1="145" y1="327" x2="160" y2="327" stroke="rgba(74,222,128,0.2)" strokeWidth="1" />
      <line x1="160" y1="327" x2="160" y2="310" stroke="rgba(74,222,128,0.2)" strokeWidth="1" />
      <circle cx="160" cy="310" r="2" fill="rgba(74,222,128,0.4)" />
    </motion.svg>
  );
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-6 pt-24">
      {/* Radial glow background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 45% at 50% 60%, rgba(74,222,128,0.06) 0%, transparent 70%)",
        }}
      />

      {/* Grid overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.025]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      {/* Tag line */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="flex items-center gap-2 mb-8"
      >
        <span
          className="w-2 h-2 rounded-full animate-pulse"
          style={{ background: "var(--accent)" }}
        />
        <span className="text-xs tracking-[0.22em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
          AI Robotics · Waste Automation
        </span>
      </motion.div>

      {/* Headline */}
      <motion.h1
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        className="font-display text-center text-4xl md:text-6xl lg:text-7xl font-bold leading-[1.08] tracking-tight max-w-4xl"
      >
        Autonomous Waste Sorting{" "}
        <span style={{ color: "var(--accent)" }} className="accent-glow">
          for a Cleaner Future
        </span>
      </motion.h1>

      {/* Subtext */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.38 }}
        className="mt-6 text-center text-base md:text-lg max-w-2xl leading-relaxed"
        style={{ color: "var(--text-muted)" }}
      >
        GreenArm uses AI and robotics to detect, classify, and sort waste in real-time —
        reducing contamination and eliminating manual handling.
      </motion.p>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.52 }}
        className="mt-10 flex flex-col sm:flex-row gap-4 items-center"
      >
        <motion.a
          href="#solution"
          whileHover={{ scale: 1.04, boxShadow: "0 0 32px rgba(74,222,128,0.35)" }}
          whileTap={{ scale: 0.97 }}
          className="px-8 py-3.5 rounded-full text-sm tracking-widest uppercase font-bold transition-all duration-200"
          style={{ background: "var(--accent)", color: "#0a0a0a" }}
        >
          Explore the System
        </motion.a>
        <a
          href="#problem"
          className="text-sm tracking-widest uppercase font-medium underline underline-offset-4 transition-colors"
          style={{ color: "var(--text-muted)" }}
        >
          Learn the Problem
        </a>
      </motion.div>

      {/* Robotic arms */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 0.6 }}
        className="mt-16 flex items-end justify-center gap-12 md:gap-24 relative"
      >
        <RoboticArm />
        <RoboticArm flip />

        {/* Center glow dot */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full"
          style={{ background: "var(--accent)" }}
          animate={{ opacity: [0.4, 1, 0.4], scale: [0.9, 1.2, 0.9] }}
          transition={{ duration: 2.5, repeat: Infinity }}
        />
      </motion.div>

      {/* Scroll hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <motion.div
          className="w-px h-10"
          style={{ background: "linear-gradient(to bottom, rgba(74,222,128,0.6), transparent)" }}
          animate={{ scaleY: [0.5, 1, 0.5], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <span className="text-[10px] tracking-[0.2em] uppercase" style={{ color: "var(--text-muted)" }}>
          Scroll
        </span>
      </motion.div>
    </section>
  );
}
