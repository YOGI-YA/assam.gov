'use client';

import React, { useState } from 'react';
import {
  FileText, ExternalLink, ChevronLeft, ChevronRight,
  ZoomIn, ZoomOut, Maximize2, ShieldCheck, Database,
  Layers, CheckCircle2, Bookmark
} from 'lucide-react';
import { PdfBadge } from '@/components/ui/PdfBadge';
import { CitationItem } from '@/types';
import { api } from '@/lib/api';

interface SourcePreviewPanelProps {
  citation: CitationItem | null;
  onClose?: () => void;
  onBackToChat?: () => void;
}

export const SourcePreviewPanel: React.FC<SourcePreviewPanelProps> = ({ citation, onBackToChat }) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoomLevel, setZoomLevel] = useState<number>(100);

  // If citation is active, determine metadata
  const totalPages = citation?.total_pages || (citation?.page_number && citation.page_number > 20 ? 63 : 12);
  const pageNum = citation?.page_number || currentPage;
  const docName = citation?.document_name || '';
  const pdfUrl = citation?.document_id ? api.getDocumentFileUrl(citation.document_id, pageNum) : '#';

  const handlePrevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  // EMPTY STATE when no document is active
  if (!citation) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-3.5 sm:p-4 shadow-xs flex flex-col h-full min-h-0 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between mb-3 shrink-0">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm sm:text-base">
            <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-slate-800" strokeWidth={1.8} />
            <span>Source Document</span>
          </div>
          {onBackToChat && (
            <button
              type="button"
              onClick={onBackToChat}
              className="lg:hidden text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 px-2.5 py-1 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Back to Chat</span>
            </button>
          )}
        </div>

        {/* Empty State Presentation */}
        <div className="flex-1 overflow-y-auto min-h-0 border border-dashed border-slate-200 rounded-xl p-4 sm:p-5 flex flex-col items-center justify-center text-center bg-slate-50/50">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-700 mb-3 shadow-2xs">
            <Bookmark className="w-6 h-6 text-blue-600" />
          </div>

          <h3 className="text-sm font-bold text-slate-800 mb-1">
            Source Document Preview
          </h3>
          <p className="text-xs text-slate-500 max-w-xs leading-relaxed mb-5">
            Submit a query or click any suggested prompt to view verified source citations, exact page numbers, and highlighted clauses.
          </p>

          {/* Indexed Repositories List */}
          <div className="w-full bg-white rounded-xl border border-slate-200 p-3.5 text-left shadow-2xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold text-slate-900 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-blue-600" />
                Indexed Knowledge Base
              </span>
              <span className="bg-emerald-50 text-emerald-700 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-emerald-200">
                8 Sources Ready
              </span>
            </div>

            <div className="space-y-1.5 text-[11px] text-slate-600">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>NESFIC 2026 Guidelines (uspr.pdf)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>ASDMA Flood Hazard Atlas & NESDR</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>ISRO Bhuvan, VEDAS & MOSDAC Data</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Assam State Geoportal & Data.gov.in</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Assam Pension Rules & Secretariat Manual</span>
              </div>
            </div>

            <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center gap-1.5 text-[10px] text-slate-500">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Departmental PDFs uploaded in Documents are automatically indexed.</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ACTIVE CITATION PRESENTATION
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-3.5 sm:p-4 shadow-xs flex flex-col h-full min-h-0 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 sm:mb-4 shrink-0">
        <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm sm:text-base">
          <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-slate-800" strokeWidth={1.8} />
          <span>Source Document</span>
        </div>
        {onBackToChat && (
          <button
            type="button"
            onClick={onBackToChat}
            className="lg:hidden text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 px-2.5 py-1 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Back to Chat</span>
          </button>
        )}
      </div>

      {/* Active Document Info Card */}
      <div className="border border-slate-200 rounded-xl p-3 flex items-center justify-between bg-white shadow-2xs mb-3 shrink-0">
        <div className="flex items-center space-x-3 truncate">
          <PdfBadge className="w-6 h-7 shrink-0" />
          <div className="truncate">
            <h4 className="text-xs font-bold text-slate-900 truncate" title={docName}>
              {docName}
            </h4>
            <p className="text-[11px] text-slate-500 font-normal mt-0.5">
              Page {pageNum} of {totalPages}
            </p>
          </div>
        </div>

        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          title="Open in new window"
          className="text-slate-500 hover:text-slate-900 p-1 rounded transition-colors"
        >
          <ExternalLink className="w-4 h-4" strokeWidth={1.8} />
        </a>
      </div>

      {/* PDF Page Navigation & Zoom Toolbar */}
      <div className="flex items-center justify-between py-1.5 px-2 text-slate-600 text-xs mb-3 shrink-0">
        {/* Page Nav */}
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={handlePrevPage}
            className="p-1 hover:bg-slate-100 rounded text-slate-700 transition-colors"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-medium text-slate-800 text-xs tracking-wide">
            {pageNum} &nbsp;/&nbsp; {totalPages}
          </span>
          <button
            type="button"
            onClick={handleNextPage}
            className="p-1 hover:bg-slate-100 rounded text-slate-700 transition-colors"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-3 text-slate-600">
          <button
            type="button"
            onClick={() => setZoomLevel(prev => Math.min(prev + 10, 150))}
            className="p-1 hover:bg-slate-100 rounded transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setZoomLevel(prev => Math.max(prev - 10, 70))}
            className="p-1 hover:bg-slate-100 rounded transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="p-1 hover:bg-slate-100 rounded transition-colors"
            title="Fullscreen / Expand"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* High-Fidelity Rendered PDF Page Sheet */}
      <div className="flex-1 min-h-0 bg-slate-100/70 p-3 rounded-xl flex items-center justify-center overflow-auto">
        <div
          className="bg-white border border-slate-200/90 rounded-lg shadow-md w-full max-w-[340px] p-6 text-slate-800 text-xs leading-relaxed transition-transform duration-150"
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
        >
          {/* Document Section / Header */}
          <div className="border-b border-slate-100 pb-2 mb-3 text-center">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
              Official Gazetted Excerpt
            </span>
            <h3 className="font-bold text-slate-900 text-xs mt-0.5 line-clamp-1">
              {docName.replace('.pdf', '').replace(/_/g, ' ')}
            </h3>
          </div>

          {/* Yellow Highlighted Clause matching screenshot */}
          <div className="bg-[#fef08a] px-2.5 py-2 rounded-xs font-semibold text-[11px] text-slate-900 leading-snug mb-3 shadow-2xs">
            {citation.excerpt}
          </div>

          {/* Verified Citation Footer */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
            <span>Citation ID: {citation.citation_id}</span>
            <span>Relevance: {Math.round(citation.similarity_score * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
