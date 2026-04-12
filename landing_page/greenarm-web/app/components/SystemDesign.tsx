"use client";

import { motion } from "framer-motion";
import FadeIn from "./FadeIn";

export default function SystemDesign() {
  return (
    <section id="system" className="py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              System Design
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-2xl">
            Blueprint of an autonomous sorting cell.
          </h2>
          <p className="mt-4 text-base max-w-lg" style={{ color: "var(--text-muted)" }}>
            Two defined zones. One intelligent system. Precise, repeatable, scalable.
          </p>
        </FadeIn>

        {/* Blueprint diagram */}
        <FadeIn delay={0.15} className="mt-16">
          <div
            className="rounded-3xl border p-8 md:p-12 relative overflow-hidden"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            {/* Blueprint grid */}
            <div
              className="absolute inset-0 opacity-[0.04]"
              style={{
                backgroundImage:
                  "linear-gradient(rgba(74,222,128,1) 1px, transparent 1px), linear-gradient(90deg, rgba(74,222,128,1) 1px, transparent 1px)",
                backgroundSize: "32px 32px",
              }}
            />

            <div className="relative flex flex-col lg:flex-row items-stretch gap-6">
              {/* Source zone */}
              <motion.div
                whileHover={{ borderColor: "rgba(74,222,128,0.5)" }}
                transition={{ duration: 0.3 }}
                className="flex-1 rounded-2xl border p-8 flex flex-col gap-6"
                style={{ borderColor: "rgba(74,222,128,0.2)", background: "var(--surface-2)" }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
                    Zone A — Source
                  </span>
                  <span className="text-xs px-2 py-1 rounded" style={{ background: "rgba(74,222,128,0.1)", color: "var(--accent)" }}>
                    Input
                  </span>
                </div>

                <div className="flex flex-col gap-4">
                  {[
                    { label: "Overhead Camera", desc: "360° waste detection field" },
                    { label: "ArUco Markers", desc: "Spatial calibration anchors" },
                    { label: "Waste Intake Area", desc: "Unstructured item placement" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-start gap-3">
                      <div
                        className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ background: "var(--accent)" }}
                      />
                      <div>
                        <p className="text-sm font-semibold text-white">{item.label}</p>
                        <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                          {item.desc}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Center — Kinova arm */}
              <div className="flex flex-col items-center justify-center gap-4 px-4 lg:px-8">
                <motion.div
                  animate={{ rotate: [0, 2, -2, 0] }}
                  transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                  className="w-16 h-16 rounded-2xl border flex items-center justify-center"
                  style={{ borderColor: "var(--accent)", background: "rgba(74,222,128,0.08)" }}
                >
                  <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="rgba(74,222,128,1)" strokeWidth="1.5">
                    <path d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
                  </svg>
                </motion.div>
                <div className="text-center">
                  <p className="text-xs font-bold tracking-widest text-white uppercase">Kinova</p>
                  <p className="text-xs" style={{ color: "var(--text-muted)" }}>Gen3 Arm</p>
                </div>
                {/* Arrow */}
                <div className="flex lg:flex-col items-center gap-1">
                  <motion.div
                    className="w-px h-8 lg:w-8 lg:h-px"
                    style={{ background: "linear-gradient(to bottom, var(--accent), transparent)" }}
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
              </div>

              {/* Destination zone */}
              <motion.div
                whileHover={{ borderColor: "rgba(74,222,128,0.5)" }}
                transition={{ duration: 0.3 }}
                className="flex-1 rounded-2xl border p-8 flex flex-col gap-6"
                style={{ borderColor: "rgba(74,222,128,0.2)", background: "var(--surface-2)" }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
                    Zone B — Destination
                  </span>
                  <span className="text-xs px-2 py-1 rounded" style={{ background: "rgba(74,222,128,0.1)", color: "var(--accent)" }}>
                    Output
                  </span>
                </div>

                <div className="flex flex-col gap-4">
                  {[
                    { label: "Recycle Bin", desc: "Paper, cardboard items" },
                    { label: "Compost Bin", desc: "Organic, tissue waste" },
                    { label: "Labelled Zones", desc: "ArUco marker-guided placement" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-start gap-3">
                      <div
                        className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ background: "var(--accent)" }}
                      />
                      <div>
                        <p className="text-sm font-semibold text-white">{item.label}</p>
                        <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                          {item.desc}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Tech specs bar */}
            <div
              className="mt-8 pt-8 border-t flex flex-wrap gap-6"
              style={{ borderColor: "var(--border)" }}
            >
              {[
                { label: "Vision Model", value: "YOLOv8" },
                { label: "Arm", value: "Kinova Gen3" },
                { label: "Framework", value: "ROS 2" },
                { label: "Calibration", value: "ArUco Markers" },
                { label: "Language", value: "Python" },
              ].map((spec) => (
                <div key={spec.label} className="flex flex-col gap-0.5">
                  <span className="text-[10px] tracking-[0.18em] uppercase" style={{ color: "var(--text-muted)" }}>
                    {spec.label}
                  </span>
                  <span className="text-sm font-bold tracking-wide text-white">{spec.value}</span>
                </div>
              ))}
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
