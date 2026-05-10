"use client";

import FadeIn from "./FadeIn";

const mlPipeline = [
  "Model: Ultralytics YOLO loaded from greenarm_perception/models/model_v9.pt.",
  "Inference runs per frame with configurable confidence threshold (default 0.5).",
  "Active classes are restricted to [0, 2], then the highest-confidence detection is selected.",
  "Bounding-box center is computed as ((x1 + x2) / 2, (y1 + y2) / 2) for target localization.",
  "Class-to-label mapping in the node: 0 → compost, 2 → recycle.",
];

const mathAndGeometry = [
  "ArUco-based homography calibration uses cv2.getPerspectiveTransform with four ordered marker points.",
  "Image-to-workspace transform is applied with cv2.perspectiveTransform to convert pixel centers into metric workspace coordinates.",
  "Marker pixel size estimate uses the mean of 4 side lengths via Euclidean norm.",
  "Workspace bounds enforce valid manipulation targets: x ∈ [0.2, 0.5], y ∈ [-0.3, 0.0] (meters).",
  "Legacy color pipeline applies HSV thresholding, morphology (open/close), contour area filtering, and normalized area confidence.",
];

const controlAndRobotics = [
  "Perception publishes SourceTarget {x, y, z, confidence, label} to /source_zone/pick_target.",
  "Pick-place control uses a state machine: approach → descend → grasp → lift → move → drop → home.",
  "Target stabilization averages recent samples and accepts only low-deviation points (threshold 0.01 m).",
  "Drop poses are sampled uniformly inside class-specific destination zone bounds.",
  "Tool orientation is fixed for Cartesian moves at (theta_x, theta_y, theta_z) = (180, 0, 180).",
];

export default function TechnicalDocumentation() {
  return (
    <section id="docs" className="py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <FadeIn>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-px" style={{ background: "var(--accent)" }} />
            <span className="text-xs tracking-[0.2em] uppercase font-semibold" style={{ color: "var(--accent)" }}>
              Technical Documentation
            </span>
          </div>
          <h2 className="font-display text-3xl md:text-5xl font-bold leading-tight max-w-3xl">
            ML, math, and robotics architecture from the Python implementation.
          </h2>
          <p className="mt-4 text-base max-w-3xl" style={{ color: "var(--text-muted)" }}>
            This section is sourced from the ROS2 Python stack in this repository (greenarm_perception, greenarm_manipulation,
            and kinova_gen3), not from placeholder web copy.
          </p>
        </FadeIn>

        <div className="mt-16 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[
            { title: "ML Pipeline (YOLO)", items: mlPipeline },
            { title: "Math & Calibration", items: mathAndGeometry },
            { title: "Control & Interfaces", items: controlAndRobotics },
          ].map((section, sectionIndex) => (
            <FadeIn key={section.title} delay={sectionIndex * 0.1}>
              <div
                className="h-full rounded-2xl border p-7"
                style={{ background: "var(--surface)", borderColor: "var(--border)" }}
              >
                <h3 className="font-display text-xl font-bold text-white mb-4">{section.title}</h3>
                <ul className="space-y-3">
                  {section.items.map((item) => (
                    <li key={item} className="text-sm leading-relaxed flex items-start gap-3" style={{ color: "var(--text-muted)" }}>
                      <span className="mt-2 w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: "var(--accent)" }} />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
