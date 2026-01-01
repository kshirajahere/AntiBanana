"use client";

import type React from "react";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import {
  Shield,
  Upload,
  FileImage,
  AlertTriangle,
  CheckCircle,
  X,
  Loader2,
  Download,
  Music,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export default function ProtectPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processProgress, setProcessProgress] = useState(0);
  const [protectedImage, setProtectedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [strength, setStrength] = useState<string>("medium");
  const [results, setResults] = useState<any>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile: File) => {
    // Check if file is an image or audio
    if (
      !selectedFile.type.startsWith("image/") &&
      !selectedFile.type.startsWith("audio/")
    ) {
      setError("Please upload an image or audio file");
      return;
    }

    setFile(selectedFile);
    setError(null);

    // Create preview for images
    if (selectedFile.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      // For audio, set a placeholder
      setPreview(null);
    }
  };

  const convertToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };

  const protectFile = async () => {
    if (!file) return;

    setIsProcessing(true);
    setProcessProgress(0);
    setProtectedImage(null);
    setResults(null);
    setError(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProcessProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 5;
      });
    }, 500);

    try {
      if (file.type.startsWith("image/")) {
        // Image protection - use existing MMHI protection
        const formData = new FormData();
        formData.append("file", file);
        formData.append("strength", strength);

        const response = await fetch("http://localhost:5000/protect_image", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Protection failed");
        }

        const data = await response.json();

        if (data.protected_image) {
          const imageData = data.protected_image;
          setProtectedImage(`data:image/png;base64,${imageData}`);
          setResults(data);
          clearInterval(progressInterval);
          setProcessProgress(100);

          setTimeout(() => {
            setIsProcessing(false);
          }, 500);
        } else {
          throw new Error("Protection failed: No protected image returned");
        }
      } else if (file.type.startsWith("audio/")) {
        // Audio protection - NEW
        const formData = new FormData();
        formData.append("file", file);
        formData.append("strength", strength);

        const response = await fetch("http://localhost:5000/protect_audio", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Audio protection failed");
        }

        const data = await response.json();

        if (data.protected_audio) {
          const audioData = data.protected_audio;
          setProtectedImage(`data:audio/wav;base64,${audioData}`);
          setResults(data);
          clearInterval(progressInterval);
          setProcessProgress(100);

          setTimeout(() => {
            setIsProcessing(false);
          }, 500);
        } else {
          throw new Error("Protection failed: No protected audio returned");
        }
      } else {
        // Video protection not yet implemented
        clearInterval(progressInterval);
        setError("Only image and audio protection is currently supported");
        setIsProcessing(false);
      }
    } catch (err) {
      clearInterval(progressInterval);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
      setIsProcessing(false);
    }
  };

  const downloadProtectedFile = () => {
    if (!protectedImage) return;

    const link = document.createElement("a");
    link.href = protectedImage;

    // Determine file extension based on file type
    const isAudio = file?.type.startsWith("audio/");
    const extension = isAudio ? "wav" : "png";
    link.download = `protected_${file?.name.replace(/\.[^/.]+$/, '')}.${extension}`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const resetProcess = () => {
    setFile(null);
    setPreview(null);
    setProtectedImage(null);
    setError(null);
    setIsProcessing(false);
    setProcessProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-gradient-to-b from-background to-background/95">
      <Navbar />

      <div className="flex-1 container mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-5xl mx-auto"
        >
          <div className="flex items-center space-x-4 mb-6">
            <div className="p-3 rounded-full bg-primary/10">
              <Shield className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h1 className="text-4xl font-space font-bold">
                Deepfake Protection
              </h1>
              <p className="text-muted-foreground">
                Protect your media from AI manipulation
              </p>
            </div>
          </div>

          <Card className="mb-8 overflow-hidden border-2 bg-card/50 backdrop-blur-sm">
            <CardContent className="p-0">
              <AnimatePresence mode="wait">
                {!file && !protectedImage ? (
                  <motion.div
                    key="upload"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div
                      className={cn(
                        "p-10 transition-all duration-300",
                        isDragging
                          ? "bg-primary/10 border-primary"
                          : "bg-transparent"
                      )}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-12 text-center hover:border-primary/50 transition-colors">
                        <input
                          type="file"
                          className="hidden"
                          id="file-upload"
                          ref={fileInputRef}
                          onChange={handleFileChange}
                          accept="image/*,audio/*"
                        />
                        <label
                          htmlFor="file-upload"
                          className="cursor-pointer flex flex-col items-center"
                        >
                          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                            <Upload className="w-10 h-10 text-primary" />
                          </div>
                          <h3 className="text-xl font-medium mb-2">
                            {isDragging
                              ? "Drop your file here"
                              : "Drag and drop your file here"}
                          </h3>
                          <p className="text-sm text-muted-foreground mb-6 max-w-md">
                            Upload your image or audio to protect it against deepfake
                            manipulation. Supports JPG, PNG, WEBP, WAV, MP3.
                          </p>
                          <Button
                            size="lg"
                            className="gap-2 shadow-lg hover:shadow-primary/25"
                          >
                            <FileImage className="w-4 h-4" />
                            Select File
                          </Button>
                        </label>
                      </div>

                      {error && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive flex items-center gap-2"
                        >
                          <AlertTriangle className="w-5 h-5" />
                          <span>{error}</span>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                ) : isProcessing ? (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-10"
                  >
                    <div className="flex flex-col md:flex-row gap-8 items-center">
                      <div className="w-full md:w-1/2 aspect-square md:aspect-auto md:max-h-[400px] relative rounded-lg overflow-hidden border shadow-2xl">
                        {preview ? (
                          <img
                            src={preview || "/placeholder.svg"}
                            alt="Preview"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-muted flex items-center justify-center">
                            {file?.type.startsWith("audio/") ? (
                              <Music className="w-16 h-16 text-muted-foreground" />
                            ) : (
                              <FileImage className="w-16 h-16 text-muted-foreground" />
                            )}
                          </div>
                        )}
                        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center p-6">
                          <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
                          <h3 className="text-xl font-medium mb-2">
                            Applying MMHI Protection
                          </h3>
                          <p className="text-sm text-muted-foreground mb-4 text-center">
                            Injecting invisible protective noise patterns...
                          </p>
                          <div className="w-full max-w-md">
                            <Progress value={processProgress} className="h-2" />
                            <p className="text-xs text-right mt-1 text-muted-foreground">
                              {Math.round(processProgress)}%
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="w-full md:w-1/2 space-y-6">
                        <div className="space-y-2">
                          <h3 className="text-xl font-medium">
                            Protection Pipeline
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {file?.type.startsWith("audio/")
                              ? "Applying multi-layer audio protection:"
                              : "Applying multi-stage adversarial perturbations:"}
                          </p>
                        </div>

                        <div className="space-y-3">
                          {(file?.type.startsWith("audio/") ? [
                            { name: "Psychoacoustic Masking", progress: 20 },
                            { name: "Temporal Poisoning", progress: 40 },
                            { name: "Prosody Shifting", progress: 60 },
                            { name: "Phase Obfuscation", progress: 80 },
                            { name: "Harmonic Disruption", progress: 95 },
                          ] : [
                            { name: "Semantic Decoupling", progress: 20 },
                            { name: "Attention Hijacking", progress: 40 },
                            { name: "Frequency Poisoning", progress: 60 },
                            { name: "Boundary Shifting", progress: 80 },
                            { name: "Final Optimization", progress: 95 },
                          ]).map((step, idx) => (
                            <div key={idx} className="flex items-center gap-3">
                              <div
                                className={cn(
                                  "w-6 h-6 rounded-full flex items-center justify-center text-xs transition-colors duration-500",
                                  processProgress > step.progress
                                    ? "bg-primary text-primary-foreground"
                                    : "bg-muted text-muted-foreground"
                                )}
                              >
                                {processProgress > step.progress
                                  ? "✓"
                                  : idx + 1}
                              </div>
                              <div className="flex-1">
                                <p
                                  className={cn(
                                    "text-sm font-medium transition-colors duration-500",
                                    processProgress > step.progress
                                      ? "text-primary"
                                      : "text-muted-foreground"
                                  )}
                                >
                                  {step.name}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ) : protectedImage ? (
                  <motion.div
                    key="results"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-0"
                  >
                    <div className="p-6 text-center bg-green-500/10 border-b border-green-500/20">
                      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 bg-background shadow-sm">
                        <CheckCircle className="w-8 h-8 text-green-500" />
                      </div>

                      <h2 className="text-3xl font-bold mb-2">
                        Protection Complete
                      </h2>

                      <p className="text-muted-foreground max-w-2xl mx-auto">
                        Your {file?.type.startsWith("audio/") ? "audio" : "image"} is now protected against AI manipulation. The
                        invisible noise patterns will disrupt deepfake
                        generation models{file?.type.startsWith("audio/") ? " and voice cloning systems" : ""}.
                      </p>
                    </div>

                    <div className="flex flex-col md:flex-row">
                      <div className="w-full md:w-1/2 p-6 border-r border-b">
                        <div className="aspect-square max-h-[400px] relative rounded-lg overflow-hidden border mb-4 shadow-inner">
                          {file?.type.startsWith("audio/") ? (
                            <div className="w-full h-full bg-gradient-to-br from-primary/10 to-primary/5 flex flex-col items-center justify-center p-8">
                              <Music className="w-24 h-24 text-primary mb-4" />
                              <p className="text-lg font-medium mb-4">Protected Audio</p>
                              <audio
                                controls
                                className="w-full max-w-md"
                                src={protectedImage || ""}
                              >
                                Your browser does not support audio playback.
                              </audio>
                            </div>
                          ) : (
                            <>
                              <img
                                src={protectedImage || "/placeholder.svg"}
                                alt="Protected media"
                                className="w-full h-full object-contain bg-black/5"
                              />
                            </>
                          )}
                          <div className="absolute top-2 right-2">
                            <Badge className="bg-green-500 hover:bg-green-600 text-white border-0">
                              PROTECTED
                            </Badge>
                          </div>
                        </div>

                        <div className="flex justify-between gap-4">
                          <Button
                            variant="outline"
                            onClick={resetProcess}
                            className="flex-1"
                          >
                            <X className="w-4 h-4 mr-2" />
                            New
                          </Button>

                          <Button
                            variant="default"
                            onClick={downloadProtectedFile}
                            className="flex-1 bg-green-600 hover:bg-green-700"
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        </div>
                      </div>

                      <div className="w-full md:w-1/2 p-6">
                        <div className="space-y-6">
                          <div>
                            <h3 className="text-lg font-medium mb-2">
                              Applied Defenses
                            </h3>
                            <div className="flex flex-wrap gap-2">
                              {results?.techniques_applied?.map(
                                (technique: string, i: number) => (
                                  <Badge
                                    key={i}
                                    variant="secondary"
                                    className="text-xs"
                                  >
                                    {technique}
                                  </Badge>
                                )
                              ) || results?.phases_applied?.map(
                                (phase: string, i: number) => (
                                  <Badge
                                    key={i}
                                    variant="secondary"
                                    className="text-xs"
                                  >
                                    {phase}
                                  </Badge>
                                )
                              ) || (
                                  file?.type.startsWith("audio/") ? (
                                    <>
                                      <Badge variant="secondary">
                                        Psychoacoustic Masking
                                      </Badge>
                                      <Badge variant="secondary">
                                        Temporal Poisoning
                                      </Badge>
                                      <Badge variant="secondary">
                                        Prosody Shifting
                                      </Badge>
                                      <Badge variant="secondary">
                                        Phase Obfuscation
                                      </Badge>
                                      <Badge variant="secondary">
                                        Harmonic Disruption
                                      </Badge>
                                    </>
                                  ) : (
                                    <>
                                      <Badge variant="secondary">
                                        Semantic Decoupling
                                      </Badge>
                                      <Badge variant="secondary">
                                        Attention Hijacking
                                      </Badge>
                                      <Badge variant="secondary">
                                        Frequency Poisoning
                                      </Badge>
                                    </>
                                  )
                                )}
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 rounded-lg bg-muted/50">
                              <h4 className="text-sm font-medium mb-1">
                                Processing Time
                              </h4>
                              <p className="text-2xl font-bold">
                                {results?.processing_time
                                  ? results.processing_time.toFixed(2)
                                  : "0.00"}
                                s
                              </p>
                            </div>
                            <div className="p-4 rounded-lg bg-muted/50">
                              <h4 className="text-sm font-medium mb-1">
                                Strength
                              </h4>
                              <p className="text-2xl font-bold capitalize">
                                {strength}
                              </p>
                            </div>
                            {results?.snr_db && (
                              <div className="p-4 rounded-lg bg-muted/50 col-span-2">
                                <h4 className="text-sm font-medium mb-1">
                                  Signal-to-Noise Ratio
                                </h4>
                                <p className="text-2xl font-bold">
                                  {results.snr_db.toFixed(1)} dB
                                </p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  Imperceptible to humans ({">"} 20 dB)
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </CardContent>

            {file && !protectedImage && !isProcessing && (
              <CardFooter className="p-6 border-t bg-muted/30 flex flex-col gap-4">
                <div className="w-full">
                  <label className="text-sm font-medium mb-2 block">
                    Protection Strength
                  </label>
                  <div className="grid grid-cols-4 gap-4">
                    {["low", "medium", "high", "extreme"].map((s) => (
                      <div
                        key={s}
                        onClick={() => setStrength(s)}
                        className={cn(
                          "cursor-pointer rounded-lg border-2 p-4 text-center transition-all hover:bg-accent",
                          strength === s
                            ? "border-primary bg-primary/5"
                            : "border-muted bg-card"
                        )}
                      >
                        <div className="font-bold capitalize mb-1">{s}</div>
                        <div className="text-xs text-muted-foreground">
                          {s === "low"
                            ? "Light"
                            : s === "medium"
                              ? "Balanced"
                              : s === "high"
                                ? "Strong"
                                : "Maximum"}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row w-full gap-4 items-center pt-4 border-t">
                  <div className="flex-1 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-md overflow-hidden border bg-muted flex items-center justify-center">
                      {preview ? (
                        <img
                          src={preview || "/placeholder.svg"}
                          alt="Preview"
                          className="w-full h-full object-cover"
                        />
                      ) : file?.type.startsWith("audio/") ? (
                        <Music className="w-6 h-6 text-muted-foreground" />
                      ) : (
                        <FileImage className="w-6 h-6 text-muted-foreground" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium truncate max-w-[200px] sm:max-w-xs">
                        {file?.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {file
                          ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
                          : ""}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2 w-full sm:w-auto">
                    <Button variant="ghost" onClick={resetProcess}>
                      Cancel
                    </Button>
                    <Button
                      className="gap-2 min-w-[140px]"
                      onClick={protectFile}
                    >
                      <Shield className="w-4 h-4" />
                      {file?.type.startsWith("audio/") ? "Protect Audio" : "Protect Image"}
                    </Button>
                  </div>
                </div>
              </CardFooter>
            )}
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-medium flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-primary" />
                  How It Works
                </h3>
                <p className="text-sm text-muted-foreground">
                  Our protection system uses advanced AI to embed invisible
                  watermarks in your media. These watermarks help identify if
                  your content is used to create deepfakes.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-medium flex items-center gap-2 mb-2">
                  <FileImage className="w-5 h-5 text-primary" />
                  Supported Formats
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Images: JPG, PNG, WebP
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Audio: MP3, WAV
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Video: MP4, WebM
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-medium flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-primary" />
                  File Requirements
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Maximum file size: 100MB
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Maximum video length: 5 minutes
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>

      <Footer />
    </main>
  );
}
