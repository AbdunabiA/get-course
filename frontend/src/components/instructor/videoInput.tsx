// frontend/src/components/instructor/VideoInput.tsx
"use client";

import { useState } from "react";
import { Link as LinkIcon, X, CheckCircle, AlertCircle } from "lucide-react";

interface VideoInputProps {
  value?: string;
  onChange: (url: string) => void;
  label?: string;
}

export function VideoInput({
  value,
  onChange,
  label = "Video",
}: VideoInputProps) {
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string>("");

  const validateUrl = (url: string) => {
    // Simple client-side validation
    const youtubePattern =
      /(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)/;
    const vimeoPattern = /(vimeo\.com\/|player\.vimeo\.com\/video\/)/;

    return youtubePattern.test(url) || vimeoPattern.test(url);
  };

  const handleUrlChange = (url: string) => {
    onChange(url);

    if (url && !validateUrl(url)) {
      setValidationError("Please enter a valid YouTube or Vimeo URL");
    } else {
      setValidationError("");
    }
  };

  const getEmbedUrl = (url: string) => {
    // Convert regular YouTube URL to embed URL
    if (url.includes("youtube.com/watch?v=")) {
      const videoId = url.split("watch?v=")[1]?.split("&")[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    if (url.includes("youtu.be/")) {
      const videoId = url.split("youtu.be/")[1]?.split("?")[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }

    // Convert regular Vimeo URL to embed URL
    if (url.includes("vimeo.com/")) {
      const videoId = url.match(/vimeo\.com\/(\d+)/)?.[1];
      return `https://player.vimeo.com/video/${videoId}`;
    }

    return url;
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700">{label}</label>

      <div className="space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="url"
              value={value || ""}
              onChange={(e) => handleUrlChange(e.target.value)}
              placeholder="https://youtube.com/watch?v=... or https://vimeo.com/..."
              className={`w-full pl-10 pr-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                validationError ? "border-red-300" : "border-gray-300"
              }`}
            />
          </div>
          {value && (
            <button
              type="button"
              onClick={() => {
                onChange("");
                setValidationError("");
              }}
              className="px-3 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {validationError && (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="h-4 w-4" />
            {validationError}
          </div>
        )}

        {value && !validationError && (
          <div className="flex items-center gap-2 text-sm text-green-600">
            <CheckCircle className="h-4 w-4" />
            Valid video URL
          </div>
        )}

        <p className="text-sm text-gray-500">
          Supported platforms: YouTube and Vimeo
        </p>
      </div>

      {/* Video Preview */}
      {value && !validationError && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
          <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
            <iframe
              src={getEmbedUrl(value)}
              className="absolute top-0 left-0 w-full h-full rounded-lg"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </div>
      )}
    </div>
  );
}
