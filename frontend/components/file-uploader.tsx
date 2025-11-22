"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  acceptedFileTypes?: {
    [key: string]: string[];
  };
  maxSize?: number; // in MB
  label?: string;
  description?: string;
  disabled?: boolean;
}

export function FileUploader({
  onFileSelect,
  acceptedFileTypes = {
    "image/*": [".jpg", ".jpeg", ".png", ".webp"],
    "video/*": [".mp4", ".avi", ".mov", ".webm"],
  },
  maxSize = 100,
  label = "Drag and drop your file here",
  description = "Support for images and videos",
  disabled = false,
}: FileUploaderProps) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const validateAndSelectFile = (file: File) => {
    setError(null);

    // Check file size
    if (file.size > maxSize * 1024 * 1024) {
      setError(`File size exceeds ${maxSize}MB limit`);
      return;
    }

    // Check file type
    const fileType = file.type;
    const isAccepted = Object.keys(acceptedFileTypes).some((type) => {
      if (type.endsWith("/*")) {
        const baseType = type.split("/")[0];
        return fileType.startsWith(`${baseType}/`);
      }
      return type === fileType;
    });

    if (!isAccepted) {
      setError("File type not supported");
      return;
    }

    onFileSelect(file);
  };

  const triggerFileInput = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="w-full">
      <motion.div
        className={cn(
          "relative overflow-hidden rounded-xl border-2 border-dashed transition-all duration-300",
          isDragging
            ? "border-primary bg-primary/5 scale-[1.01] shadow-lg shadow-primary/10"
            : "border-muted-foreground/25 bg-card hover:bg-accent/5",
          disabled && "opacity-50 cursor-not-allowed",
          error && "border-destructive/50 bg-destructive/5"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={triggerFileInput}
      >
        <div className="flex flex-col items-center justify-center p-10 text-center cursor-pointer">
          <input
            type="file"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept={Object.values(acceptedFileTypes).flat().join(",")}
            disabled={disabled}
          />

          <motion.div
            className={cn(
              "mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10",
              isDragging && "scale-110 bg-primary/20"
            )}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Upload className="h-10 w-10 text-primary" />
          </motion.div>

          <h3 className="mb-2 text-xl font-semibold tracking-tight">
            {isDragging ? "Drop it like it's hot!" : label}
          </h3>

          <p className="mb-6 text-sm text-muted-foreground max-w-xs mx-auto">
            {description}
          </p>

          <Button
            variant={isDragging ? "default" : "secondary"}
            disabled={disabled}
          >
            Select File
          </Button>
        </div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-4 left-0 right-0 mx-auto w-fit rounded-full bg-destructive/90 px-4 py-1 text-xs text-white flex items-center gap-2"
            >
              <X className="h-3 w-3" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
