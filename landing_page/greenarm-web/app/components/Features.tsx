"use client";

import { motion } from "framer-motion";
import FadeIn from "./FadeIn";

const features = [
  {
    title: "AI Vision Detection",
    description:
      "YOLOv8 processes overhead camera frames in real-time, identifying waste type, position, and orientation with high accuracy.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
  {
    title: "Robotic Precision",
    description:
      "The Kinova Gen3 arm executes sub-millimeter pick-and-place operations guided by ArUco marker calibration data.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z" />
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
  {
    title: "Real-Time Sorting",
    description:
      "End-to-end latency from detection to arm placement is minimal, enabling continuous, uninterrupted sorting cycles.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
  },
  {
    title: "Hygienic Automation",
    description:
      "Zero human contact with waste. Closed-loop automation eliminates exposure to biohazardous materials entirely.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
      </svg>
    ),
  },
];

export default function Features() {
  return (
    <section id="features" className="py-32 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(ellipse 70% 50% at 50% 50%, rgba(74,222,128,0.03) 0%, transparent 70%)" }}
      />

      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              Capabilities
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-xl">
            Built for the hardest environments.
          </h2>
        </FadeIn>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 gap-6">
          {features.map((f, i) => (
            <FadeIn key={f.title} delay={i * 0.1}>
              <motion.div
                whileHover={{
                  scale: 1.02,
                  boxShadow: "0 0 30px rgba(74,222,128,0.1), 0 0 1px rgba(74,222,128,0.3)",
                }}
                transition={{ type: "spring", stiffness: 200 }}
                className="group relative flex flex-col gap-5 p-8 rounded-2xl border card-hover cursor-default overflow-hidden"
                style={{ background: "var(--surface)", borderColor: "var(--border)" }}
              >
                {/* Hover glow */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{ background: "radial-gradient(ellipse 80% 60% at 20% 20%, rgba(74,222,128,0.06), transparent)" }}
                />

                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center border"
                  style={{ borderColor: "rgba(74,222,128,0.3)", background: "rgba(74,222,128,0.08)", color: "var(--accent)" }}
                >
                  {f.icon}
                </div>

                <div>
                  <h3 className="font-display text-xl font-bold text-white mb-2">{f.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                    {f.description}
                  </p>
                </div>

                {/* Bottom accent line */}
                <motion.div
                  className="absolute bottom-0 left-0 h-px"
                  style={{ background: "var(--accent)" }}
                  initial={{ width: 0 }}
                  whileHover={{ width: "100%" }}
                  transition={{ duration: 0.4 }}
                />
              </motion.div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
