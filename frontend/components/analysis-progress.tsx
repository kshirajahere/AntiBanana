"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";

export interface AnalysisStep {
  id: string;
  label: string;
  description?: string;
}

interface AnalysisProgressProps {
  steps: AnalysisStep[];
  currentStepIndex: number;
  progress: number;
  isComplete?: boolean;
  title?: string;
  description?: string;
}

export function AnalysisProgress({
  steps,
  currentStepIndex,
  progress,
  isComplete = false,
  title = "Analyzing...",
  description = "Please wait while we process your file.",
}: AnalysisProgressProps) {
  return (
    <div className="w-full space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold tracking-tight flex items-center justify-center gap-2">
          {isComplete ? (
            <CheckCircle2 className="h-6 w-6 text-green-500" />
          ) : (
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          )}
          {title}
        </h3>
        <p className="text-muted-foreground">{description}</p>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => {
          const isCompleted = index < currentStepIndex || isComplete;
          const isCurrent = index === currentStepIndex && !isComplete;
          const isPending = index > currentStepIndex;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "flex items-center gap-4 rounded-lg border p-4 transition-colors",
                isCurrent
                  ? "bg-primary/5 border-primary/50"
                  : "bg-card border-border",
                isCompleted ? "bg-muted/30" : ""
              )}
            >
              <div className="flex-shrink-0">
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500/10 text-green-500"
                  >
                    <CheckCircle2 className="h-5 w-5" />
                  </motion.div>
                ) : isCurrent ? (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary relative">
                    <Loader2 className="h-5 w-5 animate-spin absolute" />
                  </div>
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground">
                    <Circle className="h-5 w-5" />
                  </div>
                )}
              </div>
              <div className="flex-1">
                <h4
                  className={cn(
                    "font-medium text-sm",
                    isCompleted
                      ? "text-muted-foreground"
                      : isCurrent
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {step.label}
                </h4>
                {step.description && isCurrent && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="text-xs text-muted-foreground mt-1"
                  >
                    {step.description}
                  </motion.p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
