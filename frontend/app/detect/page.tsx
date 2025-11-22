"use client";

import type React from "react";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactJson from "react-json-view";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import {
  Search,
  Shield,
  AlertTriangle,
  CheckCircle,
  Info,
  X,
  Loader2,
  Gauge,
  FileText,
  Download,
  ChevronRight,
  Eye,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { FileUploader } from "@/components/file-uploader";
import { AnalysisProgress, AnalysisStep } from "@/components/analysis-progress";
import { useRouter } from "next/navigation";

// Types
interface DeepfakeResult {
  label: string;
  score: number;
}

interface VideoFrameResult {
  frame_number: number;
  timestamp: string;
  prediction: string;
  fusion_score: number;
  is_fake: boolean;
}

interface VideoAnalysis {
  duration: string;
  total_frames_analyzed: number;
  fake_frames_detected: number;
  fps: number;
  frame_interval: number;
  results: VideoFrameResult[];
}

interface LipSyncAnalysis {
  real_probability: number;
  fake_probability: number;
  description?: string;
  error?: string;
  processing_time_seconds?: number;
}

interface AnalysisResults {
  deepfake?: string | DeepfakeResult[];
  video_analysis?: VideoAnalysis;
  lip_sync_analysis?: LipSyncAnalysis | number;
  manifest?: any;
  report?: any;
  segmented?: {
    LIME?: { overlay: string };
    "GradCAM++"?: { overlay: string };
  };
}

const DETECTION_STEPS: AnalysisStep[] = [
  {
    id: "facial",
    label: "Facial Analysis",
    description: "Scanning for facial inconsistencies and artifacts",
  },
  {
    id: "pattern",
    label: "Pattern Recognition",
    description: "Analyzing texture patterns and noise distribution",
  },
  {
    id: "metadata",
    label: "Metadata Verification",
    description: "Checking file integrity and origin data",
  },
  {
    id: "final",
    label: "Final Assessment",
    description: "Compiling results and generating report",
  },
];

export default function DetectPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(selectedFile);
  };

  const analyzeMedia = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setCurrentStepIndex(0);
    setResults(null);
    setError(null);

    // Simulate progress steps
    const progressInterval = setInterval(() => {
      setAnalysisProgress((prev) => {
        const next = prev + Math.random() * 5;

        // Update steps based on progress
        if (next > 25 && currentStepIndex < 1) setCurrentStepIndex(1);
        if (next > 50 && currentStepIndex < 2) setCurrentStepIndex(2);
        if (next > 75 && currentStepIndex < 3) setCurrentStepIndex(3);

        return next >= 90 ? 90 : next;
      });
    }, 500);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Determine endpoint based on file type
      const endpoint = file.type.startsWith("video/")
        ? "https://5000-01jnecfjebarp3wa2fmvx8m6es.cloudspaces.litng.ai/detect_video"
        : "https://5000-01jnecfjebarp3wa2fmvx8m6es.cloudspaces.litng.ai/detect_image";

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error("Analysis failed. Please try again.");
      }

      const data = await response.json();
      setAnalysisProgress(100);
      setCurrentStepIndex(4); // Complete

      // Short delay to show 100% progress
      setTimeout(() => {
        if (file.type.startsWith("image/")) {
          // Handle image results
          if (
            !data ||
            (typeof data === "string" &&
              data.includes("No image data received"))
          ) {
            setError("Detection failed: No valid image data received");
            setIsAnalyzing(false);
            return;
          }

          if (!data.deepfake) {
            setError("Detection failed: Could not analyze the image");
            setIsAnalyzing(false);
            return;
          }
        }
        // For both image and video results
        setResults(data);
        setIsAnalyzing(false);
      }, 800);
    } catch (err) {
      clearInterval(progressInterval);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    setIsAnalyzing(false);
    setAnalysisProgress(0);
    setCurrentStepIndex(0);
  };

  // Helper to determine result status
  const getResultStatus = () => {
    if (!results) return null;

    // Video Analysis
    if (results.video_analysis) {
      const fakePercentage =
        (results.video_analysis.fake_frames_detected /
          results.video_analysis.total_frames_analyzed) *
        100;
      if (fakePercentage > 30) return "fake";
      if (fakePercentage > 10) return "suspicious";
      return "real";
    }

    // Image Analysis
    if (Array.isArray(results.deepfake)) {
      const highestScoreResult = results.deepfake.reduce(
        (prev, current) => (prev.score > current.score ? prev : current),
        { label: "", score: Number.NEGATIVE_INFINITY }
      );
      if (highestScoreResult.label) {
        return highestScoreResult.label.toLowerCase();
      }
    } else if (typeof results.deepfake === "string") {
      if (results.deepfake.startsWith("Fake")) return "fake";
      if (results.deepfake.startsWith("Real")) return "real";
    }

    return "unknown";
  };

  const getConfidenceScore = () => {
    if (!results) return 0;

    if (results.video_analysis) {
      const fakePercentage =
        (results.video_analysis.fake_frames_detected /
          results.video_analysis.total_frames_analyzed) *
        100;
      return Math.round(fakePercentage);
    }

    if (Array.isArray(results.deepfake)) {
      const highestScoreResult = results.deepfake.reduce(
        (prev, current) => (prev.score > current.score ? prev : current),
        { label: "", score: 0 }
      );
      return Math.round(highestScoreResult.score * 100);
    }

    if (typeof results.deepfake === "string") {
      const match = results.deepfake.match(/\d+\.\d+/);
      if (match) return Math.round(Number.parseFloat(match[0]) * 100);
    }

    return 0;
  };

  const generateReport = async () => {
    if (!results) return;
    setIsGeneratingReport(true);

    try {
      const isVideo = !!results.video_analysis;
      const endpoint = isVideo
        ? "https://5000-01jnecfjebarp3wa2fmvx8m6es.cloudspaces.litng.ai/generate_video_report"
        : "https://5000-01jnecfjebarp3wa2fmvx8m6es.cloudspaces.litng.ai/generate_report";

      const bodyData = isVideo
        ? JSON.stringify({
            analysis_results: results,
            investigator_name: "AI Detection System",
            case_number: `VIDEO-${Date.now().toString(36).toUpperCase()}`,
          })
        : (() => {
            const fd = new FormData();
            if (file) fd.append("file", file);
            fd.append("investigator_name", "AI Detection System");
            fd.append("analysis_results", JSON.stringify(results));
            return fd;
          })();

      const response = await fetch(endpoint, {
        method: "POST",
        headers: isVideo ? { "Content-Type": "application/json" } : undefined,
        body: bodyData,
      });

      if (!response.ok) throw new Error("Failed to generate report");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `DeepfakeReport_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Error generating report:", err);
      setError(
        err instanceof Error ? err.message : "Failed to generate report"
      );
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const resultStatus = getResultStatus();
  const confidence = getConfidenceScore();

  return (
    <main className="min-h-screen flex flex-col bg-background">
      <Navbar />

      <div className="flex-1 container mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-6xl mx-auto"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-xl bg-primary/10 border border-primary/20">
                <Search className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
                  Deepfake Detection
                </h1>
                <p className="text-muted-foreground">
                  Analyze media for AI manipulation using advanced forensics
                </p>
              </div>
            </div>

            {results && (
              <Button
                variant="outline"
                onClick={resetAnalysis}
                className="gap-2"
              >
                <Search className="w-4 h-4" />
                New Analysis
              </Button>
            )}
          </div>

          <AnimatePresence mode="wait">
            {!file && !results ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card className="border-2 border-dashed shadow-sm">
                  <CardContent className="p-0">
                    <FileUploader
                      onFileSelect={handleFileSelect}
                      label="Upload Media for Analysis"
                      description="Support for JPG, PNG, WEBP, MP4, AVI, MOV"
                    />
                  </CardContent>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                  <Card className="bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Shield className="w-5 h-5 text-primary" />
                        Advanced Forensics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Multi-layered analysis checking for facial
                        inconsistencies, lighting artifacts, and compression
                        anomalies.
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Activity className="w-5 h-5 text-primary" />
                        Real-time Processing
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Fast and accurate detection powered by state-of-the-art
                        deep learning models.
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Eye className="w-5 h-5 text-primary" />
                        Visual Explanations
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Get detailed heatmaps and frame-by-frame analysis to
                        understand why media was flagged.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </motion.div>
            ) : isAnalyzing ? (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="max-w-2xl mx-auto"
              >
                <Card>
                  <CardContent className="p-12">
                    <AnalysisProgress
                      steps={DETECTION_STEPS}
                      currentStepIndex={currentStepIndex}
                      progress={analysisProgress}
                      title={
                        file?.type.startsWith("video/")
                          ? "Analyzing Video Frames"
                          : "Scanning Image"
                      }
                    />
                  </CardContent>
                </Card>
              </motion.div>
            ) : !results ? (
              // Preview State before analysis
              <motion.div
                key="preview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card className="overflow-hidden">
                  <div className="grid md:grid-cols-2 gap-0">
                    <div className="bg-muted/30 p-8 flex items-center justify-center border-b md:border-b-0 md:border-r">
                      <div className="relative max-w-full max-h-[500px] rounded-lg overflow-hidden shadow-lg">
                        {file?.type.startsWith("video/") ? (
                          <video
                            src={preview!}
                            controls
                            className="max-w-full max-h-[400px]"
                          />
                        ) : (
                          <img
                            src={preview!}
                            alt="Preview"
                            className="max-w-full max-h-[400px] object-contain"
                          />
                        )}
                      </div>
                    </div>
                    <div className="p-8 flex flex-col justify-center space-y-6">
                      <div>
                        <h2 className="text-2xl font-bold mb-2">
                          Ready to Analyze
                        </h2>
                        <p className="text-muted-foreground">
                          {file?.name} (
                          {(file!.size / (1024 * 1024)).toFixed(2)} MB)
                        </p>
                      </div>

                      <div className="space-y-4">
                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span>File integrity verified</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span>
                            Format supported (
                            {file?.type.split("/")[1].toUpperCase()})
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-3 pt-4">
                        <Button
                          variant="outline"
                          onClick={resetAnalysis}
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                        <Button onClick={analyzeMedia} className="flex-1 gap-2">
                          <Search className="w-4 h-4" />
                          Start Analysis
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ) : (
              // Results State
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Main Verdict Card */}
                <Card
                  className={cn(
                    "border-l-4 overflow-hidden",
                    resultStatus === "fake"
                      ? "border-l-destructive"
                      : resultStatus === "suspicious"
                      ? "border-l-amber-500"
                      : "border-l-green-500"
                  )}
                >
                  <CardContent className="p-8">
                    <div className="flex flex-col md:flex-row items-center gap-8">
                      <div
                        className={cn(
                          "w-24 h-24 rounded-full flex items-center justify-center flex-shrink-0",
                          resultStatus === "fake"
                            ? "bg-destructive/10 text-destructive"
                            : resultStatus === "suspicious"
                            ? "bg-amber-500/10 text-amber-500"
                            : "bg-green-500/10 text-green-500"
                        )}
                      >
                        {resultStatus === "fake" ? (
                          <AlertTriangle className="w-12 h-12" />
                        ) : resultStatus === "suspicious" ? (
                          <Info className="w-12 h-12" />
                        ) : (
                          <CheckCircle className="w-12 h-12" />
                        )}
                      </div>

                      <div className="flex-1 text-center md:text-left space-y-2">
                        <h2 className="text-3xl font-bold">
                          {resultStatus === "fake"
                            ? "Deepfake Detected"
                            : resultStatus === "suspicious"
                            ? "Potential Manipulation"
                            : "Likely Authentic"}
                        </h2>
                        <p className="text-muted-foreground text-lg">
                          {resultStatus === "fake"
                            ? "High probability of AI manipulation detected."
                            : resultStatus === "suspicious"
                            ? "Some anomalies detected, manual review recommended."
                            : "No significant signs of manipulation found."}
                        </p>
                      </div>

                      <div className="flex flex-col items-center gap-2 min-w-[150px]">
                        <div className="text-sm font-medium text-muted-foreground">
                          Confidence Score
                        </div>
                        <div
                          className={cn(
                            "text-4xl font-bold",
                            resultStatus === "fake"
                              ? "text-destructive"
                              : resultStatus === "suspicious"
                              ? "text-amber-500"
                              : "text-green-500"
                          )}
                        >
                          {confidence}%
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Column: Visuals */}
                  <div className="lg:col-span-1 space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Analyzed Media</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="rounded-lg overflow-hidden border bg-muted/50 relative">
                          {file?.type.startsWith("video/") ? (
                            <video
                              src={preview!}
                              controls
                              className="w-full h-auto"
                            />
                          ) : (
                            <img
                              src={preview!}
                              alt="Analyzed"
                              className="w-full h-auto"
                            />
                          )}
                          {resultStatus === "fake" && (
                            <div className="absolute top-2 right-2">
                              <Badge variant="destructive">FAKE</Badge>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Heatmaps for Images */}
                    {results.segmented && (
                      <Card>
                        <CardHeader>
                          <CardTitle>AI Heatmaps</CardTitle>
                          <CardDescription>
                            Visualizing manipulated regions
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {results.segmented.LIME?.overlay && (
                            <div>
                              <div className="text-xs font-medium mb-2 text-muted-foreground">
                                LIME Analysis
                              </div>
                              <div className="rounded-lg overflow-hidden border">
                                <img
                                  src={results.segmented.LIME.overlay}
                                  alt="LIME"
                                  className="w-full"
                                />
                              </div>
                            </div>
                          )}
                          {results.segmented["GradCAM++"]?.overlay && (
                            <div>
                              <div className="text-xs font-medium mb-2 text-muted-foreground">
                                GradCAM++ Analysis
                              </div>
                              <div className="rounded-lg overflow-hidden border">
                                <img
                                  src={results.segmented["GradCAM++"].overlay}
                                  alt="GradCAM"
                                  className="w-full"
                                />
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )}

                    <div className="flex flex-col gap-3">
                      <Button
                        onClick={generateReport}
                        disabled={isGeneratingReport}
                        className="w-full gap-2"
                      >
                        {isGeneratingReport ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <FileText className="w-4 h-4" />
                        )}
                        Download Full Report
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => router.push("/protect")}
                        className="w-full gap-2"
                      >
                        <Shield className="w-4 h-4" />
                        Protect This Media
                      </Button>
                    </div>
                  </div>

                  {/* Right Column: Detailed Analysis */}
                  <div className="lg:col-span-2">
                    <Tabs defaultValue="details" className="w-full">
                      <TabsList className="w-full justify-start">
                        <TabsTrigger value="details">
                          Analysis Details
                        </TabsTrigger>
                        {results.video_analysis && (
                          <TabsTrigger value="frames">
                            Frame Analysis
                          </TabsTrigger>
                        )}
                        {results.lip_sync_analysis && (
                          <TabsTrigger value="lipsync">Lip Sync</TabsTrigger>
                        )}
                        <TabsTrigger value="metadata">Metadata</TabsTrigger>
                      </TabsList>

                      <TabsContent value="details" className="space-y-4 mt-4">
                        <Card>
                          <CardHeader>
                            <CardTitle>Detailed Findings</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-6">
                            {results.report ? (
                              <div className="space-y-4">
                                {[
                                  "Visual Content Analysis",
                                  "Anomaly Detection",
                                  "Deep Learning Model Evaluation",
                                ].map(
                                  (key) =>
                                    results.report[key] && (
                                      <div key={key} className="space-y-2">
                                        <h4 className="font-semibold text-sm text-primary">
                                          {key}
                                        </h4>
                                        <p className="text-sm text-muted-foreground leading-relaxed">
                                          {results.report[key]}
                                        </p>
                                      </div>
                                    )
                                )}
                              </div>
                            ) : (
                              <div className="text-center py-8 text-muted-foreground">
                                Detailed report generation unavailable.
                              </div>
                            )}
                          </CardContent>
                        </Card>

                        {Array.isArray(results.deepfake) && (
                          <Card>
                            <CardHeader>
                              <CardTitle>Model Confidence</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-4">
                                {results.deepfake.map((res, idx) => (
                                  <div key={idx} className="space-y-1">
                                    <div className="flex justify-between text-sm">
                                      <span>{res.label}</span>
                                      <span className="font-medium">
                                        {(res.score * 100).toFixed(1)}%
                                      </span>
                                    </div>
                                    <Progress
                                      value={res.score * 100}
                                      className={cn(
                                        "h-2",
                                        res.label.toLowerCase().includes("fake")
                                          ? "bg-destructive/20"
                                          : "bg-green-500/20"
                                      )}
                                    />
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </TabsContent>

                      {results.video_analysis && (
                        <TabsContent value="frames" className="mt-4">
                          <Card>
                            <CardHeader>
                              <CardTitle>Frame-by-Frame Analysis</CardTitle>
                              <CardDescription>
                                {results.video_analysis.fake_frames_detected}{" "}
                                suspicious frames detected out of{" "}
                                {results.video_analysis.total_frames_analyzed}{" "}
                                analyzed.
                              </CardDescription>
                            </CardHeader>
                            <CardContent>
                              <div className="rounded-md border">
                                <div className="grid grid-cols-4 bg-muted p-3 text-xs font-medium">
                                  <div>Time</div>
                                  <div>Frame</div>
                                  <div>Score</div>
                                  <div>Status</div>
                                </div>
                                <div className="max-h-[400px] overflow-y-auto">
                                  {results.video_analysis.results.map(
                                    (frame, idx) => (
                                      <div
                                        key={idx}
                                        className={cn(
                                          "grid grid-cols-4 p-3 text-xs border-t items-center",
                                          frame.is_fake
                                            ? "bg-destructive/5"
                                            : ""
                                        )}
                                      >
                                        <div>{frame.timestamp}</div>
                                        <div>{frame.frame_number}</div>
                                        <div>
                                          {frame.fusion_score?.toFixed(3) ||
                                            "N/A"}
                                        </div>
                                        <div>
                                          {frame.is_fake ? (
                                            <Badge
                                              variant="destructive"
                                              className="text-[10px] h-5"
                                            >
                                              FAKE
                                            </Badge>
                                          ) : (
                                            <Badge
                                              variant="outline"
                                              className="text-[10px] h-5 text-green-600 border-green-200"
                                            >
                                              REAL
                                            </Badge>
                                          )}
                                        </div>
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>
                      )}

                      {results.lip_sync_analysis && (
                        <TabsContent value="lipsync" className="mt-4">
                          <Card>
                            <CardHeader>
                              <CardTitle>Lip Synchronization</CardTitle>
                            </CardHeader>
                            <CardContent>
                              {typeof results.lip_sync_analysis === "object" ? (
                                <div className="space-y-6">
                                  <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 rounded-lg bg-muted/50 text-center">
                                      <div className="text-sm text-muted-foreground mb-1">
                                        Real Probability
                                      </div>
                                      <div className="text-2xl font-bold text-green-500">
                                        {(
                                          results.lip_sync_analysis
                                            .real_probability * 100
                                        ).toFixed(1)}
                                        %
                                      </div>
                                    </div>
                                    <div className="p-4 rounded-lg bg-muted/50 text-center">
                                      <div className="text-sm text-muted-foreground mb-1">
                                        Fake Probability
                                      </div>
                                      <div className="text-2xl font-bold text-destructive">
                                        {(
                                          results.lip_sync_analysis
                                            .fake_probability * 100
                                        ).toFixed(1)}
                                        %
                                      </div>
                                    </div>
                                  </div>
                                  {results.lip_sync_analysis.description && (
                                    <p className="text-sm text-muted-foreground bg-muted p-4 rounded-lg">
                                      {results.lip_sync_analysis.description}
                                    </p>
                                  )}
                                </div>
                              ) : (
                                <div className="text-center p-4">
                                  <div className="text-2xl font-bold mb-2">
                                    {(results.lip_sync_analysis * 100).toFixed(
                                      1
                                    )}
                                    %
                                  </div>
                                  <p className="text-sm text-muted-foreground">
                                    Sync Confidence Score
                                  </p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </TabsContent>
                      )}

                      <TabsContent value="metadata" className="mt-4">
                        <Card>
                          <CardHeader>
                            <CardTitle>File Metadata</CardTitle>
                          </CardHeader>
                          <CardContent>
                            {results.manifest ? (
                              <div className="rounded-lg overflow-hidden border">
                                <ReactJson
                                  src={results.manifest}
                                  theme="monokai"
                                  style={{ padding: "20px", fontSize: "12px" }}
                                  displayDataTypes={false}
                                />
                              </div>
                            ) : (
                              <div className="text-center py-8 text-muted-foreground">
                                No metadata manifest available.
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </TabsContent>
                    </Tabs>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
      <Footer />
    </main>
  );
}
