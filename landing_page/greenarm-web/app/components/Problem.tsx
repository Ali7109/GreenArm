"use client";

import FadeIn from "./FadeIn";

const problems = [
  {
    stat: "60%",
    label: "of washroom waste",
    description: "is incorrectly disposed, causing recycling contamination.",
  },
  {
    stat: "3×",
    label: "higher maintenance",
    description: "Manual sorting of hygienic waste poses serious health hazards.",
  },
  {
    stat: "∞",
    label: "plumbing failures",
    description: "Tissues and products flushed down drains clog entire systems.",
  },
];

export default function Problem() {
  return (
    <section id="problem" className="py-32 px-6 relative">
      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              The Problem
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-2xl">
            Waste mismanagement is a{" "}
            <span className="line-through opacity-40">small</span>{" "}
            <span style={{ color: "var(--accent)" }}>systemic</span> issue.
          </h2>
        </FadeIn>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-px" style={{ background: "var(--border)" }}>
          {problems.map((p, i) => (
            <FadeIn key={p.stat} delay={i * 0.12}>
              <div
                className="p-10 flex flex-col gap-4"
                style={{ background: "var(--bg)" }}
              >
                <span
                  className="font-display text-5xl md:text-6xl font-bold"
                  style={{ color: "var(--accent)" }}
                >
                  {p.stat}
                </span>
                <span className="text-sm font-semibold tracking-wide text-white uppercase">
                  {p.label}
                </span>
                <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {p.description}
                </p>
              </div>
            </FadeIn>
          ))}
        </div>

        <FadeIn delay={0.4} className="mt-16 max-w-3xl">
          <p className="text-lg md:text-xl leading-relaxed font-light" style={{ color: "var(--text-muted)" }}>
            Public and commercial washrooms generate enormous volumes of non-recyclable waste
            daily. Without intelligent sorting, contamination spreads through the entire stream —
            inflating costs, endangering workers, and failing our environment.
          </p>
        </FadeIn>
      </div>
    </section>
  );
}
