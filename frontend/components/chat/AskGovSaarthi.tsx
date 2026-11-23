'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Paperclip, Send, User, Landmark, Sparkles, 
  FileText, ArrowRight, Loader2, BookOpen, Layers,
  Upload, X, CheckCircle2, FileUp, RotateCcw,
  CornerDownRight, ChevronRight, MessageSquare
} from 'lucide-react';
import { PdfBadge } from '@/components/ui/PdfBadge';
import { AssamEmblem } from '@/components/ui/AssamEmblem';
import { SourcePreviewPanel } from './SourcePreviewPanel';
import { CitationItem, DocumentItem } from '@/types';
import { api } from '@/lib/api';

interface SourceDocItem {
  id: string;
  name: string;
  page: number;
  total_pages: number;
  subtitle: string;
  excerpt: string;
}

const SUGGESTED_PROMPTS = [
  {
    category: 'NESFIC 2026 Public Resources',
    title: 'Portal Data & Geospatial Resources',
    query: 'What public resources, open data portals, and geospatial platforms are available on the NESFIC 2026 portal for challenge candidates?',
    sourceLabel: 'Data.gov.in, Bhuvan, VEDAS, MOSDAC, Survey of India, Geoportal, NESDR, DES & ASDMA'
  },
  {
    category: 'NESFIC 2026 Challenge Guidelines',
    title: 'Uniform Proposal Requirements (USPR)',
    query: 'What are the mandatory proposal components and evaluation dimensions under the NESFIC 2026 Uniform Solution Proposal Requirements (USPR)?',
    sourceLabel: 'startup.assam.gov.in/nesfic26/docs/uspr.pdf'
  },
  {
    category: 'Earth Observation & State Mapping',
    title: 'Satellite Data & State Geoportal',
    query: 'What satellite imagery, climate data, and spatial planning layers are hosted on Bhuvan, VEDAS, MOSDAC, and the Assam State Geoportal?',
    sourceLabel: 'ISRO Bhuvan, SAC VEDAS, MOSDAC & Directorate of Town & Country Planning'
  },
  {
    category: 'Disaster Response & Relief SOP',
    title: 'ASDMA Citizens SOP & SDRF Norms',
    query: 'What immediate actions should citizens take during a disaster, and what are the SDRF relief norms and 3-tier DDMA verification steps?',
    sourceLabel: 'ASDMA Disaster Response SOP & SDRF Manual (Notifications 2023/45 & 2024/08)'
  }
];

const FOLLOW_UP_SUGGESTIONS: Record<string, string[]> = {
  default: [
    'What scale does Survey of India provide maps in?',
    'What datasets can candidates access from Data.gov.in and Geospatial Data Catalogue?',
    'What statistical surveys are published by the Directorate of Economics and Statistics (DES)?'
  ],
  pension: [
    'What is the timeline under Circular No. 142 for submitting pension papers?',
    'Who is the competent sanctioning authority for pension cases?',
    'What are the guidelines in the Pension Processing Office Memorandum?'
  ],
  disaster: [
    'What are the approved relief rates for housing assistance and ex-gratia?',
    'What is the 3-tier DDMA verification procedure for SDRF claims?',
    'What documents are required to submit an SDRF relief claim?'
  ],
  nesfic: [
    'What are the evaluation criteria and assessment dimensions in USPR?',
    'What are the data and geospatial requirements under Section 7 of USPR?',
    'What datasets can candidates access from Data.gov.in and Geospatial Data Catalogue?'
  ],
  geospatial: [
    'What scale does Survey of India provide maps in?',
    'What layers are available on the North Eastern Spatial Data Repository (NESDR) Assam?',
    'What environmental applications and indices does VEDAS provide for Assam?'
  ]
};

export const AskGovSaarthi: React.FC = () => {
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [mobileTab, setMobileTab] = useState<'chat' | 'source'>('chat');

  // PDF Attachment & Upload States
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const [uploadingFileName, setUploadingFileName] = useState('');
  const [attachedDoc, setAttachedDoc] = useState<DocumentItem | null>(null);

  // Messages stream
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'assistant';
    content?: string;
    timestamp?: string;
    sources?: SourceDocItem[];
  }>>([]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleNewChat = () => {
    setMessages([]);
    setActiveCitation(null);
    setAttachedDoc(null);
    setConversationId(undefined);
    setInputQuery('');
  };

  const handlePaperclipClick = () => {
    if (uploadingPdf) return;
    fileInputRef.current?.click();
  };

  const handleFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Only PDF documents (.pdf) are permitted.');
      e.target.value = '';
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      alert('File size exceeds the maximum 25MB limit.');
      e.target.value = '';
      return;
    }

    setUploadingPdf(true);
    setUploadingFileName(file.name);

    try {
      const doc = await api.uploadDocument(file, 'General Documents', 'Officer Uploaded Document');
      setAttachedDoc(doc);

      const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      setMessages(prev => [
        ...prev,
        {
          id: `asst-upload-${Date.now()}`,
          role: 'assistant',
          content: `Based on the verified official records retrieved for your query:

- Document **${doc.filename}** (${doc.page_count} ${doc.page_count === 1 ? 'page' : 'pages'}) has been successfully uploaded, extracted, and indexed with vector embeddings into the knowledge base. **[Source: ${doc.filename}, Page 1 (CIT-UPLOAD)]**

*All factual statements above are traceable to the source citations displayed in the right-hand panel.*`,
          timestamp: currentTime,
          sources: [
            {
              id: 'CIT-UPLOAD',
              name: doc.filename,
              page: 1,
              total_pages: doc.page_count || 1,
              subtitle: `Page 1 • ${doc.filename.replace('.pdf', '')}`,
              excerpt: `Document ${doc.filename} (${doc.page_count} pages) successfully parsed and indexed for verified retrieval.`
            }
          ]
        }
      ]);

      setActiveCitation({
        citation_id: 'CIT-UPLOAD',
        document_id: doc.id,
        document_name: doc.filename,
        page_number: 1,
        total_pages: doc.page_count || 1,
        excerpt: `Uploaded Document: ${doc.filename} (${doc.page_count} pages). Extracted and indexed into the vector database.`,
        similarity_score: 1.0
      });

    } catch (err: any) {
      alert(`Upload failed: ${err.message || 'Error uploading document'}`);
    } finally {
      setUploadingPdf(false);
      setUploadingFileName('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const executeQuery = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed || loading) return;

    setInputQuery('');
    setLoading(true);

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Add user message
    setMessages(prev => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        role: 'user',
        content: trimmed,
        timestamp: currentTime
      }
    ]);

    try {
      const docFilterId = attachedDoc ? attachedDoc.id : undefined;
      const res = await api.askQuestion(trimmed, conversationId, docFilterId);

      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }

      const mappedSources: SourceDocItem[] = (res.citations && res.citations.length > 0)
        ? res.citations.map((c, i) => ({
            id: c.citation_id || `CIT-${i + 1}`,
            name: c.document_name,
            page: c.page_number,
            total_pages: c.total_pages || (c.page_number > 20 ? 63 : 12),
            subtitle: `Page ${c.page_number} • ${c.document_name.replace('.pdf', '')}`,
            excerpt: c.excerpt
          }))
        : [];

      if (res.citations && res.citations.length > 0) {
        setActiveCitation({
          ...res.citations[0],
          total_pages: res.citations[0].total_pages || (res.citations[0].page_number > 20 ? 63 : 12)
        });
      }

      setMessages(prev => [
        ...prev,
        {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: res.answer,
          sources: mappedSources
        }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: `asst-err-${Date.now()}`,
          role: 'assistant',
          content: 'Unable to connect to the backend server. Please verify backend connection on port 8000.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    await executeQuery(inputQuery);
  };

  const handleSelectSource = (src: SourceDocItem) => {
    setActiveCitation({
      citation_id: src.id,
      document_id: src.id,
      document_name: src.name,
      page_number: src.page,
      total_pages: src.total_pages,
      excerpt: src.excerpt,
      similarity_score: 0.95
    });
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      setMobileTab('source');
    }
  };

  const getFollowUpList = () => {
    const lastUserMsg = messages.filter(m => m.role === 'user').slice(-1)[0]?.content?.toLowerCase() || '';
    if (lastUserMsg.includes('pension') || lastUserMsg.includes('superannuation') || lastUserMsg.includes('service book')) return FOLLOW_UP_SUGGESTIONS.pension;
    if (lastUserMsg.includes('disaster') || lastUserMsg.includes('flood') || lastUserMsg.includes('relief') || lastUserMsg.includes('housing') || lastUserMsg.includes('aid') || lastUserMsg.includes('sdrf') || lastUserMsg.includes('asdma') || lastUserMsg.includes('gratuitous')) return FOLLOW_UP_SUGGESTIONS.disaster;
    if (lastUserMsg.includes('uspr') || lastUserMsg.includes('proposal') || lastUserMsg.includes('nesfic')) return FOLLOW_UP_SUGGESTIONS.nesfic;
    if (lastUserMsg.includes('geo') || lastUserMsg.includes('bhuvan') || lastUserMsg.includes('map') || lastUserMsg.includes('satellite') || lastUserMsg.includes('assac')) return FOLLOW_UP_SUGGESTIONS.geospatial;
    return FOLLOW_UP_SUGGESTIONS.default;
  };

  const renderInlineFormatted = (rawText: string, currentSources?: SourceDocItem[]) => {
    // 1. Extract source citation if present
    const sourceMatch = rawText.match(/(\*\*\[Source:\s*([^,\]]+),\s*Page\s*(\d+)(?:\s*\(([^)]+)\))?\]\s*\*\*|\[Source:\s*([^,\]]+),\s*Page\s*(\d+)(?:\s*\(([^)]+)\))?\])/i);
    let textToFormat = rawText;
    let sourceElement: React.ReactNode = null;

    if (sourceMatch && sourceMatch.index !== undefined) {
      textToFormat = rawText.substring(0, sourceMatch.index);
      const docRaw = sourceMatch[2] || sourceMatch[5] || '';
      const pageStr = sourceMatch[3] || sourceMatch[6] || '1';
      const citId = sourceMatch[4] || sourceMatch[7] || '';
      const docClean = docRaw.trim().replace(/\.pdf$/i, '');
      const pageNum = parseInt(pageStr, 10) || 1;

      sourceElement = (
        <span
          key={`src-${docClean}-${pageNum}`}
          onClick={(e) => {
            e.stopPropagation();
            if (currentSources && currentSources.length > 0) {
              const matched = currentSources.find(
                s => (citId && s.id === citId) || (s.name.toLowerCase().includes(docClean.toLowerCase()) && s.page === pageNum)
              ) || currentSources.find(s => s.name.toLowerCase().includes(docClean.toLowerCase()));
              if (matched) {
                handleSelectSource(matched);
              }
            }
          }}
          className="inline-flex items-center gap-1 font-semibold text-blue-900 bg-blue-50/90 hover:bg-blue-100 text-[11px] px-2 py-0.5 rounded-md cursor-pointer border border-blue-200/80 transition-colors ml-1.5 shadow-3xs"
          title={`Click to view ${docClean} (Page ${pageNum}) in preview panel`}
        >
          <FileText className="w-3 h-3 text-blue-600 shrink-0" />
          <span>{docClean} · P.{pageNum}</span>
        </span>
      );
    }

    // 2. Clean unmatched stray asterisks
    let clean = textToFormat.trim();
    const dblAsteriskCount = (clean.match(/\*\*/g) || []).length;
    if (dblAsteriskCount % 2 !== 0) {
      clean = clean.replace(/\*\*/g, '');
    }

    // 3. Tokenize by **bold**, `code`, *italic*
    const parts: React.ReactNode[] = [];
    const tokenRegex = /(\*\*.*?\*\*|`.*?`|\*.*?\*)/g;
    let lastIdx = 0;
    let match: RegExpExecArray | null;

    while ((match = tokenRegex.exec(clean)) !== null) {
      if (match.index > lastIdx) {
        parts.push(clean.substring(lastIdx, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
        parts.push(
          <strong key={`b-${match.index}`} className="font-semibold text-slate-950">
            {token.slice(2, -2)}
          </strong>
        );
      } else if (token.startsWith('`') && token.endsWith('`') && token.length >= 2) {
        parts.push(
          <code key={`c-${match.index}`} className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded text-[11px] font-mono">
            {token.slice(1, -1)}
          </code>
        );
      } else if (token.startsWith('*') && token.endsWith('*') && token.length >= 2) {
        parts.push(
          <em key={`i-${match.index}`} className="italic text-slate-700">
            {token.slice(1, -1)}
          </em>
        );
      } else {
        parts.push(token);
      }
      lastIdx = tokenRegex.lastIndex;
    }

    if (lastIdx < clean.length) {
      parts.push(clean.substring(lastIdx));
    }

    return (
      <>
        {parts.length > 0 ? parts : clean}
        {sourceElement}
      </>
    );
  };

  const renderMarkdownText = (text?: string, currentSources?: SourceDocItem[]) => {
    if (!text) return null;
    const lines = text.split('\n');

    return (
      <div className="space-y-2 text-xs sm:text-[13px] text-slate-800 leading-relaxed pl-1">
        {lines.map((line, idx) => {
          const trimmed = line.trim();
          if (!trimmed) return <div key={idx} className="h-1" />;

          // Preamble header
          if (trimmed.includes('Based on the verified official records')) {
            return (
              <p key={idx} className="font-semibold text-slate-900 pb-1 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>{trimmed}</span>
              </p>
            );
          }

          // Traceability footer disclaimer
          if (trimmed.startsWith('*') && trimmed.endsWith('*') && trimmed.includes('traceable')) {
            return (
              <p key={idx} className="italic text-xs text-slate-500 pt-2.5 border-t border-slate-100/90 mt-2 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
                <span>{trimmed.replace(/\*/g, '')}</span>
              </p>
            );
          }

          // Indented sub-bullets (e.g. "  • " or "    - " or "  (i) ")
          const subMatch = line.match(/^(\s{2,}|\t+)(?:[\-\*\•]|\([iIvVxXa-z\d]+\)|\d+\.)\s+(.*)/);
          if (subMatch) {
            const subBody = subMatch[2];
            return (
              <div key={idx} className="flex items-start space-x-2 pl-6 py-0.5 text-slate-700">
                <span className="text-slate-400 font-bold shrink-0 mt-0.5">–</span>
                <span className="leading-relaxed">{renderInlineFormatted(subBody, currentSources)}</span>
              </div>
            );
          }

          // Top-level Bullets (- or • or *)
          if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
            const body = trimmed.substring(2);
            return (
              <div key={idx} className="flex items-start space-x-2 pl-1 py-0.5 group">
                <span className="text-blue-600 font-bold shrink-0 mt-0.5">•</span>
                <span className="leading-relaxed">{renderInlineFormatted(body, currentSources)}</span>
              </div>
            );
          }

          // Numbered lists (e.g. 1. , 2. )
          const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
          if (numMatch) {
            const num = numMatch[1];
            const body = numMatch[2];
            return (
              <div key={idx} className="flex items-start space-x-2.5 pl-1 py-0.5">
                <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-800 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {num}
                </span>
                <span className="leading-relaxed">{renderInlineFormatted(body, currentSources)}</span>
              </div>
            );
          }

          // Normal paragraphs / Executive briefing sentences
          return (
            <p key={idx} className="leading-relaxed text-slate-700 py-0.5">
              {renderInlineFormatted(trimmed, currentSources)}
            </p>
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 sm:gap-5 items-start w-full">
      
      {/* Hidden File Input for Paperclip / Direct Upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileSelected}
        className="hidden"
      />

      {/* MOBILE TAB SWITCHER (< lg screens) */}
      <div className="flex lg:hidden w-full bg-slate-200/80 p-1 rounded-xl mb-2 text-xs font-semibold shrink-0">
        <button
          type="button"
          onClick={() => setMobileTab('chat')}
          className={`flex-1 py-2 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            mobileTab === 'chat'
              ? 'bg-white text-blue-700 shadow-2xs font-bold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Chat & Inquiries</span>
          {messages.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-blue-600"></span>
          )}
        </button>
        <button
          type="button"
          onClick={() => setMobileTab('source')}
          className={`flex-1 py-2 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            mobileTab === 'source'
              ? 'bg-white text-blue-700 shadow-2xs font-bold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Source Document</span>
          {activeCitation && (
            <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-1.5 py-0.2 rounded-full">
              P.{activeCitation.page_number}
            </span>
          )}
        </button>
      </div>

      {/* LEFT / CENTER: Ask gov.guide Chat Module (62% width on desktop) */}
      <div className={`flex-1 w-full flex-col ${mobileTab === 'chat' ? 'flex' : 'hidden lg:flex'}`}>
        {/* Header Title, Subtitle, & Session Action */}
        <div className="mb-3 sm:mb-4 flex items-center justify-between gap-2">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 leading-tight">
              Ask gov.guide
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 font-normal mt-0.5">
              Source-grounded government intelligence & official document assistant.
            </p>
          </div>

          {messages.length > 0 && (
            <button
              type="button"
              onClick={handleNewChat}
              className="inline-flex items-center space-x-1 sm:space-x-1.5 px-2.5 sm:px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs transition-colors shrink-0"
              title="Start a fresh conversation"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">New Session</span>
              <span className="sm:hidden">Reset</span>
            </button>
          )}
        </div>

        {/* White Chat Main Card */}
        <div className="relative bg-white rounded-2xl border border-slate-200 p-3.5 sm:p-5 lg:p-6 shadow-xs flex flex-col space-y-4 sm:space-y-6 min-h-[440px] sm:min-h-[520px] overflow-hidden">
          
          {/* Subtle Background Watermark Logo */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none opacity-[0.035] -z-0">
            <AssamEmblem className="w-80 h-96 scale-150 text-slate-900" />
          </div>

          {/* INITIAL STATE: When no messages have been sent yet */}
          {messages.length === 0 && (
            <div className="relative z-10 flex flex-col justify-center my-auto py-2 sm:py-4">
              {/* Welcome Badge */}
              <div className="flex items-center space-x-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-[#0f243a] text-white flex items-center justify-center shadow-xs shrink-0">
                  <Landmark className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    Official Knowledge Assistant
                    <span className="bg-blue-100 text-blue-800 text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-full">
                      NESFIC 2026
                    </span>
                  </h2>
                  <p className="text-xs text-slate-500">
                    Upload official government manuals, circulars, or gazette notifications to query with verified citations.
                  </p>
                </div>
              </div>

              {/* Prominent Upload Dropzone Card */}
              <div 
                onClick={handlePaperclipClick}
                className="border-2 border-dashed border-blue-200/90 hover:border-blue-500 bg-gradient-to-b from-blue-50/40 via-white to-slate-50/60 hover:bg-blue-50/50 rounded-2xl p-6 sm:p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all group shadow-2xs"
              >
                <div className="w-14 h-14 rounded-2xl bg-blue-100/90 text-blue-700 flex items-center justify-center mb-3 group-hover:scale-105 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-xs">
                  {uploadingPdf ? (
                    <Loader2 className="w-7 h-7 animate-spin text-blue-600 group-hover:text-white" />
                  ) : (
                    <FileUp className="w-7 h-7 text-blue-600 group-hover:text-white transition-colors" />
                  )}
                </div>

                <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-1">
                  {uploadingPdf ? `Indexing ${uploadingFileName}...` : 'Upload Official PDF Document'}
                </h3>
                <p className="text-xs text-slate-500 max-w-sm leading-relaxed mb-4">
                  Upload departmental orders, rules, circulars, or guidelines. GovSaarthi will automatically extract, chunk, and index the text for verifiable retrieval.
                </p>

                <button
                  type="button"
                  disabled={uploadingPdf}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-[#2563eb] hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>{uploadingPdf ? 'Processing Document...' : 'Select PDF to Upload'}</span>
                </button>

                <div className="flex items-center gap-3 mt-3 text-[11px] text-slate-400">
                  <span>PDF format up to 25MB</span>
                  <span>•</span>
                  <span>Vector Indexed</span>
                  <span>•</span>
                  <span>Source Grounded</span>
                </div>
              </div>

              {/* Three Trust & Capability Pillars */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mt-4">
                <div className="bg-slate-50/80 border border-slate-200/70 rounded-xl p-3 flex items-start space-x-2.5 text-left">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">Instant Parsing</span>
                    <span className="text-[11px] text-slate-500 leading-snug">Extracts clauses, headings, and lists cleanly.</span>
                  </div>
                </div>

                <div className="bg-slate-50/80 border border-slate-200/70 rounded-xl p-3 flex items-start space-x-2.5 text-left">
                  <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">Exact Page Citations</span>
                    <span className="text-[11px] text-slate-500 leading-snug">Answers link directly to source page numbers.</span>
                  </div>
                </div>

                <div className="bg-slate-50/80 border border-slate-200/70 rounded-xl p-3 flex items-start space-x-2.5 text-left">
                  <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-bold text-slate-900 block">Zero Hallucinations</span>
                    <span className="text-[11px] text-slate-500 leading-snug">Strict verification against uploaded text.</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* MESSAGE STREAM: Displayed after questions are asked */}
          {messages.map((msg, index) => (
            <div key={msg.id || index} className="w-full">
              {msg.role === 'user' ? (
                /* USER MESSAGE BUBBLE */
                <div className="w-full flex justify-end mb-4">
                  <div className="bg-[#dbeafe] rounded-2xl p-3 sm:p-4 px-3.5 sm:px-5 max-w-[88%] sm:max-w-xl w-auto shadow-2xs">
                    <div className="flex items-center space-x-2.5 sm:space-x-3">
                      <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-[#3b82f6] text-white flex items-center justify-center shrink-0">
                        <User className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      </div>
                      <div className="text-xs sm:text-sm font-medium text-slate-900 leading-normal">
                        {msg.content}
                      </div>
                    </div>
                    <div className="text-[10px] sm:text-[11px] text-slate-500 text-right mt-1.5 font-normal">
                      {msg.timestamp || 'Just now'}
                    </div>
                  </div>
                </div>
              ) : (
                /* ASSISTANT RESPONSE */
                <div className="w-full space-y-3.5 pt-1 mb-6 border-b border-slate-100 pb-6 last:border-b-0 last:pb-0">
                  {/* Header: gov.guide + Green Pill */}
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 rounded-full bg-[#0f243a] text-white flex items-center justify-center shrink-0">
                      <Landmark className="w-4 h-4" />
                    </div>
                    <span className="font-bold text-sm text-slate-900">
                      gov.guide
                    </span>
                    <span className="bg-[#dcfce7] text-[#15803d] text-xs px-3 py-0.5 rounded-full font-medium">
                      Source-grounded answer
                    </span>
                  </div>

                  {/* Answer Text */}
                  <div className="text-sm text-slate-800 leading-relaxed space-y-3 pl-1">
                    {renderMarkdownText(msg.content, msg.sources)}
                  </div>

                  {/* Sources Box */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="pt-3 pl-1 space-y-2.5">
                      <h4 className="font-bold text-sm text-slate-900">
                        Sources ({msg.sources.length})
                      </h4>

                      {msg.sources.map((src) => {
                        const isSelected = activeCitation?.citation_id 
                          ? activeCitation.citation_id === src.id
                          : activeCitation?.document_name === src.name && activeCitation?.page_number === src.page;
                        return (
                          <div
                            key={src.id}
                            className={`border rounded-xl p-3 bg-white flex items-center justify-between transition-all ${
                              isSelected 
                                ? 'border-blue-400 bg-blue-50/20 shadow-2xs' 
                                : 'border-slate-200 hover:bg-slate-50/70'
                            }`}
                          >
                            <div className="flex items-center space-x-3 truncate">
                              <PdfBadge className="w-6 h-7 shrink-0" />
                              <div className="truncate">
                                <div className="font-bold text-xs text-slate-900 truncate">
                                  {src.name}
                                </div>
                                <div className="text-xs text-slate-500 font-normal mt-0.5 truncate">
                                  {src.subtitle}
                                </div>
                              </div>
                            </div>

                            <button
                              type="button"
                              onClick={() => handleSelectSource(src)}
                              className="px-4 py-1 rounded-lg border border-[#bfdbfe] bg-[#eff6ff] text-[#2563eb] text-xs font-semibold hover:bg-blue-100 transition-colors shrink-0 ml-3"
                            >
                              View
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Follow-up Question Prompts (only on the latest assistant message) */}
                  {index === messages.length - 1 && !loading && (
                    <div className="mt-4 pt-3 border-t border-slate-100 pl-1">
                      <p className="text-[11px] font-semibold text-slate-500 mb-2 flex items-center gap-1.5">
                        <CornerDownRight className="w-3.5 h-3.5 text-blue-600" />
                        Relevant follow-up questions:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {getFollowUpList().map((suggestion, sIdx) => (
                          <button
                            key={sIdx}
                            type="button"
                            onClick={() => executeQuery(suggestion)}
                            className="text-left text-xs text-slate-700 bg-slate-50 hover:bg-blue-50/80 hover:text-blue-900 hover:border-blue-300 border border-slate-200 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 shadow-2xs"
                          >
                            <span>{suggestion}</span>
                            <ChevronRight className="w-3 h-3 text-slate-400" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {/* LOADING INDICATOR */}
          {loading && (
            <div className="w-full space-y-3 pt-2">
              <div className="flex items-center space-x-3">
                <div className="w-7 h-7 rounded-full bg-[#0f243a] text-white flex items-center justify-center shrink-0">
                  <Landmark className="w-4 h-4" />
                </div>
                <span className="font-bold text-sm text-slate-900">
                  gov.guide
                </span>
                <span className="bg-blue-50 text-blue-700 text-xs px-2.5 py-0.5 rounded-full font-medium flex items-center gap-1.5">
                  <Loader2 className="w-3 h-3 animate-spin text-blue-600" />
                  Generating source-grounded response...
                </span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-500 space-y-2">
                <div className="h-3 bg-slate-200 rounded animate-pulse w-3/4"></div>
                <div className="h-3 bg-slate-200 rounded animate-pulse w-5/6"></div>
                <div className="h-3 bg-slate-200 rounded animate-pulse w-1/2"></div>
              </div>
            </div>
          )}

          {/* Anchor for Auto-scroll */}
          <div ref={messagesEndRef} />

        </div>

        {/* UPLOADING PROGRESS BANNER */}
        {uploadingPdf && (
          <div className="flex items-center space-x-2.5 bg-blue-50 border border-blue-200 text-blue-900 text-xs px-4 py-2.5 rounded-xl mt-3 shadow-2xs">
            <Loader2 className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
            <span className="font-medium">
              Uploading and indexing <strong>{uploadingFileName}</strong> into pgvector knowledge base...
            </span>
          </div>
        )}

        {/* ATTACHED DOCUMENT PILL ABOVE INPUT */}
        {attachedDoc && (
          <div className="flex items-center justify-between bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-2 text-xs text-emerald-950 mt-3 shadow-2xs">
            <div className="flex items-center space-x-2.5 truncate">
              <PdfBadge className="w-5 h-6 shrink-0" />
              <div className="truncate">
                <span className="font-bold text-slate-900">
                  Attached Document:
                </span>
                <span className="ml-1.5 font-medium text-emerald-800">
                  {attachedDoc.filename}
                </span>
                <span className="text-[11px] text-emerald-600 ml-2">
                  ({attachedDoc.page_count} {attachedDoc.page_count === 1 ? 'page' : 'pages'} • Indexed)
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setAttachedDoc(null)}
              className="text-slate-400 hover:text-slate-800 p-1 rounded-md transition-colors text-xs flex items-center gap-1 font-medium ml-3 shrink-0"
              title="Clear attached document filter to query across all documents"
            >
              <span>Search all</span>
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* BOTTOM INPUT BAR MATCHING SCREENSHOT */}
        <form
          onSubmit={handleSend}
          className="bg-white border border-slate-200 rounded-2xl p-1.5 sm:p-2.5 px-2.5 sm:px-4 flex items-center justify-between shadow-xs mt-3 gap-1.5 sm:gap-2"
        >
          {/* Paperclip Button for File Upload */}
          <button
            type="button"
            onClick={handlePaperclipClick}
            disabled={uploadingPdf}
            className="text-slate-400 hover:text-blue-600 p-1.5 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center disabled:opacity-40 shrink-0"
            title="Upload and index PDF document"
          >
            {uploadingPdf ? (
              <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 animate-spin" />
            ) : (
              <Paperclip className="w-4 h-4 sm:w-5 sm:h-5" strokeWidth={1.8} />
            )}
          </button>

          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={
              attachedDoc 
                ? `Ask about ${attachedDoc.filename}...`
                : messages.length === 0 
                  ? "Ask about government rules, circulars, or portal resources..." 
                  : "Ask a follow-up question..."
            }
            disabled={loading || uploadingPdf}
            className="flex-1 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none px-1.5 sm:px-3 bg-transparent min-w-0"
          />

          <button
            type="submit"
            disabled={loading || uploadingPdf || !inputQuery.trim()}
            className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-[#2563eb] hover:bg-blue-700 disabled:opacity-40 text-white flex items-center justify-center transition-colors shadow-xs shrink-0"
          >
            <Send className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white -rotate-12 translate-x-0.5" />
          </button>
        </form>

      </div>

      {/* RIGHT: Source Document Preview Panel (38% width on desktop, full tab on mobile) */}
      <div className={`w-full lg:w-[410px] shrink-0 sticky top-20 sm:top-22 ${mobileTab === 'source' ? 'block' : 'hidden lg:block'}`}>
        <SourcePreviewPanel 
          citation={activeCitation} 
          onBackToChat={() => setMobileTab('chat')}
        />
      </div>

    </div>
  );
};
