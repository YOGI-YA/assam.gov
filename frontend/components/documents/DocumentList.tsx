'use client';

import React, { useState, useEffect } from 'react';
import { 
  FileText, Upload, Trash2, Search, Filter, ExternalLink, 
  CheckCircle2, Clock, AlertTriangle, RefreshCw, Eye
} from 'lucide-react';
import { api } from '@/lib/api';
import { DocumentItem } from '@/types';
import { DocumentUploadModal } from './DocumentUploadModal';

export const DocumentList: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedDocForPreview, setSelectedDocForPreview] = useState<DocumentItem | null>(null);

  useEffect(() => {
    loadDocuments();
  }, [categoryFilter, search]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.getDocuments(categoryFilter, search);
      setDocuments(data);
    } catch (e) {
      console.error('Failed to load documents:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete '${name}'? This will remove all chunks and vector embeddings.`)) {
      return;
    }
    try {
      await api.deleteDocument(id);
      loadDocuments();
    } catch (e: any) {
      alert(`Delete failed: ${e.message}`);
    }
  };

  const categories = [
    'All', 
    'NESFIC Guidelines', 
    'State Data Portals', 
    'Rules & Manuals', 
    'Department Notifications', 
    'Circulars', 
    'Training Guidelines', 
    'Office Order'
  ];

  return (
    <div className="space-y-4">
      {/* Page Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h1 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <span>Official Government Documents</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
              {documents.length} Total
            </span>
          </h1>
          <p className="text-xs text-slate-500">
            Manage, upload and inspect indexed Assam Government manuals, circulars and departmental notifications.
          </p>
        </div>

        <button
          onClick={() => setIsUploadOpen(true)}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-gov-800 hover:bg-gov-900 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
        >
          <Upload className="w-3.5 h-3.5 text-amber-300" />
          <span>Upload Document (PDF)</span>
        </button>
      </div>

      {/* Filters and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-lg border border-slate-200 shadow-xs">
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search documents by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-gov-700"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="text-xs text-slate-500 font-medium">Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-gov-700"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={loadDocuments}
            title="Refresh list"
            className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Document Title</th>
                <th className="py-3 px-3">Category</th>
                <th className="py-3 px-3">Pages</th>
                <th className="py-3 px-3">File Size</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Upload Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    {loading ? 'Loading documents...' : 'No documents found matching the filter.'}
                  </td>
                </tr>
              ) : (
                documents.map((doc) => {
                  const sizeKB = Math.round(doc.file_size / 1024);
                  return (
                    <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2.5">
                          <FileText className="w-4 h-4 text-gov-800 shrink-0" />
                          <div>
                            <div className="font-semibold text-slate-800 hover:text-gov-800 transition-colors">
                              {doc.filename}
                            </div>
                            <div className="text-[10px] text-slate-400">
                              {doc.source_classification}
                            </div>
                          </div>
                        </div>
                      </td>

                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-medium border border-slate-200">
                          {doc.category}
                        </span>
                      </td>

                      <td className="py-3 px-3 font-medium text-slate-700">
                        {doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}
                      </td>

                      <td className="py-3 px-3 text-slate-500">
                        {sizeKB > 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`}
                      </td>

                      <td className="py-3 px-3">
                        {doc.processing_status === 'INDEXED' ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            <span>INDEXED</span>
                          </span>
                        ) : doc.processing_status === 'PROCESSING' ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-semibold border border-blue-200">
                            <RefreshCw className="w-3 h-3 text-blue-600 animate-spin" />
                            <span>PROCESSING</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-50 text-rose-700 text-[10px] font-semibold border border-rose-200" title={doc.error_message || ''}>
                            <AlertTriangle className="w-3 h-3 text-rose-600" />
                            <span>FAILED</span>
                          </span>
                        )}
                      </td>

                      <td className="py-3 px-3 text-slate-500 text-[11px]">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>

                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => setSelectedDocForPreview(doc)}
                            title="Inspect PDF Document"
                            className="p-1.5 text-slate-600 hover:text-gov-800 hover:bg-slate-100 rounded transition-colors"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <a
                            href={api.getDocumentFileUrl(doc.id)}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="Open original file in new tab"
                            className="p-1.5 text-slate-600 hover:text-gov-800 hover:bg-slate-100 rounded transition-colors"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                          <button
                            onClick={() => handleDelete(doc.id, doc.filename)}
                            title="Delete document"
                            className="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <DocumentUploadModal
          onClose={() => setIsUploadOpen(false)}
          onUploadSuccess={() => {
            setIsUploadOpen(false);
            loadDocuments();
          }}
        />
      )}

      {/* Document Quick Preview Modal */}
      {selectedDocForPreview && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-4xl h-[85vh] flex flex-col overflow-hidden shadow-2xl border border-slate-200">
            <div className="p-3.5 bg-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2 truncate">
                <FileText className="w-4 h-4 text-amber-300" />
                <span className="text-xs font-semibold truncate">{selectedDocForPreview.filename}</span>
                <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                  {selectedDocForPreview.page_count} Pages
                </span>
              </div>
              <button
                onClick={() => setSelectedDocForPreview(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700"
              >
                Close Preview
              </button>
            </div>
            <div className="flex-1 bg-slate-100">
              <iframe
                src={api.getDocumentFileUrl(selectedDocForPreview.id)}
                className="w-full h-full border-0"
                title={selectedDocForPreview.filename}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
