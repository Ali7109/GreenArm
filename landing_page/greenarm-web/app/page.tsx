import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Problem from "./components/Problem";
import Solution from "./components/Solution";
import SystemDesign from "./components/SystemDesign";
import Features from "./components/Features";
import Impact from "./components/Impact";
import FutureWork from "./components/FutureWork";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <main>
      <Navbar />
      <Hero />
      <Problem />
      <Solution />
      <SystemDesign />
      <Features />
      <Impact />
      <FutureWork />
      <Footer />
    </main>
  );
}
