"use client";

import { motion } from "framer-motion";
import FadeIn from "./FadeIn";

const steps = [
  {
    number: "01",
    label: "Detect",
    description: "Overhead camera captures waste items using real-time computer vision.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="3" />
        <path d="M3 9V6a2 2 0 012-2h3M3 15v3a2 2 0 002 2h3M15 3h3a2 2 0 012 2v3M15 21h3a2 2 0 002-2v-3" />
      </svg>
    ),
  },
  {
    number: "02",
    label: "Classify",
    description: "YOLOv8 model identifies each object and assigns a category.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="1.5">
        <path d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1 1 .3 2.7-1.1 2.7H3.9c-1.4 0-2.1-1.7-1.1-2.7L4.2 15.3" />
      </svg>
    ),
  },
  {
    number: "03",
    label: "Pick",
    description: "The Kinova robotic arm localises and grips the waste item precisely.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="1.5">
        <path d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
      </svg>
    ),
  },
  {
    number: "04",
    label: "Sort",
    description: "Item is deposited into the correct bin — Recycle or Compost.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="1.5">
        <path d="M3 7.5L7.5 3m0 0L12 7.5M7.5 3v13.5m13.5 0L16.5 21m0 0L12 16.5m4.5 4.5V7.5" />
      </svg>
    ),
  },
];

export default function Solution() {
  return (
    <section id="solution" className="py-32 px-6 relative overflow-hidden">
      {/* subtle bg strip */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(ellipse 80% 40% at 50% 50%, rgba(74,222,128,0.03) 0%, transparent 70%)" }}
      />

      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              The Solution
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-xl">
            Four steps. Fully automated.
          </h2>
          <p className="mt-4 text-base max-w-lg" style={{ color: "var(--text-muted)" }}>
            GreenArm orchestrates a seamless pipeline from detection to disposal — no human intervention required.
          </p>
        </FadeIn>

        {/* Steps */}
        <div className="mt-20 relative">
          {/* Connector line */}
          <div
            className="absolute top-10 left-0 right-0 h-px hidden lg:block"
            style={{ background: "linear-gradient(to right, transparent, rgba(74,222,128,0.3), transparent)" }}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 sm:auto-rows-fr">
            {steps.map((step, i) => (
              <FadeIn key={step.number} delay={i * 0.1}>
                <motion.div
                  whileHover={{ y: -4 }}
                  transition={{ type: "spring", stiffness: 300 }}
                  className="relative h-full flex flex-col gap-5 p-8 rounded-2xl border card-hover cursor-default"
                  style={{ background: "var(--surface)", borderColor: "var(--border)" }}
                >
                  {/* Number badge */}
                  <span
                    className="absolute -top-3.5 left-6 text-[10px] tracking-widest px-3 py-0.5 rounded-full font-bold"
                    style={{ background: "var(--accent)", color: "#0a0a0a" }}
                  >
                    {step.number}
                  </span>

                  <div style={{ color: "var(--accent)" }}>{step.icon}</div>

                  <div>
                    <h3 className="font-display text-xl font-bold text-white mb-2">{step.label}</h3>
                    <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                      {step.description}
                    </p>
                  </div>
                </motion.div>
              </FadeIn>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
