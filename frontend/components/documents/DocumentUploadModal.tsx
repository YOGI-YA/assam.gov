'use client';

import React, { useState } from 'react';
import { Upload, X, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';

interface DocumentUploadModalProps {
  onClose: () => void;
  onUploadSuccess: () => void;
}

export const DocumentUploadModal: React.FC<DocumentUploadModalProps> = ({ onClose, onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState('Rules & Manuals');
  const [classification, setClassification] = useState('Public Official Document');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    'Rules & Manuals',
    'Department Notifications',
    'Circulars',
    'Training Guidelines',
    'Office Order',
    'NESFIC Guidelines',
    'State Data Portals',
    'General Administrative Order'
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF documents (.pdf) are permitted.');
        return;
      }
      if (selected.size > 25 * 1024 * 1024) {
        setError('File size exceeds the 25MB limit.');
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF document to upload.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await api.uploadDocument(file, category, classification);
      onUploadSuccess();
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please verify PDF file integrity.');
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-lg overflow-hidden shadow-2xl border border-slate-200">
        <div className="p-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Upload className="w-4 h-4 text-amber-300" />
            <h3 className="text-sm font-semibold">Upload Government Document</h3>
          </div>
          <button
            onClick={onClose}
            disabled={uploading}
            className="text-slate-400 hover:text-white p-1 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleUpload} className="p-5 space-y-4">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* File input drag drop zone */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Select Official PDF File *
            </label>
            <div className="border-2 border-dashed border-slate-200 hover:border-gov-600 rounded-lg p-5 text-center transition-colors bg-slate-50/50">
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                disabled={uploading}
                className="hidden"
                id="doc-file-input"
              />
              <label
                htmlFor="doc-file-input"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <div className="w-10 h-10 rounded-full bg-gov-100 flex items-center justify-center text-gov-800">
                  <FileText className="w-5 h-5 text-gov-800" />
                </div>
                {file ? (
                  <div>
                    <span className="text-xs font-semibold text-slate-800 block">
                      {file.name}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      {(file.size / 1024).toFixed(1)} KB • Ready for extraction
                    </span>
                  </div>
                ) : (
                  <div>
                    <span className="text-xs font-medium text-gov-800 hover:underline">
                      Click to browse or drop PDF here
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">
                      Max file size: 25MB • Text-based PDFs recommended
                    </span>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Document Category */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Document Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={uploading}
              className="w-full text-xs bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-gov-700"
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Source Classification */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Source Classification / Department
            </label>
            <input
              type="text"
              value={classification}
              onChange={(e) => setClassification(e.target.value)}
              disabled={uploading}
              placeholder="e.g. Assam Administrative Staff College (AASC)"
              className="w-full text-xs bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-gov-700"
            />
          </div>

          <div className="p-3 bg-slate-50 rounded border border-slate-200 text-[11px] text-slate-500 space-y-1">
            <div className="font-semibold text-slate-700">RAG Ingestion Pipeline:</div>
            <div>1. Page-by-page text extraction via PyMuPDF.</div>
            <div>2. Semantic chunking with original page metadata.</div>
            <div>3. Dense vector embedding generation & database indexing.</div>
          </div>

          {/* Modal Actions */}
          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={uploading}
              className="px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading || !file}
              className="px-4 py-2 bg-gov-800 hover:bg-gov-900 disabled:opacity-40 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition-colors"
            >
              {uploading ? (
                <span>Extracting & Indexing...</span>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5 text-amber-300" />
                  <span>Index Document</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
