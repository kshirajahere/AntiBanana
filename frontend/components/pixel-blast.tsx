"use client";

import React, { useEffect, useRef } from "react";

interface PixelBlastProps {
    variant?: "circle" | "square";
    pixelSize?: number;
    color?: string;
    patternScale?: number;
    patternDensity?: number;
    pixelSizeJitter?: number;
    enableRipples?: boolean;
    rippleSpeed?: number;
    rippleThickness?: number;
    rippleIntensityScale?: number;
    liquid?: boolean;
    liquidStrength?: number;
    liquidRadius?: number;
    liquidWobbleSpeed?: number;
    speed?: number;
    edgeFade?: number;
    transparent?: boolean;
}

interface Particle {
    x: number;
    y: number;
    baseX: number;
    baseY: number;
    size: number;
    color: string;
    vx: number;
    vy: number;
    hue: number;
}

export default function PixelBlast({
    variant = "circle",
    pixelSize = 4,
    color = "#B19EEF",
    patternScale = 3,
    patternDensity = 1.2,
    pixelSizeJitter = 0.5,
    enableRipples = true,
    rippleSpeed = 0.4,
    rippleThickness = 0.12,
    rippleIntensityScale = 1.5,
    liquid = true,
    liquidStrength = 0.12,
    liquidRadius = 1.2,
    liquidWobbleSpeed = 5,
    speed = 0.6,
    edgeFade = 0.15,
    transparent = true,
}: PixelBlastProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const particlesRef = useRef<Particle[]>([]);
    const mouseRef = useRef({ x: -1000, y: -1000 });
    const animationRef = useRef<number>();
    const timeRef = useRef(0);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d", { alpha: transparent });
        if (!ctx) return;

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            initParticles();
        };

        const isInBounds = (x: number, y: number) => {
            return x >= -100 && x <= canvas.width + 100 && y >= -100 && y <= canvas.height + 100;
        };

        const addParticle = (baseX: number, baseY: number, hue: number) => {
            const saturation = 60 + Math.random() * 20;
            const lightness = 50 + Math.random() * 20;
            const particleColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;

            particlesRef.current.push({
                x: baseX,
                y: baseY,
                baseX,
                baseY,
                size: pixelSize * (0.7 + Math.random() * pixelSizeJitter),
                color: particleColor,
                vx: 0,
                vy: 0,
                hue,
            });
        };

        // Reduced intensity - much fewer particles
        const initParticles = () => {
            particlesRef.current = [];
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const baseHues = [260, 270, 280, 220, 240];

            // Only 1-2 patterns instead of 5-8
            const patternTypes = Math.floor(Math.random() * 2) + 1;

            for (let p = 0; p < patternTypes; p++) {
                const patternType = Math.floor(Math.random() * 6);
                const hue = baseHues[Math.floor(Math.random() * baseHues.length)];
                const offsetX = p % 3 === 0 ? 0 : (Math.random() - 0.5) * canvas.width * 0.8;
                const offsetY = (Math.random() - 0.5) * canvas.height * 0.5;

                switch (patternType) {
                    case 0: createSpiralPattern(centerX + offsetX, centerY + offsetY, hue); break;
                    case 1: createCirclePattern(centerX + offsetX, centerY + offsetY, hue); break;
                    case 2: createWavePattern(centerY + offsetY, hue); break;
                    case 3: createGridPattern(centerX + offsetX, centerY + offsetY, hue); break;
                    case 4: createClusterPattern(hue); break;
                    case 5: createSideFillPattern(hue); break;
                }
            }

            fillEdges();
        };

        const createSpiralPattern = (cx: number, cy: number, hue: number) => {
            const turns = 4 + Math.random() * 3;
            const spacing = 5 + Math.random() * 8;

            // Reduced from 600 to 30
            for (let i = 0; i < 30 * patternDensity; i++) {
                const angle = (i / 50) * Math.PI * turns;
                const radius = i * spacing * 0.4;
                const baseX = cx + Math.cos(angle) * radius;
                const baseY = cy + Math.sin(angle) * radius;

                if (isInBounds(baseX, baseY)) {
                    addParticle(baseX, baseY, hue);
                }
            }
        };

        const createCirclePattern = (cx: number, cy: number, hue: number) => {
            // Reduced from 5-10 rings to 2-3
            const rings = 2 + Math.floor(Math.random() * 2);

            for (let r = 0; r < rings; r++) {
                const radius = 80 + r * 140;
                // Reduced density massively
                const points = Math.floor(radius * patternDensity * 0.03);

                for (let i = 0; i < points; i++) {
                    const angle = (i / points) * Math.PI * 2;
                    const jitter = (Math.random() - 0.5) * 30;
                    const baseX = cx + Math.cos(angle) * (radius + jitter);
                    const baseY = cy + Math.sin(angle) * (radius + jitter);

                    if (isInBounds(baseX, baseY)) {
                        addParticle(baseX, baseY, hue);
                    }
                }
            }
        };

        const createWavePattern = (offsetY: number, hue: number) => {
            const amplitude = 80 + Math.random() * 150;
            const frequency = 0.003 + Math.random() * 0.008;
            const offset = Math.random() * Math.PI * 2;
            const numWaves = 2 + Math.floor(Math.random() * 3);

            for (let w = 0; w < numWaves; w++) {
                const waveY = offsetY + (w - numWaves / 2) * 120;
                // Increased spacing from 5 to 25
                for (let x = -100; x < canvas.width + 100; x += 25 / patternDensity) {
                    const y = Math.sin(x * frequency + offset + w * Math.PI) * amplitude + waveY;

                    if (isInBounds(x, y)) {
                        addParticle(x, y, hue);
                    }
                }
            }
        };

        const createGridPattern = (cx: number, cy: number, hue: number) => {
            const spacing = 30 + Math.random() * 50;
            // Much smaller grid
            const gridWidth = Math.ceil(canvas.width / spacing / 8);
            const gridHeight = Math.ceil(canvas.height / spacing / 8);

            for (let x = -gridWidth; x <= gridWidth; x++) {
                for (let y = -gridHeight; y <= gridHeight; y++) {
                    // More holes in grid
                    if (Math.random() > 0.85) {
                        const baseX = cx + x * spacing;
                        const baseY = cy + y * spacing;

                        if (isInBounds(baseX, baseY)) {
                            addParticle(baseX, baseY, hue);
                        }
                    }
                }
            }
        };

        const createClusterPattern = (hue: number) => {
            // Reduced from 10-25 to 2-4
            const clusters = 2 + Math.floor(Math.random() * 3);

            for (let c = 0; c < clusters; c++) {
                const clusterX = Math.random() * canvas.width;
                const clusterY = Math.random() * canvas.height;
                const clusterSize = 50 + Math.random() * 100;

                // Reduced density by 80%
                for (let i = 0; i < clusterSize * patternDensity * 0.2; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const radius = Math.random() * 140;
                    const baseX = clusterX + Math.cos(angle) * radius;
                    const baseY = clusterY + Math.sin(angle) * radius;

                    if (isInBounds(baseX, baseY)) {
                        addParticle(baseX, baseY, hue);
                    }
                }
            }
        };

        const createSideFillPattern = (hue: number) => {
            // Reduced sections from 6 to 3
            const sections = 3;

            for (let s = 0; s < sections; s++) {
                const y = (canvas.height / sections) * s + canvas.height / (sections * 2);

                // Reduced from 80 to 15 particles per side
                for (let i = 0; i < 15 * patternDensity; i++) {
                    const x = Math.random() * 400;
                    const yOffset = (Math.random() - 0.5) * 250;
                    addParticle(x, y + yOffset, hue);
                }

                for (let i = 0; i < 15 * patternDensity; i++) {
                    const x = canvas.width - Math.random() * 400;
                    const yOffset = (Math.random() - 0.5) * 250;
                    addParticle(x, y + yOffset, hue);
                }
            }
        };

        const fillEdges = () => {
            const edgeHue = 270;
            // Reduced from 150 to 20
            const particles = 20 * patternDensity;

            for (let i = 0; i < particles; i++) {
                addParticle(Math.random() * canvas.width, Math.random() * 200, edgeHue);
                addParticle(Math.random() * canvas.width, canvas.height - Math.random() * 200, edgeHue);
                addParticle(Math.random() * 250, Math.random() * canvas.height, edgeHue);
                addParticle(canvas.width - Math.random() * 250, Math.random() * canvas.height, edgeHue);
            }
        };

        const animate = () => {
            if (!ctx || !canvas) return;

            timeRef.current += 0.016 * speed;

            if (transparent) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            } else {
                ctx.fillStyle = "rgba(10, 10, 20, 0.05)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }

            particlesRef.current.forEach((particle, index) => {
                let offsetX = 0;
                let offsetY = 0;

                if (liquid) {
                    const wobbleX = Math.sin(timeRef.current * liquidWobbleSpeed + particle.baseX * 0.01 + index * 0.1);
                    const wobbleY = Math.cos(timeRef.current * liquidWobbleSpeed * 0.8 + particle.baseY * 0.01 + index * 0.1);
                    offsetX = wobbleX * liquidStrength * 50 * liquidRadius;
                    offsetY = wobbleY * liquidStrength * 50 * liquidRadius;
                }

                if (enableRipples) {
                    const distFromCenter = Math.sqrt(
                        Math.pow(particle.baseX - canvas.width / 2, 2) +
                        Math.pow(particle.baseY - canvas.height / 2, 2)
                    );
                    const ripple = Math.sin(distFromCenter * 0.015 - timeRef.current * rippleSpeed * 15) * rippleIntensityScale * 15;
                    offsetY += ripple;
                    offsetX += Math.cos(distFromCenter * 0.015 - timeRef.current * rippleSpeed * 15) * rippleIntensityScale * 5;
                }

                const dx = mouseRef.current.x - particle.x;
                const dy = mouseRef.current.y - particle.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const maxDist = 200;

                if (dist < maxDist && dist > 0) {
                    const force = (maxDist - dist) / maxDist;
                    particle.vx -= (dx / dist) * force * 3;
                    particle.vy -= (dy / dist) * force * 3;
                }

                particle.vx *= 0.92;
                particle.vy *= 0.92;

                const springX = (particle.baseX - particle.x) * 0.03;
                const springY = (particle.baseY - particle.y) * 0.03;

                particle.vx += springX;
                particle.vy += springY;

                particle.x += particle.vx + offsetX * 0.15;
                particle.y += particle.vy + offsetY * 0.15;

                const distFromEdge = Math.min(
                    particle.x,
                    particle.y,
                    canvas.width - particle.x,
                    canvas.height - particle.y
                );
                const fadeDistance = Math.min(canvas.width, canvas.height) * edgeFade;
                const alpha = Math.min(1, Math.max(0.2, distFromEdge / fadeDistance));

                const hueShift = Math.sin(timeRef.current * 2 + index * 0.1) * 10;
                const shimmerColor = `hsl(${particle.hue + hueShift}, ${60 + Math.sin(timeRef.current * 3 + index * 0.2) * 20}%, ${50 + Math.sin(timeRef.current * 4 + index * 0.15) * 15}%)`;

                ctx.fillStyle = shimmerColor;
                ctx.globalAlpha = alpha * (0.5 + Math.sin(timeRef.current * 2 + index * 0.1) * 0.2);

                if (variant === "circle") {
                    ctx.beginPath();
                    ctx.arc(particle.x, particle.y, particle.size / 2, 0, Math.PI * 2);
                    ctx.fill();

                    if (Math.random() > 0.98) {
                        ctx.shadowBlur = 20;
                        ctx.shadowColor = shimmerColor;
                        ctx.fill();
                        ctx.shadowBlur = 0;
                    }
                } else {
                    const rotation = timeRef.current * 0.5 + index * 0.1;
                    ctx.save();
                    ctx.translate(particle.x, particle.y);
                    ctx.rotate(rotation);
                    ctx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size);
                    ctx.restore();
                }
            });

            ctx.globalAlpha = 1;
            animationRef.current = requestAnimationFrame(animate);
        };

        const handleMouseMove = (e: MouseEvent) => {
            mouseRef.current = { x: e.clientX, y: e.clientY };
        };

        const handleTouchMove = (e: TouchEvent) => {
            if (e.touches.length > 0) {
                mouseRef.current = {
                    x: e.touches[0].clientX,
                    y: e.touches[0].clientY,
                };
            }
        };

        const handleMouseLeave = () => {
            mouseRef.current = { x: -1000, y: -1000 };
        };

        resizeCanvas();
        window.addEventListener("resize", resizeCanvas);
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("touchmove", handleTouchMove);
        window.addEventListener("mouseleave", handleMouseLeave);
        animate();

        return () => {
            window.removeEventListener("resize", resizeCanvas);
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("touchmove", handleTouchMove);
            window.removeEventListener("mouseleave", handleMouseLeave);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [
        color,
        pixelSize,
        speed,
        liquid,
        liquidStrength,
        liquidRadius,
        liquidWobbleSpeed,
        enableRipples,
        rippleSpeed,
        rippleIntensityScale,
        edgeFade,
        variant,
        pixelSizeJitter,
        patternScale,
        patternDensity,
        transparent,
    ]);

    return (
        <canvas
            ref={canvasRef}
            className="w-full h-full"
            style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
            }}
        />
    );
}
