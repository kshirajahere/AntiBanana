"use client";

import { motion } from "framer-motion";
import { Shield, Search, Lock, Menu, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={cn(
          "fixed top-6 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none"
        )}
      >
        <div
          className={cn(
            "pointer-events-auto flex items-center justify-between gap-8 px-6 py-3 rounded-full transition-all duration-300 border border-white/10",
            scrolled
              ? "bg-black/50 backdrop-blur-xl shadow-lg shadow-primary/5 w-full max-w-2xl"
              : "bg-transparent border-transparent w-full max-w-7xl"
          )}
        >
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-primary/20 group-hover:bg-primary/30 transition-colors">
              <Shield className="w-5 h-5 text-primary" />
            </div>
            <span className="font-bold text-lg tracking-tight">AntiBanana</span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            <NavLink href="/protect" icon={<Lock className="w-4 h-4" />} label="Protect" />
            <NavLink href="/detect" icon={<Search className="w-4 h-4" />} label="Detect" />
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/detect">
              <Button variant="default" size="sm" className="rounded-full bg-primary hover:bg-primary/90 text-white px-6 shadow-[0_0_20px_-5px_rgba(124,58,237,0.5)] hover:shadow-[0_0_25px_-5px_rgba(124,58,237,0.6)] transition-all duration-300">
                Get Started
              </Button>
            </Link>
          </div>

          <button
            className="md:hidden p-2 text-muted-foreground hover:text-foreground"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed inset-0 z-40 bg-background/95 backdrop-blur-xl pt-24 px-6 md:hidden"
        >
          <div className="flex flex-col gap-4">
            <Link
              href="/protect"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className="p-2 rounded-lg bg-primary/20 text-primary">
                <Lock className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold">Protect Media</div>
                <div className="text-sm text-muted-foreground">Secure your images and audio</div>
              </div>
            </Link>
            <Link
              href="/detect"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className="p-2 rounded-lg bg-blue-500/20 text-blue-500">
                <Search className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold">Detect Deepfakes</div>
                <div className="text-sm text-muted-foreground">Analyze media for manipulation</div>
              </div>
            </Link>
          </div>
        </motion.div>
      )}
    </>
  );
}

function NavLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}