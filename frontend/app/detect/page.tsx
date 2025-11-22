"use client";

import type React from "react";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
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
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import {
  AlertTriangle,
  CheckCircle,
  Info,
  X,
  Loader2,
  FileText,
  Shield,
  Search,
  Upload,
  FileImage,
  Gauge,
  FileWarning,
} from "lucide-react";

export default function DetectPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

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
    setAnalysisProgress(0);
    setResults(null);
    setError(null);

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
    // Check if file is an image or video
    if (
      !selectedFile.type.startsWith("image/") &&
      !selectedFile.type.startsWith("video/")
    ) {
      setError(
        "Please upload an image or video file (JPG, PNG, WEBP, MP4, AVI, MOV)"
      );
      return;
    }

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
    setResults(null);
    setError(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 15;
      });
    }, 300);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Enable XAI explanations for images
      if (file.type.startsWith("image/")) {
        formData.append("enable_xai", "true");
        formData.append("xai_methods", "GradCAM++");
      } else if (file.type.startsWith("video/")) {
        // Add video specific parameters
        formData.append("num_samples", "30");
        formData.append("strategy", "hybrid");
        formData.append("include_xai", "false");
      }

      // Determine endpoint based on file type
      // Using detect-video for video files and detect for images
      const endpoint = file.type.startsWith("video/")
        ? "http://localhost:5000/detect-video"
        : "http://localhost:5000/detect";

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
        if (file.type.startsWith("video/")) {
          setResults({
            video_analysis: data,
            lip_sync_analysis: data.lip_sync_analysis || null
          });
        } else {
          setResults(data);
        }
        setIsAnalyzing(false);
      }, 500);
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
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const generateVideoReport = () => {
    setIsGeneratingReport(true);
    // Simulate report generation
    setTimeout(() => {
      setIsGeneratingReport(false);
    }, 2000);
  };

  // Determine if the image is fake or real based on results
  const getResultStatus = () => {
    if (!results) return null;

    // Handle new array format
    if (Array.isArray(results.deepfake)) {
      // Find the object with the highest score
      interface DeepfakeResult {
        label: string;
        score: number;
      }

      const highestScoreResult: DeepfakeResult = results.deepfake.reduce(
        (prev: DeepfakeResult, current: DeepfakeResult) =>
          prev.score > current.score ? prev : current,
        { label: "", score: Number.NEGATIVE_INFINITY }
      );

      if (highestScoreResult.label) {
        return highestScoreResult.label.toLowerCase();
      }
      return "unknown";
    }

    // Handle old string format for backwards compatibility
    const deepfakeResult = results.deepfake || "";
    if (deepfakeResult.startsWith("Fake")) {
      return "fake";
    } else if (deepfakeResult.startsWith("Real")) {
      return "real";
    }
    return "unknown";
  };

  // Extract confidence score from results
  const getConfidenceScore = () => {
    if (!results || !results.deepfake) return null;

    if (typeof results.deepfake === "string") {
      const match = results.deepfake.match(/\d+\.\d+/);
      if (match) {
        const score = Number.parseFloat(match[0]);
        // Convert to percentage between 0-100
        return Math.abs(score) * 100;
      }
    } else if (Array.isArray(results.deepfake)) {
      // Handle new array format
      const highestScoreResult = results.deepfake.reduce(
        (prev: any, current: any) =>
          prev.score > current.score ? prev : current,
        { label: "", score: Number.NEGATIVE_INFINITY }
      );
      return highestScoreResult.score * 100;
    }

    return null;
  };

  const resultStatus = getResultStatus();
  const confidenceScore = getConfidenceScore();

  const VideoResultsDisplay = () => {
    if (!results || !results.video_analysis) return null;

    const { video_analysis, lip_sync_analysis } = results;
    const fakeFramesPercentage =
      (video_analysis.fake_frames_detected /
        video_analysis.total_frames_analyzed) *
      100;

    return (
      <div className="flex flex-col">
        <div
          className={cn(
            "p-6 text-center",
            fakeFramesPercentage > 30
              ? "bg-destructive/10"
              : fakeFramesPercentage > 10
                ? "bg-amber-500/10"
                : "bg-green-500/10"
          )}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 bg-background">
            {fakeFramesPercentage > 30 ? (
              <AlertTriangle className="w-8 h-8 text-destructive" />
            ) : fakeFramesPercentage > 10 ? (
              <Info className="w-8 h-8 text-amber-500" />
            ) : (
              <CheckCircle className="w-8 h-8 text-green-500" />
            )}
          </div>

          <h2 className="text-3xl font-bold mb-2">
            {fakeFramesPercentage > 30
              ? "Deepfake Detected"
              : fakeFramesPercentage > 10
                ? "Possible Manipulation"
                : "Likely Authentic"}
          </h2>

          <p className="text-muted-foreground max-w-2xl mx-auto">
            {fakeFramesPercentage > 30
              ? "Our AI has detected significant signs of manipulation in this video."
              : fakeFramesPercentage > 10
                ? "Our AI has detected some potential signs of manipulation in this video."
                : "Our AI analysis indicates this is likely an authentic video without significant signs of deepfake manipulation."}
          </p>

          <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-background">
            <span className="text-sm font-medium">Fake Frames:</span>
            <Badge
              variant={
                fakeFramesPercentage > 30
                  ? "destructive"
                  : fakeFramesPercentage > 10
                    ? "outline"
                    : "default"
              }
            >
              {video_analysis.fake_frames_detected} /{" "}
              {video_analysis.total_frames_analyzed} (
              {Math.round(fakeFramesPercentage)}%)
            </Badge>
          </div>
        </div>

        <div className="flex flex-col md:flex-row">
          <div className="w-full md:w-1/2 p-6 border-r border-b">
            <div className="aspect-video max-h-[400px] relative rounded-lg overflow-hidden border mb-4">
              {preview && (
                <video
                  src={preview}
                  controls
                  className="w-full h-full object-cover"
                />
              )}

              {fakeFramesPercentage > 30 && (
                <div className="absolute top-2 right-2">
                  <Badge variant="destructive" className="text-xs px-2 py-1">
                    FAKE
                  </Badge>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-2 mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={resetAnalysis}
                className="gap-2"
              >
                <X className="w-4 h-4" />
                New Analysis
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={generateVideoReport}
                className="gap-2"
                disabled={isGeneratingReport}
              >
                {isGeneratingReport ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4" />
                )}
                Generate Report
              </Button>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="secondary"
                      size="sm"
                      className="gap-2 ml-auto"
                    >
                      <Shield className="w-4 h-4" />
                      Protect Your Media
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Add protection to your own media</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>

          <div className="w-full md:w-1/2 p-6">
            <Tabs defaultValue="summary">
              <TabsList className="w-full mb-4">
                <TabsTrigger value="summary" className="flex-1">
                  Summary
                </TabsTrigger>
                <TabsTrigger value="frames" className="flex-1">
                  Frame Analysis
                </TabsTrigger>
                <TabsTrigger value="lipsync" className="flex-1">
                  Lip Sync
                </TabsTrigger>
                <TabsTrigger value="technical" className="flex-1">
                  Technical Details
                </TabsTrigger>
              </TabsList>

              <TabsContent value="summary" className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Analysis Summary</h3>
                  <p className="text-sm text-muted-foreground">
                    {fakeFramesPercentage > 30
                      ? "This video shows significant signs of AI manipulation consistent with deepfake technology. Multiple frames were flagged as potentially fake."
                      : fakeFramesPercentage > 10
                        ? "This video shows some signs of potential manipulation. A small number of frames were flagged as suspicious."
                        : "This video appears to be authentic. Our analysis found natural patterns and consistent features throughout the video."}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-muted">
                    <h4 className="text-sm font-medium mb-1">Video Duration</h4>
                    <p className="text-xs text-muted-foreground">
                      {video_analysis.duration}
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-muted">
                    <h4 className="text-sm font-medium mb-1">
                      Frames Analyzed
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {video_analysis.total_frames_analyzed}
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-muted">
                    <h4 className="text-sm font-medium mb-1">Fake Frames</h4>
                    <p
                      className={cn(
                        "text-xs",
                        fakeFramesPercentage > 30
                          ? "text-destructive"
                          : fakeFramesPercentage > 10
                            ? "text-amber-500"
                            : "text-green-500"
                      )}
                    >
                      {video_analysis.fake_frames_detected} (
                      {Math.round(fakeFramesPercentage)}%)
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-muted">
                    <h4 className="text-sm font-medium mb-1">
                      Lip Sync Analysis
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {lip_sync_analysis?.error
                        ? "Analysis failed"
                        : lip_sync_analysis?.fake_probability !== undefined
                          ? lip_sync_analysis.fake_probability > 0.5
                            ? "Potential mismatch detected"
                            : "No issues detected"
                          : typeof lip_sync_analysis === "number"
                            ? lip_sync_analysis < 0.5
                              ? "Potential mismatch detected"
                              : "No issues detected"
                            : "Analysis unavailable"}
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="frames" className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">
                    Frame-by-Frame Analysis
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Detailed analysis of individual video frames.
                  </p>
                </div>

                <div className="border rounded-md overflow-hidden">
                  <div className="grid grid-cols-12 bg-muted p-2 text-xs font-medium">
                    <div className="col-span-1">Frame</div>
                    <div className="col-span-3">Timestamp</div>
                    <div className="col-span-2">Result</div>
                    <div className="col-span-3">Score</div>
                    <div className="col-span-3">Status</div>
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {(video_analysis.results || []).map((frame: any, index: any) => (
                      <div
                        key={index}
                        className={cn(
                          "grid grid-cols-12 p-2 text-xs border-t",
                          frame.is_fake ? "bg-destructive/5" : ""
                        )}
                      >
                        <div className="col-span-1">{frame.frame_number}</div>
                        <div className="col-span-3">{frame.timestamp}</div>
                        <div className="col-span-2">{frame.prediction}</div>
                        <div className="col-span-3">
                          {frame.fusion_score
                            ? frame.fusion_score.toFixed(4)
                            : "N/A"}
                        </div>
                        <div className="col-span-3">
                          {frame.is_fake ? (
                            <span className="inline-flex items-center text-destructive">
                              <AlertTriangle className="w-3 h-3 mr-1" />{" "}
                              Suspicious
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-green-500">
                              <CheckCircle className="w-3 h-3 mr-1" /> OK
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="lipsync" className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">
                    Lip Synchronization Analysis
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Analysis of audio-visual synchronization to detect potential
                    deepfakes.
                  </p>
                </div>

                {lip_sync_analysis?.error ? (
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm">
                      {lip_sync_analysis.description || lip_sync_analysis.error}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-muted">
                        <h4 className="text-sm font-medium mb-1">
                          Real Probability
                        </h4>
                        <div className="flex items-center">
                          {lip_sync_analysis && typeof lip_sync_analysis === "object" ? (
                            <>
                              <Progress
                                value={lip_sync_analysis.real_probability * 100}
                                className="h-2 flex-1 mr-2"
                              />
                              <span className="text-xs">
                                {Math.round(
                                  lip_sync_analysis.real_probability * 100
                                )}
                                %
                              </span>
                            </>
                          ) : (
                            <>
                              <Progress
                                value={
                                  typeof lip_sync_analysis === "number"
                                    ? lip_sync_analysis * 100
                                    : 0
                                }
                                className="h-2 flex-1 mr-2"
                              />
                              <span className="text-xs">
                                {typeof lip_sync_analysis === "number"
                                  ? Math.round(lip_sync_analysis * 100)
                                  : 0}
                                %
                              </span>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="p-4 rounded-lg bg-muted">
                        <h4 className="text-sm font-medium mb-1">
                          Fake Probability
                        </h4>
                        <div className="flex items-center">
                          {lip_sync_analysis && typeof lip_sync_analysis === "object" ? (
                            <>
                              <Progress
                                value={lip_sync_analysis.fake_probability * 100}
                                className="h-2 flex-1 mr-2"
                              />
                              <span className="text-xs">
                                {Math.round(
                                  lip_sync_analysis.fake_probability * 100
                                )}
                                %
                              </span>
                            </>
                          ) : (
                            <>
                              <Progress
                                value={
                                  typeof lip_sync_analysis === "number"
                                    ? (1 - lip_sync_analysis) * 100
                                    : 0
                                }
                                className="h-2 flex-1 mr-2"
                              />
                              <span className="text-xs">
                                {typeof lip_sync_analysis === "number"
                                  ? Math.round((1 - lip_sync_analysis) * 100)
                                  : 0}
                                %
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-muted">
                      <h4 className="text-sm font-medium mb-1">
                        Analysis Result
                      </h4>
                      <p className="text-sm">
                        {lip_sync_analysis && typeof lip_sync_analysis === "object"
                          ? lip_sync_analysis.description ||
                          (lip_sync_analysis.fake_probability > 0.5
                            ? "Potential lip sync mismatch detected, suggesting possible manipulation."
                            : "No significant lip sync issues detected.")
                          : typeof lip_sync_analysis === "number"
                            ? lip_sync_analysis < 0.5
                              ? "Potential lip sync mismatch detected, suggesting possible manipulation."
                              : "No significant lip sync issues detected."
                            : "Analysis unavailable"}
                      </p>
                    </div>

                    {lip_sync_analysis?.processing_time_seconds && (
                      <div className="p-4 rounded-lg bg-muted">
                        <h4 className="text-sm font-medium mb-1">
                          Processing Time
                        </h4>
                        <p className="text-sm">
                          {lip_sync_analysis.processing_time_seconds} seconds
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="technical" className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Technical Details</h3>
                  <p className="text-sm text-muted-foreground">
                    Technical metadata and analysis parameters used for
                    detection.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-muted space-y-2">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <span className="font-medium">Model Used:</span>
                    <span>Multi-Modal Deepfake Detector v2.1</span>

                    <span className="font-medium">Frame Sampling:</span>
                    <span>Every 10th frame</span>

                    <span className="font-medium">Resolution:</span>
                    <span>{video_analysis.resolution || "1920x1080"}</span>

                    <span className="font-medium">FPS:</span>
                    <span>{video_analysis.fps || "30"}</span>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto space-y-8"
        >
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              Deepfake Detection
            </h1>
            <p className="text-xl text-muted-foreground">
              Upload an image or video to analyze for AI manipulation using our
              advanced multi-modal detection models.
            </p>
          </div>

          <Card className="border-2 border-dashed">
            <CardContent className="p-0">
              {!file ? (
                <div
                  className={cn(
                    "flex flex-col items-center justify-center p-12 transition-colors cursor-pointer",
                    isDragging
                      ? "bg-primary/5 border-primary"
                      : "hover:bg-muted/50"
                  )}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                    <Upload className="w-10 h-10 text-primary" />
                  </div>
                  <h3 className="text-2xl font-semibold mb-2">Upload Media</h3>
                  <p className="text-muted-foreground mb-6 text-center max-w-md">
                    Drag and drop your image or video here, or click to browse.
                    Supports JPG, PNG, MP4, AVI.
                  </p>
                  <Button>Select File</Button>
                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="image/*,video/*"
                    onChange={handleFileChange}
                  />
                </div>
              ) : (
                <div className="p-8">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-lg bg-muted flex items-center justify-center overflow-hidden">
                        {file.type.startsWith("image/") ? (
                          preview ? (
                            <img
                              src={preview || "/placeholder.svg"}
                              alt="Preview"
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <FileImage className="w-8 h-8 text-muted-foreground" />
                          )
                        ) : (
                          <FileText className="w-8 h-8 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{file.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB •{" "}
                          {file.type}
                        </p>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={resetAnalysis}>
                      <X className="w-5 h-5" />
                    </Button>
                  </div>

                  {error && (
                    <div className="mb-6 p-4 rounded-lg bg-destructive/10 text-destructive flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      <p>{error}</p>
                    </div>
                  )}

                  {!results && !error && (
                    <div className="space-y-6">
                      {isAnalyzing ? (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Analyzing media...</span>
                            <span>{Math.round(analysisProgress)}%</span>
                          </div>
                          <Progress value={analysisProgress} className="h-2" />
                          <p className="text-xs text-muted-foreground text-center mt-4">
                            Running multi-modal analysis: artifacts, frequency,
                            noise patterns, and semantic consistency.
                          </p>
                        </div>
                      ) : (
                        <Button
                          className="w-full"
                          size="lg"
                          onClick={analyzeMedia}
                        >
                          <Search className="w-4 h-4 mr-2" />
                          Start Analysis
                        </Button>
                      )}
                    </div>
                  )}

                  {results && (
                    <div className="space-y-8">
                      {file.type.startsWith("video/") ? (
                        <VideoResultsDisplay />
                      ) : (
                        <div className="grid md:grid-cols-2 gap-8">
                          <div className="space-y-6">
                            <div className="relative aspect-square rounded-lg overflow-hidden border bg-muted">
                              {preview && (
                                <img
                                  src={preview || "/placeholder.svg"}
                                  alt="Analyzed Image"
                                  className="w-full h-full object-contain"
                                />
                              )}
                              {resultStatus && (
                                <div className="absolute top-4 right-4">
                                  <Badge
                                    variant={
                                      resultStatus === "fake"
                                        ? "destructive"
                                        : "default"
                                    }
                                    className="text-lg px-4 py-1"
                                  >
                                    {resultStatus === "fake" ? "FAKE" : "REAL"}
                                  </Badge>
                                </div>
                              )}
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <Card>
                                <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                                  <Gauge className="w-8 h-8 mb-2 text-primary" />
                                  <div className="text-2xl font-bold">
                                    {confidenceScore
                                      ? `${confidenceScore.toFixed(1)}%`
                                      : "N/A"}
                                  </div>
                                  <p className="text-xs text-muted-foreground">
                                    Confidence Score
                                  </p>
                                </CardContent>
                              </Card>
                              <Card>
                                <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                                  <Shield className="w-8 h-8 mb-2 text-primary" />
                                  <div className="text-2xl font-bold">High</div>
                                  <p className="text-xs text-muted-foreground">
                                    Analysis Depth
                                  </p>
                                </CardContent>
                              </Card>
                            </div>
                          </div>

                          <div className="space-y-6">
                            <div>
                              <h2 className="text-2xl font-bold mb-2">
                                Analysis Results
                              </h2>
                              <p className="text-muted-foreground">
                                {resultStatus === "fake"
                                  ? "Our multi-modal analysis has detected significant artifacts indicating this image is likely AI-generated or manipulated."
                                  : "Our analysis indicates this image is likely authentic. No significant manipulation artifacts were detected."}
                              </p>
                            </div>

                            <Tabs defaultValue="details">
                              <TabsList className="w-full">
                                <TabsTrigger value="details" className="flex-1">
                                  Details
                                </TabsTrigger>
                                <TabsTrigger value="xai" className="flex-1">
                                  Explainability
                                </TabsTrigger>
                                <TabsTrigger
                                  value="metadata"
                                  className="flex-1"
                                >
                                  Metadata
                                </TabsTrigger>
                              </TabsList>

                              <TabsContent
                                value="details"
                                className="space-y-4 mt-4"
                              >
                                <div className="space-y-4">
                                  {results.deepfake &&
                                    Array.isArray(results.deepfake) ? (
                                    results.deepfake.map(
                                      (item: any, idx: number) => (
                                        <div key={idx} className="space-y-2">
                                          <div className="flex justify-between text-sm">
                                            <span className="font-medium capitalize">
                                              {item.label} Probability
                                            </span>
                                            <span>
                                              {(item.score * 100).toFixed(1)}%
                                            </span>
                                          </div>
                                          <Progress
                                            value={item.score * 100}
                                            className="h-2"
                                          />
                                        </div>
                                      )
                                    )
                                  ) : (
                                    <div className="p-4 bg-muted rounded-lg text-sm text-muted-foreground">
                                      Detailed score breakdown unavailable
                                    </div>
                                  )}

                                  {/* SynthID Detection Display */}
                                  {results.synthid_detection && (
                                    <div className={cn(
                                      "p-4 rounded-lg border-2 space-y-2",
                                      results.synthid_detection.has_watermark
                                        ? "bg-amber-50 border-amber-500 dark:bg-amber-950/20"
                                        : "bg-muted border-border"
                                    )}>
                                      <div className="flex items-center gap-2">
                                        <Shield className={cn(
                                          "w-5 h-5",
                                          results.synthid_detection.has_watermark
                                            ? "text-amber-600"
                                            : "text-muted-foreground"
                                        )} />
                                        <h4 className="font-semibold text-sm">
                                          SynthID Detection
                                        </h4>
                                        {results.synthid_detection.has_watermark && (
                                          <Badge variant="outline" className="ml-auto bg-amber-500 text-white border-amber-600">
                                            Detected
                                          </Badge>
                                        )}
                                      </div>
                                      <p className="text-xs text-muted-foreground">
                                        {results.synthid_detection.has_watermark
                                          ? `Google's invisible SynthID watermark detected. This image was likely generated by ${results.synthid_detection.generation_method || 'Google AI'}.`
                                          : "No SynthID watermark detected. This image was not generated by Google's AI tools."}
                                      </p>
                                      {results.synthid_detection.has_watermark && (
                                        <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                                          <div>
                                            <span className="text-muted-foreground">Confidence:</span>
                                            <span className="ml-1 font-medium">
                                              {(results.synthid_detection.confidence * 100).toFixed(1)}%
                                            </span>
                                          </div>
                                          <div>
                                            <span className="text-muted-foreground">Strength:</span>
                                            <span className="ml-1 font-medium">
                                              {(results.synthid_detection.watermark_strength * 100).toFixed(1)}%
                                            </span>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  <div className="p-4 rounded-lg bg-muted space-y-2">
                                    <h4 className="font-medium text-sm">
                                      Technical Analysis
                                    </h4>
                                    <ul className="text-sm space-y-1 text-muted-foreground">
                                      <li>
                                        • Frequency domain analysis completed
                                      </li>
                                      <li>
                                        • Noise pattern consistency checked
                                      </li>
                                      <li>
                                        • Compression artifact inspection done
                                      </li>
                                      <li>• Semantic consistency verified</li>
                                      {results.synthid_detection && (
                                        <li className={cn(
                                          results.synthid_detection.has_watermark
                                            ? "text-amber-600 font-medium"
                                            : ""
                                        )}>
                                          • SynthID watermark scan: {results.synthid_detection.has_watermark ? "✓ Detected" : "Not found"}
                                        </li>
                                      )}
                                    </ul>
                                  </div>
                                </div>
                              </TabsContent>

                              <TabsContent value="xai" className="mt-4">
                                {results.xai_explanations ? (
                                  <div className="space-y-4">
                                    <p className="text-sm text-muted-foreground">
                                      Heatmaps highlight areas that influenced
                                      the AI's decision. Red areas indicate
                                      strong indicators of manipulation.
                                    </p>
                                    <div className="grid grid-cols-2 gap-4">
                                      {Object.entries(
                                        results.xai_explanations
                                      ).map(([method, data]: [string, any]) => {
                                        if (
                                          method === "prediction" ||
                                          method === "error"
                                        )
                                          return null;

                                        // Handle data structure from XAIExplainer
                                        let imageUrl = "";
                                        if (typeof data === "object" && data !== null) {
                                          // Prefer overlay if available, otherwise saliency
                                          if (data.overlay) imageUrl = data.overlay;
                                          else if (data.saliency) imageUrl = data.saliency;
                                          else if (data.visualization) imageUrl = data.visualization.startsWith("data:") ? data.visualization : `data:image/png;base64,${data.visualization}`;
                                        } else if (typeof data === "string") {
                                          // Handle raw base64 string
                                          imageUrl = data.startsWith("data:") ? data : `data:image/png;base64,${data}`;
                                        }

                                        if (!imageUrl) return null;

                                        return (
                                          <div
                                            key={method}
                                            className="space-y-2"
                                          >
                                            <div className="aspect-square rounded-lg overflow-hidden border bg-muted relative group">
                                              <img
                                                src={imageUrl}
                                                alt={`${method} Heatmap`}
                                                className="w-full h-full object-cover"
                                              />
                                              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                <Button
                                                  variant="secondary"
                                                  size="sm"
                                                >
                                                  View Full
                                                </Button>
                                              </div>
                                            </div>
                                            <p className="text-xs text-center font-medium">
                                              {method}
                                            </p>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="flex flex-col items-center justify-center p-8 text-center space-y-4 border-2 border-dashed rounded-lg">
                                    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                                      <Search className="w-6 h-6 text-muted-foreground" />
                                    </div>
                                    <div>
                                      <h4 className="font-medium">
                                        No Explanations Available
                                      </h4>
                                      <p className="text-sm text-muted-foreground">
                                        XAI analysis was not enabled or failed
                                        for this image.
                                      </p>
                                    </div>
                                  </div>
                                )}
                              </TabsContent>

                              <TabsContent value="metadata" className="mt-4">
                                <div className="space-y-4">
                                  {results.c2pa_verification?.has_c2pa ? (
                                    <div className="space-y-4">
                                      {/* Status Banner */}
                                      {results.c2pa_verification.deep_scan_detected ? (
                                        <div className="flex items-center gap-2 p-3 bg-amber-500/10 text-amber-600 rounded-lg border border-amber-200 dark:border-amber-800">
                                          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                                          <div>
                                            <span className="font-medium block">Hidden/Corrupted C2PA Detected</span>
                                            <span className="text-xs opacity-90">Deep scan found traces of C2PA data, but it appears corrupted or stripped.</span>
                                          </div>
                                        </div>
                                      ) : results.c2pa_verification.verified ? (
                                        <div className="flex items-center gap-2 p-3 bg-green-500/10 text-green-600 rounded-lg border border-green-200 dark:border-green-800">
                                          <CheckCircle className="w-5 h-5" />
                                          <span className="font-medium">C2PA Signature Verified</span>
                                        </div>
                                      ) : (
                                        <div className="flex items-center gap-2 p-3 bg-red-500/10 text-red-600 rounded-lg border border-red-200 dark:border-red-800">
                                          <X className="w-5 h-5 flex-shrink-0" />
                                          <div>
                                            <span className="font-medium block">C2PA Verification Failed</span>
                                            <span className="text-xs opacity-90">Signature invalid or chain of custody broken.</span>
                                          </div>
                                        </div>
                                      )}

                                      <Accordion
                                        type="single"
                                        collapsible
                                        className="w-full"
                                      >
                                        <AccordionItem value="manifest">
                                          <AccordionTrigger>
                                            Manifest Information
                                          </AccordionTrigger>
                                          <AccordionContent>
                                            <div className="space-y-2 text-sm">
                                              <div className="grid grid-cols-3 gap-2">
                                                <span className="font-medium text-muted-foreground">
                                                  Title:
                                                </span>
                                                <span className="col-span-2">
                                                  {results.c2pa_verification
                                                    .manifest?.title || "N/A"}
                                                </span>
                                              </div>
                                              <div className="grid grid-cols-3 gap-2">
                                                <span className="font-medium text-muted-foreground">
                                                  Format:
                                                </span>
                                                <span className="col-span-2">
                                                  {results.c2pa_verification
                                                    .manifest?.format || "N/A"}
                                                </span>
                                              </div>
                                              <div className="grid grid-cols-3 gap-2">
                                                <span className="font-medium text-muted-foreground">
                                                  Instance ID:
                                                </span>
                                                <span className="col-span-2 break-all font-mono text-xs">
                                                  {results.c2pa_verification
                                                    .manifest?.instance_id ||
                                                    "N/A"}
                                                </span>
                                              </div>
                                            </div>
                                          </AccordionContent>
                                        </AccordionItem>

                                        <AccordionItem value="signature">
                                          <AccordionTrigger>
                                            Signature Details
                                          </AccordionTrigger>
                                          <AccordionContent>
                                            <div className="space-y-2 text-sm">
                                              <div className="grid grid-cols-3 gap-2">
                                                <span className="font-medium text-muted-foreground">
                                                  Issuer:
                                                </span>
                                                <span className="col-span-2">
                                                  {results.c2pa_verification
                                                    .signature?.issuer || "N/A"}
                                                </span>
                                              </div>
                                              <div className="grid grid-cols-3 gap-2">
                                                <span className="font-medium text-muted-foreground">
                                                  Date:
                                                </span>
                                                <span className="col-span-2">
                                                  {results.c2pa_verification
                                                    .signature?.time || "N/A"}
                                                </span>
                                              </div>
                                            </div>
                                          </AccordionContent>
                                        </AccordionItem>

                                        <AccordionItem value="raw">
                                          <AccordionTrigger>
                                            Raw Data
                                          </AccordionTrigger>
                                          <AccordionContent>
                                            <pre className="bg-muted p-4 rounded-lg overflow-auto text-xs max-h-[200px]">
                                              {JSON.stringify(
                                                results.c2pa_verification,
                                                null,
                                                2
                                              )}
                                            </pre>
                                          </AccordionContent>
                                        </AccordionItem>
                                      </Accordion>
                                    </div>
                                  ) : (
                                    <div className="flex flex-col items-center justify-center p-8 text-center space-y-4 border-2 border-dashed rounded-lg">
                                      <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                                        <FileWarning className="w-6 h-6 text-muted-foreground" />
                                      </div>
                                      <div>
                                        <h4 className="font-medium">
                                          No C2PA Metadata
                                        </h4>
                                        <p className="text-sm text-muted-foreground">
                                          This image does not contain Content
                                          Credentials or digital signature data.
                                        </p>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </TabsContent>
                            </Tabs>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
