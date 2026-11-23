'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  FileText, CheckCircle2, MessageSquare, PenTool, ArrowRight, 
  Upload, ShieldCheck, Sparkles, Building2, Landmark
} from 'lucide-react';
import { api } from '@/lib/api';
import { DashboardStats } from '@/types';

export const DashboardOverview: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_documents: 0,
    indexed_documents: 0,
    total_queries: 0,
    total_drafts: 0,
    recent_questions: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load dashboard stats:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-gov-900 via-gov-800 to-slate-900 rounded-xl p-6 text-white shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-2xl">
            <div className="flex items-center space-x-2 text-amber-300 text-xs font-semibold">
              <Landmark className="w-4 h-4" />
              <span>Assam Administrative Staff College (AASC) • DST • ASSAC</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">
              Welcome to gov.guide Knowledge Assistant
            </h1>
            <p className="text-xs text-slate-300 leading-relaxed">
              AI-powered document intelligence developed for the NESFIC 2026 challenge. 
              Enabling government officers to search administrative rules, verify source pages, and draft official notes with strict traceability.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <Link
              href="/chat"
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-amber-400 hover:bg-amber-300 text-slate-950 rounded-lg text-xs font-bold transition-all shadow-xs"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ask GovSaarthi</span>
            </Link>
            <Link
              href="/documents"
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-semibold backdrop-blur-xs transition-all border border-white/20"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload PDF</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Actual Database Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Uploaded
            </span>
            <FileText className="w-4 h-4 text-gov-700" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {stats.total_documents}
          </div>
          <p className="text-[10px] text-slate-400 mt-0.5">Government PDFs on record</p>
        </div>

        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Indexed in pgvector
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {stats.indexed_documents}
          </div>
          <p className="text-[10px] text-emerald-600 font-medium mt-0.5">Ready for RAG retrieval</p>
        </div>

        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Questions Answered
            </span>
            <MessageSquare className="w-4 h-4 text-gov-800" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {stats.total_queries}
          </div>
          <p className="text-[10px] text-slate-400 mt-0.5">Source-grounded queries</p>
        </div>

        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Drafts Generated
            </span>
            <PenTool className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">
            {stats.total_drafts}
          </div>
          <p className="text-[10px] text-slate-400 mt-0.5">Notes, letters & orders</p>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Recent Questions from Database */}
        <div className="lg:col-span-7 bg-white rounded-lg border border-slate-200 shadow-xs p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Recent Government Inquiries
              </h3>
              <Link href="/chat" className="text-xs text-gov-700 hover:text-gov-900 font-semibold flex items-center space-x-1">
                <span>Open Assistant</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="space-y-2">
              {stats.recent_questions.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-400">
                  No questions asked yet. Click &apos;Ask GovSaarthi&apos; to begin!
                </div>
              ) : (
                stats.recent_questions.map((q) => (
                  <Link
                    key={q.id}
                    href="/chat"
                    className="block p-2.5 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-gov-50 hover:border-gov-200 transition-colors"
                  >
                    <div className="text-xs font-medium text-slate-800 truncate">
                      {q.question}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {new Date(q.created_at).toLocaleString()}
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
            <span>Every answer grounded with exact document title and page number.</span>
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          </div>
        </div>

        {/* Core Principles & Demonstration Overview */}
        <div className="lg:col-span-5 bg-white rounded-lg border border-slate-200 shadow-xs p-4 space-y-3">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider pb-2 border-b border-slate-100">
            Core Product Philosophy
          </h3>

          <div className="space-y-2.5 text-xs">
            <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
              <div className="font-semibold text-slate-800">1. Grounded Retrieval Only</div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                If supporting information is not found in the indexed documents, GovSaarthi explicitly refuses rather than hallucinating rules.
              </p>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
              <div className="font-semibold text-slate-800">2. Answer-to-Source Verification</div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                Clicking citations immediately reveals the exact source document, page number, and supporting excerpt.
              </p>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
              <div className="font-semibold text-slate-800">3. Drafts Require Human Review</div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                All generated official drafts are clearly marked as requiring human review and authorized signatures.
              </p>
            </div>
          </div>

          <div className="pt-2 text-[10px] text-slate-400">
            NESFIC 2026 • Challenge ID NESFIC-D-36 • Stream 1 MVP
          </div>
        </div>
      </div>
    </div>
  );
};
