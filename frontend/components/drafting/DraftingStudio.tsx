'use client';

import React, { useState, useEffect } from 'react';
import { 
  PenTool, FileText, Copy, Download, Check, Sparkles, AlertCircle, 
  BookOpen, Landmark, Send, RefreshCw
} from 'lucide-react';
import { api } from '@/lib/api';
import { DocumentItem, CitationItem, DraftingRequest } from '@/types';

export const DraftingStudio: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [draftType, setDraftType] = useState<'office_note' | 'formal_letter' | 'office_order' | 'summary'>('office_note');
  const [subject, setSubject] = useState('');
  const [instructions, setInstructions] = useState('');
  const [targetAuthority, setTargetAuthority] = useState('Commissioner & Secretary, Government of Assam');
  const [referenceNumber, setReferenceNumber] = useState('');
  
  const [generating, setGenerating] = useState(false);
  const [generatedDraft, setGeneratedDraft] = useState('');
  const [referencesUsed, setReferencesUsed] = useState<CitationItem[]>([]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments();
      const indexed = data.filter(d => d.processing_status === 'INDEXED');
      setDocuments(indexed);
      if (indexed.length > 0) {
        setSelectedDocIds([indexed[0].id]);
      }
    } catch (e) {
      console.error('Failed to load documents for drafting:', e);
    }
  };

  const handleSelectDoc = (docId: string) => {
    setSelectedDocIds(prev => 
      prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
    );
  };

  const applyTemplate = (type: 'office_note' | 'formal_letter' | 'office_order' | 'summary') => {
    setDraftType(type);
    if (type === 'office_note') {
      setSubject('Sanction of contingent expenditure for IT infrastructure upgrading at AASC');
      setInstructions('Examine compliance under the Assam Secretariat Manual Rule 34 and DFPR thresholds. Recommend approval within authorized contingent expenditure limits.');
    } else if (type === 'formal_letter') {
      setSubject('Submission of satellite imagery spatial layers and drone survey data to ASSAC Nodal Repository');
      setInstructions('Direct all departmental divisions to deposit drone survey outputs in WGS84 Datum and UTM projection in compliance with DST Notification No. DST.88/2025/14.');
    } else if (type === 'office_order') {
      setSubject('Constitution of Departmental Condemnation Committee for obsolete IT hardware');
      setInstructions('Order the constitution of the technical condemnation committee including AMTRON/NIC representative in accordance with Rule 35 of the Secretariat Manual.');
    } else {
      setSubject('Executive Brief on Revised Gratuity and Pensionary Settlement Timelines');
      setInstructions('Summarize the critical procedural timelines for Pension Form 1 forwarding and the revised ceiling of Rs. 20 Lakhs for DCRG under Circular PPG(P) 142/2024/5.');
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !instructions.trim()) return;

    setGenerating(true);
    try {
      const req: DraftingRequest = {
        draft_type: draftType,
        subject,
        instructions,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        target_authority: targetAuthority,
        reference_number: referenceNumber || undefined,
      };

      const res = await api.generateDraft(req);
      setGeneratedDraft(res.draft_content);
      setReferencesUsed(res.references_used);
    } catch (err: any) {
      alert(`Draft generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedDraft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([generatedDraft], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = `Draft_${draftType}_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="pb-3 border-b border-slate-200">
        <h1 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <span>AI Drafting Studio</span>
          <span className="text-xs px-2 py-0.5 rounded bg-gov-100 text-gov-800 font-semibold">
            Government Draft Generator
          </span>
        </h1>
        <p className="text-xs text-slate-500">
          Synthesize official Assam Government administrative notes, letters, and orders grounded in verified records.
        </p>
      </div>

      {/* Split Screen Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* LEFT COLUMN: Input & Configuration (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-4">
            
            {/* Quick Template Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                1. Select Document Type & Format
              </label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { id: 'office_note', label: 'Office Note', desc: 'Green note sheet' },
                  { id: 'formal_letter', label: 'Formal Letter', desc: 'Official correspondence' },
                  { id: 'office_order', label: 'Office Order', desc: 'Directive / Sanction' },
                  { id: 'summary', label: 'Executive Summary', desc: 'Brief for superiors' },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => applyTemplate(item.id as any)}
                    className={`p-2.5 rounded-lg border text-left transition-all ${
                      draftType === item.id
                        ? 'bg-gov-50 border-gov-700 text-gov-900 font-semibold ring-1 ring-gov-700'
                        : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="text-xs">{item.label}</div>
                    <div className="text-[10px] text-slate-500 font-normal">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleGenerate} className="space-y-3.5">
              {/* Subject */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  2. Subject Matter *
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Sanction of contingent expenditure..."
                  required
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:ring-1 focus:ring-gov-700 focus:bg-white"
                />
              </div>

              {/* Target Authority */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  3. Addressed Authority / Department
                </label>
                <input
                  type="text"
                  value={targetAuthority}
                  onChange={(e) => setTargetAuthority(e.target.value)}
                  placeholder="e.g. Commissioner & Secretary, Government of Assam"
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:ring-1 focus:ring-gov-700 focus:bg-white"
                />
              </div>

              {/* Reference Document Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  4. Grounding Knowledge Context (Select Indexed Documents)
                </label>
                <div className="max-h-28 overflow-y-auto space-y-1 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                  {documents.length === 0 ? (
                    <div className="text-[11px] text-slate-400">No indexed documents available.</div>
                  ) : (
                    documents.map((d) => (
                      <label key={d.id} className="flex items-center space-x-2 text-slate-700 cursor-pointer hover:text-slate-900">
                        <input
                          type="checkbox"
                          checked={selectedDocIds.includes(d.id)}
                          onChange={() => handleSelectDoc(d.id)}
                          className="rounded text-gov-700 focus:ring-gov-700"
                        />
                        <span className="truncate text-[11px]">{d.filename}</span>
                      </label>
                    ))
                  )}
                </div>
              </div>

              {/* Instructions */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  5. Drafting Directives & Specific Instructions *
                </label>
                <textarea
                  rows={4}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Specify key clauses, background rationale, and decision sought..."
                  required
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-900 focus:outline-none focus:ring-1 focus:ring-gov-700 focus:bg-white resize-none"
                />
              </div>

              {/* Action Button */}
              <button
                type="submit"
                disabled={generating || !subject.trim() || !instructions.trim()}
                className="w-full py-2.5 bg-gov-800 hover:bg-gov-900 disabled:opacity-40 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-colors shadow-xs"
              >
                {generating ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Synthesizing Grounded Draft...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                    <span>Generate Official Draft</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* RIGHT COLUMN: Generated Output & Editor (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-3">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xs flex flex-col h-full min-h-[500px]">
            {/* Header Toolbar */}
            <div className="p-3 bg-slate-900 text-white rounded-t-lg flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-amber-300" />
                <span className="text-xs font-semibold">Generated Official Draft Preview</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-400 text-slate-900 font-bold uppercase tracking-wider">
                  Draft Watermark
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={handleCopy}
                  disabled={!generatedDraft}
                  className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded text-slate-300 transition-colors"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
                <button
                  type="button"
                  onClick={handleDownload}
                  disabled={!generatedDraft}
                  className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 bg-gov-700 hover:bg-gov-600 disabled:opacity-40 rounded text-white font-medium transition-colors"
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
                </button>
              </div>
            </div>

            {/* Disclaimer Alert */}
            <div className="p-2.5 bg-amber-50 border-b border-amber-200 text-[11px] text-amber-900 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                <strong>Mandatory Requirement:</strong> Every generated draft requires human administrative verification and an authorized officer&apos;s signature before official dispatch.
              </span>
            </div>

            {/* Editable Content Area */}
            <div className="flex-1 p-4 bg-slate-50/50 flex flex-col">
              {generatedDraft ? (
                <textarea
                  value={generatedDraft}
                  onChange={(e) => setGeneratedDraft(e.target.value)}
                  className="w-full flex-1 p-4 bg-white rounded border border-slate-300 font-mono text-xs leading-relaxed text-slate-900 focus:outline-none focus:ring-1 focus:ring-gov-700 resize-none"
                />
              ) : (
                <div className="h-full flex flex-col items-center justify-center p-8 text-center text-slate-400 space-y-3">
                  <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
                    <PenTool className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-700">No Draft Generated Yet</h4>
                    <p className="text-xs text-slate-500 max-w-sm mt-1">
                      Select a document template on the left, enter administrative instructions, and click Generate.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* References Citation Footer */}
            {referencesUsed.length > 0 && (
              <div className="p-3 bg-white border-t border-slate-200 rounded-b-lg">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Grounded Source References Used in This Draft:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {referencesUsed.map((ref) => (
                    <span
                      key={ref.citation_id}
                      className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-[10px] font-medium border border-slate-200"
                    >
                      {ref.document_name} (Page {ref.page_number})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
