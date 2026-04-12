"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import FadeIn from "./FadeIn";

const impacts = [
  {
    metric: "—",
    label: "Reduced Contamination",
    description: "Precision sorting prevents cross-contamination between waste streams.",
  },
  {
    metric: "—",
    label: "Safer Conditions",
    description: "Workers are never exposed to hygienic waste or sharp objects.",
  },
  {
    metric: "—",
    label: "Lower Maintenance",
    description: "Proper disposal prevents plumbing failures and costly interventions.",
  },
  {
    metric: "—",
    label: "Scalable Automation",
    description: "Deploys across any facility size with minimal convenient configuration.",
  },
];

function AnimatedBar({ delay }: { delay: number }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <div ref={ref} className="h-1 rounded-full overflow-hidden" style={{ background: "var(--surface-2)" }}>
      <motion.div
        className="h-full rounded-full"
        style={{ background: "var(--accent)" }}
        initial={{ width: 0 }}
        animate={isInView ? { width: `${60 + delay * 15}%` } : {}}
        transition={{ duration: 1, delay: delay * 0.15 + 0.3, ease: [0.22, 1, 0.36, 1] }}
      />
    </div>
  );
}

export default function Impact() {
  return (
    <section id="impact" className="py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              Impact
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-2xl">
            Measurable outcomes. Real-world value.
          </h2>
          <p className="mt-4 text-base max-w-lg" style={{ color: "var(--text-muted)" }}>
            GreenArm directly addresses the most costly and dangerous aspects of waste management.
          </p>
        </FadeIn>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
          {impacts.map((item, i) => (
            <FadeIn key={item.label} delay={i * 0.1}>
              <div
                className="p-8 rounded-2xl border flex flex-col gap-5"
                style={{ background: "var(--surface)", borderColor: "var(--border)" }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-display text-lg font-bold text-white">{item.label}</h3>
                    <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                      {item.description}
                    </p>
                  </div>
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: "rgba(74,222,128,0.1)" }}
                  >
                    <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4" stroke="rgba(74,222,128,1)" strokeWidth="2">
                      <path d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  </div>
                </div>
                <AnimatedBar delay={i} />
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
