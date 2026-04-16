"use client";

import { getImageUrl } from "@/lib/api";
import { useState } from "react";

interface ImageGalleryProps {
  pageImageUrls: string[];
  embeddedImageUrls: string[];
  embeddedImages: { filename: string; page: number; width: number; height: number }[];
}

export default function ImageGallery({ pageImageUrls, embeddedImageUrls, embeddedImages }: ImageGalleryProps) {
  const [activeTab, setActiveTab] = useState<"pages" | "embedded">("pages");
  const [lightbox, setLightbox] = useState<string | null>(null);

  const hasPages = pageImageUrls && pageImageUrls.length > 0;
  const hasEmbedded = embeddedImageUrls && embeddedImageUrls.length > 0;

  if (!hasPages && !hasEmbedded) {
    return (
      <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500/30 to-pink-500/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-white/90">Extracted Images</h3>
        </div>
        <p className="text-sm text-white/40">No images available.</p>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500/30 to-pink-500/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
              </svg>
            </div>
            <h3 className="text-base font-semibold text-white/90">Extracted Images</h3>
          </div>
          <div className="flex gap-1">
            {hasPages && (
              <button
                onClick={() => setActiveTab("pages")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "pages"
                    ? "bg-purple-500/30 text-purple-300"
                    : "bg-white/5 text-white/40 hover:bg-white/10"
                }`}
              >
                Pages ({pageImageUrls.length})
              </button>
            )}
            {hasEmbedded && (
              <button
                onClick={() => setActiveTab("embedded")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  activeTab === "embedded"
                    ? "bg-purple-500/30 text-purple-300"
                    : "bg-white/5 text-white/40 hover:bg-white/10"
                }`}
              >
                Embedded ({embeddedImageUrls.length})
              </button>
            )}
          </div>
        </div>

        {/* Image Grid */}
        <div className="p-4 grid grid-cols-2 md:grid-cols-3 gap-3">
          {activeTab === "pages" &&
            pageImageUrls.map((url, i) => (
              <div
                key={i}
                className="group relative aspect-[3/4] rounded-xl overflow-hidden bg-white/5 border border-white/10 cursor-pointer hover:border-purple-400/50 transition-all"
                onClick={() => setLightbox(getImageUrl(url))}
              >
                <img
                  src={getImageUrl(url)}
                  alt={`Page ${i + 1}`}
                  className="w-full h-full object-contain"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="absolute bottom-2 left-2 text-xs text-white/80 bg-black/50 px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                  Page {i + 1}
                </span>
              </div>
            ))}
          {activeTab === "embedded" &&
            embeddedImageUrls.map((url, i) => (
              <div
                key={i}
                className="group relative aspect-square rounded-xl overflow-hidden bg-white/5 border border-white/10 cursor-pointer hover:border-purple-400/50 transition-all"
                onClick={() => setLightbox(getImageUrl(url))}
              >
                <img
                  src={getImageUrl(url)}
                  alt={embeddedImages[i]?.filename || `Image ${i + 1}`}
                  className="w-full h-full object-contain"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="absolute bottom-2 left-2 text-xs text-white/80 bg-black/50 px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                  {embeddedImages[i] ? `Page ${embeddedImages[i].page}` : `Image ${i + 1}`}
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-8"
          onClick={() => setLightbox(null)}
        >
          <button
            className="absolute top-6 right-6 text-white/60 hover:text-white text-3xl"
            onClick={() => setLightbox(null)}
          >
            ✕
          </button>
          <img
            src={lightbox}
            alt="Full size"
            className="max-w-full max-h-full object-contain rounded-xl"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
