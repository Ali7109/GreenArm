"use client";

import { motion } from "framer-motion";
import FadeIn from "./FadeIn";

const items = [
  {
    title: "Expanded Object Classes",
    description: "Train on a broader dataset to recognise more waste types — plastics, metals, glass.",
  },
  {
    title: "Orientation-Aware Pickup",
    description: "Smarter gripper planning that adapts to irregular shapes and awkward orientations.",
  },
  {
    title: "Multi-Object Scheduling",
    description: "Queue and prioritise multiple items for concurrent or sequential arm operations.",
  },
  {
    title: "Improved Model Accuracy",
    description: "Continual learning pipeline fed by real-world deployment data for iterative improvement.",
  },
];

export default function FutureWork() {
  return (
    <section id="future" className="py-32 px-6 relative overflow-hidden">
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] pointer-events-none"
        style={{ background: "radial-gradient(ellipse at center, rgba(74,222,128,0.05) 0%, transparent 70%)" }}
      />

      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              What&apos;s Next
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-xl">
            The roadmap ahead.
          </h2>
          <p className="mt-4 text-base max-w-lg" style={{ color: "var(--text-muted)" }}>
            GreenArm is a foundation. The next iterations will push capability, accuracy, and autonomy further.
          </p>
        </FadeIn>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 gap-6">
          {items.map((item, i) => (
            <FadeIn key={item.title} delay={i * 0.1}>
              <motion.div
                whileHover={{ x: 4 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="flex items-start gap-5 p-6 rounded-xl border"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                <div
                  className="mt-1 w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-xs"
                  style={{ background: "rgba(74,222,128,0.12)", color: "var(--accent)" }}
                >
                  {i + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm mb-1">{item.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                    {item.description}
                  </p>
                </div>
              </motion.div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
