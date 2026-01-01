"use client"

import { useRef } from "react"
import { motion, useScroll, useTransform } from "framer-motion"
import { Shield, Eye, Lock, Zap, Activity, ArrowRight, Fingerprint, Scan, Globe } from "lucide-react"
import Link from "next/link"
import { Navbar } from "@/components/navbar"
import PixelBlast from "@/components/pixel-blast"

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  })

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"])

  return (
    <main className="min-h-screen bg-background text-foreground overflow-hidden selection:bg-primary/30">
      <Navbar />

      {/* Background Elements */}
      <div className="fixed inset-0 z-0">
        <PixelBlast
          variant="circle"
          pixelSize={5}
          color="#B19EEF"
          patternScale={3}
          patternDensity={1.5}
          pixelSizeJitter={0.8}
          enableRipples
          rippleSpeed={0.3}
          rippleThickness={0.12}
          rippleIntensityScale={1.2}
          liquid
          liquidStrength={0.15}
          liquidRadius={1.5}
          liquidWobbleSpeed={4}
          speed={0.5}
          edgeFade={0.2}
          transparent
        />
        <div className="absolute inset-0 bg-background/85 backdrop-blur-[1px]" />
      </div>

      <div ref={containerRef} className="relative z-10">

        {/* Hero Section */}
        <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="text-center max-w-4xl mx-auto space-y-8"
          >
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 border border-white/10 backdrop-blur-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-sm font-medium text-muted-foreground">System Operational</span>
            </motion.div>

            <motion.h1 variants={fadeInUp} className="text-6xl md:text-8xl font-bold tracking-tight">
              Protect Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-400 to-blue-500">
                Digital Reality
              </span>
            </motion.h1>

            <motion.p variants={fadeInUp} className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Advanced AI-powered deepfake detection and media protection.
              Secure your identity in the age of synthetic media.
            </motion.p>

            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/detect" className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-primary px-8 font-medium text-white transition-all duration-300 hover:bg-primary/90 hover:scale-105 hover:shadow-[0_0_40px_-10px_rgba(124,58,237,0.5)]">
                <span className="mr-2">Start Detection</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link href="/protect" className="group inline-flex h-12 items-center justify-center rounded-md border border-input bg-background/50 px-8 font-medium transition-colors hover:bg-accent hover:text-accent-foreground backdrop-blur-sm">
                Protect Media
              </Link>
            </motion.div>
          </motion.div>

          {/* Abstract 3D-like Element (CSS only) */}
          <motion.div
            style={{ y }}
            className="absolute bottom-0 left-0 right-0 h-[40vh] opacity-30 pointer-events-none"
          >
            <div className="w-full h-full bg-gradient-to-t from-background to-transparent" />
          </motion.div>
        </section>

        {/* Bento Grid Features */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-16 text-center"
            >
              <h2 className="text-3xl md:text-5xl font-bold mb-6">Modular Defense System</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Our architecture is built on independent, high-performance modules designed to detect, analyze, and neutralize synthetic media threats.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">

              {/* Large Card */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="md:col-span-2 row-span-1 md:row-span-2 rounded-3xl p-8 bg-card/30 border border-white/5 backdrop-blur-md overflow-hidden relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10 h-full flex flex-col justify-between">
                  <div>
                    <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center mb-6 text-primary">
                      <Scan className="w-6 h-6" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Deepfake Detection Engine</h3>
                    <p className="text-muted-foreground">
                      State-of-the-art transformer models analyzing frame-by-frame anomalies to detect synthetic manipulation with 99.9% accuracy.
                    </p>
                  </div>
                  <div className="w-full h-32 bg-gradient-to-r from-primary/20 to-blue-500/20 rounded-xl mt-6 border border-white/5 flex items-center justify-center overflow-hidden">
                    {/* Abstract visualization */}
                    <div className="flex gap-1 items-end h-16">
                      {[40, 70, 30, 85, 50, 90, 60].map((h, i) => (
                        <motion.div
                          key={i}
                          initial={{ height: 10 }}
                          whileInView={{ height: h + '%' }}
                          transition={{ duration: 1, delay: i * 0.1, repeat: Infinity, repeatType: "reverse" }}
                          className="w-3 bg-primary/60 rounded-t-sm"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Small Card 1 */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="rounded-3xl p-8 bg-card/30 border border-white/5 backdrop-blur-md relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-6 text-blue-500">
                  <Shield className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-2">Audio Shield</h3>
                <p className="text-sm text-muted-foreground">
                  Invisible watermarking and spectral analysis to protect voice authenticity.
                </p>
              </motion.div>

              {/* Small Card 2 */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="rounded-3xl p-8 bg-card/30 border border-white/5 backdrop-blur-md relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="w-12 h-12 rounded-2xl bg-green-500/20 flex items-center justify-center mb-6 text-green-500">
                  <Fingerprint className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-2">Identity Guard</h3>
                <p className="text-sm text-muted-foreground">
                  Proactive protection against unauthorized likeness usage in AI models.
                </p>
              </motion.div>

              {/* Wide Card */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="md:col-span-3 rounded-3xl p-8 bg-card/30 border border-white/5 backdrop-blur-md relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-transparent to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="flex-1">
                    <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center mb-6 text-purple-500">
                      <Globe className="w-6 h-6" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Global Threat Intelligence</h3>
                    <p className="text-muted-foreground">
                      Real-time updates on emerging deepfake generation techniques and adversarial patterns.
                    </p>
                  </div>
                  <div className="flex-1 w-full">
                    <div className="grid grid-cols-3 gap-4">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-24 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center">
                          <Activity className="w-6 h-6 text-muted-foreground/50" />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>

            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 border-t border-white/10 bg-black/20 backdrop-blur-lg">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">A</div>
              <span className="font-bold text-xl">AntiBanana</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 AntiBanana Defense Systems. All rights reserved.
            </p>
            <div className="flex gap-6">
              <Link href="#" className="text-muted-foreground hover:text-primary transition-colors">Privacy</Link>
              <Link href="#" className="text-muted-foreground hover:text-primary transition-colors">Terms</Link>
              <Link href="#" className="text-muted-foreground hover:text-primary transition-colors">Contact</Link>
            </div>
          </div>
        </footer>

      </div>
    </main>
  )
}
