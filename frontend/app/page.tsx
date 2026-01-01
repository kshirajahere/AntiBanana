"use client"

import { useRef } from "react"
import { motion, useScroll, useTransform } from "framer-motion"
import { Shield, Eye, Lock, Zap, Activity, ArrowRight, Fingerprint, Scan, Globe, CheckCircle } from "lucide-react"
import Link from "next/link"
import { Navbar } from "@/components/navbar"
import PixelBlast from "@/components/pixel-blast"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

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
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 border border-white/10 backdrop-blur-sm shadow-[0_0_20px_rgba(124,58,237,0.1)]">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-sm font-medium text-muted-foreground uppercase tracking-widest">Global Defense Active</span>
            </motion.div>

            <motion.h1 variants={fadeInUp} className="text-6xl md:text-9xl font-bold tracking-tight">
              Protect Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-400 to-blue-500 animate-gradient-x">
                Digital Identity
              </span>
            </motion.h1>

            <motion.p variants={fadeInUp} className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              AntiBanana utilizes dual-layer forensic analysis and higher-order statistics to shield your media from unauthorized AI manipulation and deepfake generation.
            </motion.p>

            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-4">
              <Link href="/detect" className="group relative inline-flex h-14 items-center justify-center overflow-hidden rounded-full bg-primary px-10 font-bold text-white transition-all duration-300 hover:scale-105 hover:shadow-[0_0_50px_-10px_rgba(124,58,237,0.6)]">
                <span className="relative z-10 flex items-center">
                  Live Detection
                  <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              </Link>
              <Link href="/protect" className="group inline-flex h-14 items-center justify-center rounded-full border-2 border-primary/30 bg-background/50 px-10 font-bold transition-all hover:bg-primary/10 hover:border-primary/60 backdrop-blur-sm">
                Shield Media
              </Link>
            </motion.div>
          </motion.div>

          {/* Abstract Ground Plane */}
          <div className="absolute bottom-0 left-0 right-0 h-[30vh] pointer-events-none overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-10" />
            <div className="w-full h-full opacity-20"
              style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, rgba(124,58,237,0.3) 1px, transparent 0)`,
                backgroundSize: '40px 40px',
                transform: 'perspective(500px) rotateX(60deg) translateY(0%)',
              }}
            />
          </div>
        </section>

        {/* Security Pulse Section */}
        <section className="py-24 px-6 relative overflow-hidden">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { label: "Threats Blocked", value: "2.4M+", icon: <Zap className="w-5 h-5" />, color: "text-amber-400" },
              { label: "Scan Accuracy", value: "99.98%", icon: <Activity className="w-5 h-5" />, color: "text-green-400" },
              { label: "Media Protected", value: "850K+", icon: <Lock className="w-5 h-5" />, color: "text-blue-400" },
              { label: "System Latency", value: "12ms", icon: <Globe className="w-5 h-5" />, color: "text-purple-400" },
            ].map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-8 rounded-3xl bg-card/20 border border-white/5 backdrop-blur-sm flex flex-col items-center text-center group hover:border-primary/20 transition-colors"
              >
                <div className={cn("mb-4 p-3 rounded-2xl bg-white/5 group-hover:scale-110 transition-transform", stat.color)}>
                  {stat.icon}
                </div>
                <div className="text-4xl font-bold mb-1 font-space tracking-tight">{stat.value}</div>
                <div className="text-sm text-muted-foreground font-medium uppercase tracking-wider">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Real vs Fake Visualizer */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row items-center gap-16">
              <div className="flex-1 space-y-6">
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                >
                  <Badge variant="outline" className="mb-4 py-1 px-4 border-primary/30 text-primary">Forensic Analysis</Badge>
                  <h2 className="text-4xl md:text-6xl font-bold leading-tight">
                    See Beyond the <br />
                    <span className="text-muted-foreground">Synthetic Mask</span>
                  </h2>
                  <p className="text-lg text-muted-foreground max-w-lg mt-6">
                    Our DRN (DenoiseResponseNet) technology decomposes media into noise residuals, exposing the subtle artifacts left behind by generative AI that are invisible to the human eye.
                  </p>
                  <div className="flex gap-4 mt-8">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-primary" />
                      <span className="text-sm font-medium">Dual-Domain FD-Net</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-primary" />
                      <span className="text-sm font-medium">Dynamics-Aware SSM</span>
                    </div>
                  </div>
                </motion.div>
              </div>

              <div className="flex-1 w-full relative">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  className="aspect-square md:aspect-video rounded-3xl bg-card border border-white/10 overflow-hidden relative group shadow-2xl shadow-primary/10"
                >
                  <div className="absolute inset-0 bg-[url('/ai-face.png')] bg-cover bg-center" />

                  {/* Scanner overlay */}
                  <motion.div
                    animate={{ left: ["0%", "100%", "0%"] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute top-0 bottom-0 w-1 bg-primary/80 z-20 shadow-[0_0_20px_rgba(124,58,237,1)]"
                  />

                  {/* Analysis annotations */}
                  <div className="absolute top-10 right-10 z-20 space-y-2">
                    <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-md border border-red-500/50 flex items-center gap-2 animate-pulse">
                      <div className="w-2 h-2 rounded-full bg-red-500" />
                      <span className="text-[10px] font-mono font-bold text-red-500">SYNTHETIC ARTIFACT DETECTED</span>
                    </div>
                    <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-md border border-white/20 flex items-center gap-2">
                      <span className="text-[10px] font-mono text-white/70">CONFIDENCE: 99.82%</span>
                    </div>
                  </div>

                  {/* Fake mask overlay */}
                  <div className="absolute inset-0 bg-blue-500/10 pointer-events-none mix-blend-overlay" />
                </motion.div>
              </div>
            </div>
          </div>
        </section>

        {/* Bento Grid Features */}
        <section className="py-32 px-6 bg-black/40">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-20 text-center"
            >
              <h2 className="text-4xl md:text-6xl font-bold mb-6">Modular Defense Architecture</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
                Independent, high-performance engines optimized for specific vector threats in the synthetic media landscape.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 auto-rows-[340px]">

              {/* Large Card */}
              <motion.div
                whileHover={{ y: -10 }}
                className="md:col-span-2 row-span-1 md:row-span-2 rounded-[2.5rem] p-12 bg-card/40 border border-white/5 backdrop-blur-xl overflow-hidden relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="relative z-10 h-full flex flex-col justify-between">
                  <div className="max-w-md">
                    <div className="w-16 h-16 rounded-3xl bg-primary/20 flex items-center justify-center mb-8 text-primary group-hover:scale-110 transition-transform shadow-[0_0_30px_rgba(124,58,237,0.2)]">
                      <Scan className="w-8 h-8" />
                    </div>
                    <h3 className="text-3xl font-bold mb-4">DRN Detection Core</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Advanced neural architectures analyzing frame-by-frame noise residuals and higher-order statistics to expose GAN and Diffusion-based manipulations.
                    </p>
                  </div>
                  <div className="w-full h-40 bg-black/40 rounded-3xl mt-12 border border-white/5 flex items-center justify-center overflow-hidden relative">
                    <div className="absolute inset-0 bg-gradient-to-t from-primary/5 to-transparent" />
                    <div className="flex gap-2 items-end h-24">
                      {[40, 70, 30, 85, 50, 90, 60, 40, 75, 55].map((h, i) => (
                        <motion.div
                          key={i}
                          initial={{ height: "20%" }}
                          animate={{ height: [h + "%", (h - 20) + "%", h + "%"] }}
                          transition={{ duration: 1.5 + (i * 0.1), repeat: Infinity, ease: "easeInOut" }}
                          className="w-4 bg-primary/40 rounded-full"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Small Card 1 */}
              <motion.div
                whileHover={{ y: -10 }}
                className="rounded-[2.5rem] p-10 bg-card/40 border border-white/5 backdrop-blur-xl relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-6 text-blue-500 group-hover:rotate-12 transition-transform shadow-[0_0_30px_rgba(59,130,246,0.2)]">
                  <Shield className="w-7 h-7" />
                </div>
                <h3 className="text-2xl font-bold mb-3">Audio Sanctuary</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Spectral watermarking and biometric analysis to safeguard vocal profiles against advanced cloning.
                </p>
              </motion.div>

              {/* Small Card 2 */}
              <motion.div
                whileHover={{ y: -10 }}
                className="rounded-[2.5rem] p-10 bg-card/40 border border-white/5 backdrop-blur-xl relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="w-14 h-14 rounded-2xl bg-green-500/20 flex items-center justify-center mb-6 text-green-500 group-hover:scale-110 transition-transform shadow-[0_0_30px_rgba(34,197,94,0.2)]">
                  <Fingerprint className="w-7 h-7" />
                </div>
                <h3 className="text-2xl font-bold mb-3">Biometric Vault</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Decentralized identity protection preventing the unauthorized ingestion of your likeness into training datasets.
                </p>
              </motion.div>

              {/* Wide Card */}
              <motion.div
                whileHover={{ y: -10 }}
                className="md:col-span-3 rounded-[2.5rem] p-10 bg-card/40 border border-white/5 backdrop-blur-xl relative group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-transparent to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="flex flex-col md:flex-row items-center justify-between gap-12">
                  <div className="flex-1">
                    <div className="w-16 h-16 rounded-3xl bg-purple-500/20 flex items-center justify-center mb-6 text-purple-500 shadow-[0_0_30px_rgba(168,85,247,0.2)]">
                      <Globe className="w-8 h-8" />
                    </div>
                    <h3 className="text-3xl font-bold mb-4">Neural Intelligence Grid</h3>
                    <p className="text-muted-foreground leading-relaxed max-w-xl">
                      Real-time global synchronization with emerging generative patterns, ensuring your defense evolves alongside SOTA synthetic models.
                    </p>
                  </div>
                  <div className="flex-1 w-full grid grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-32 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center group/icon overflow-hidden relative">
                        <Activity className="w-8 h-8 text-muted-foreground/30 group-hover/icon:text-primary transition-colors z-10" />
                        <div className="absolute inset-0 bg-primary/5 translate-y-full group-hover/icon:translate-y-0 transition-transform duration-500" />
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>

            </div>
          </div>
        </section>

        {/* Enhanced CTA Section */}
        <section className="py-48 px-6 relative">
          <div className="max-w-4xl mx-auto rounded-[3rem] bg-gradient-to-br from-primary/20 via-primary/5 to-transparent border border-white/10 p-16 text-center space-y-10 backdrop-blur-2xl relative overflow-hidden">
            <div className="absolute -top-24 -left-24 w-64 h-64 bg-primary/20 rounded-full blur-[120px]" />
            <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary/20 rounded-full blur-[120px]" />

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="relative z-10"
            >
              <h2 className="text-5xl md:text-7xl font-bold mb-8">Ready to Secure <br />Your Future?</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-12">
                Join thousands of creators and organizations leveraging AntiBanana to maintain digital integrity in an AI-driven world.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                <Link href="/detect" className="w-full sm:w-auto px-12 py-5 rounded-full bg-primary text-white font-bold text-lg hover:shadow-[0_0_60px_-10px_rgba(124,58,237,0.8)] transition-all hover:scale-105">
                  Get Started Free
                </Link>
                <Link href="/protect" className="w-full sm:w-auto px-12 py-5 rounded-full border border-white/20 bg-white/5 font-bold text-lg hover:bg-white/10 transition-all">
                  View Demo
                </Link>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-20 border-t border-white/10 bg-black/40 backdrop-blur-2xl">
          <div className="max-w-7xl mx-auto px-8 grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="col-span-1 md:col-span-2 space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-[0_0_20px_rgba(124,58,237,0.4)]">A</div>
                <span className="font-bold text-2xl tracking-tighter">AntiBanana</span>
              </div>
              <p className="text-muted-foreground max-w-sm text-lg font-light">
                Redefining digital security through forensic neural analysis and proactive biometric shielding.
              </p>
            </div>

            <div>
              <h4 className="font-bold mb-6 text-white">Platform</h4>
              <ul className="space-y-4 text-muted-foreground">
                <li><Link href="/detect" className="hover:text-primary transition-colors">Forensic Detection</Link></li>
                <li><Link href="/protect" className="hover:text-primary transition-colors">Media Protector</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">API Access</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-6 text-white">Company</h4>
              <ul className="space-y-4 text-muted-foreground">
                <li><Link href="#" className="hover:text-primary transition-colors">Ethics Protocol</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Research</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-8 mt-20 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
            <p className="text-sm text-muted-foreground">
              © 2026 AntiBanana Defense Systems. Designed for a synthetic future.
            </p>
            <div className="flex gap-8 text-sm text-muted-foreground">
              <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
              <Link href="#" className="hover:text-white transition-colors">Service Terms</Link>
            </div>
          </div>
        </footer>

      </div>
    </main>
  )
}
