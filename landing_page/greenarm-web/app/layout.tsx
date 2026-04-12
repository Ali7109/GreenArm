import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GreenArm — Autonomous Waste Sorting",
  description:
    "GreenArm uses AI and robotics to detect, classify, and sort waste in real-time — reducing contamination and eliminating manual handling.",
  keywords: ["robotics", "AI", "waste sorting", "automation", "GreenArm"],
  openGraph: {
    title: "GreenArm — Autonomous Waste Sorting",
    description:
      "An intelligent robotic system that automates waste sorting using computer vision and a robotic arm.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400..700;1,400..700&family=Saira+Stencil:ital,wght@0,100..900;1,100..900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
