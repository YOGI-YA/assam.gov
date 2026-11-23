'use client';

import React, { useState, useEffect } from 'react';
import { History, Shield, RefreshCw, Filter, Clock, User, FileText, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { AuditLogItem } from '@/types';

export const AuditLogTable: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('ALL');

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(60);
      setLogs(data);
    } catch (e) {
      console.error('Failed to load audit logs:', e);
    } finally {
      setLoading(false);
    }
  };

  const actions = ['ALL', 'LOGIN', 'DOCUMENT_UPLOAD', 'DOCUMENT_DELETE', 'CHAT_QUERY', 'CONTEXT_RETRIEVAL', 'RESPONSE_GENERATED', 'GENERATE_DRAFT', 'SUMMARIZE'];

  const filteredLogs = filterAction === 'ALL' 
    ? logs 
    : logs.filter(l => l.action === filterAction);

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'LOGIN':
        return <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-semibold border border-blue-200">LOGIN</span>;
      case 'DOCUMENT_UPLOAD':
        return <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">UPLOAD</span>;
      case 'DOCUMENT_DELETE':
        return <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 text-[10px] font-semibold border border-rose-200">DELETE</span>;
      case 'CHAT_QUERY':
      case 'CONTEXT_RETRIEVAL':
        return <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[10px] font-semibold border border-indigo-200">RETRIEVAL</span>;
      case 'RESPONSE_GENERATED':
        return <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 text-[10px] font-semibold border border-purple-200">AI ANSWER</span>;
      case 'GENERATE_DRAFT':
      case 'SUMMARIZE':
        return <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 text-[10px] font-semibold border border-amber-200">DRAFTING</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-semibold">{action}</span>;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h1 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <span>Audit & Traceability Records</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
              {filteredLogs.length} Records
            </span>
          </h1>
          <p className="text-xs text-slate-500">
            Immutable activity log recording user logins, document uploads, RAG queries, and draft creations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-gov-700"
          >
            {actions.map((act) => (
              <option key={act} value={act}>{act}</option>
            ))}
          </select>
          <button
            onClick={loadLogs}
            className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-3">Action Type</th>
                <th className="py-3 px-3">Officer / User</th>
                <th className="py-3 px-4">Metadata & Trace Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-400">
                    {loading ? 'Loading audit records...' : 'No activity records match the selected filter.'}
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-4 text-slate-500 text-[11px] whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3">
                      {getActionBadge(log.action)}
                    </td>
                    <td className="py-2.5 px-3 font-medium text-slate-700 text-[11px]">
                      {log.user_email || log.user_id || 'System / Officer'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-600 font-mono text-[11px]">
                      {log.metadata ? (
                        <div className="max-w-xl truncate text-[11px]">
                          {Object.entries(log.metadata).map(([k, v]) => (
                            <span key={k} className="mr-3">
                              <span className="text-slate-400 font-semibold">{k}:</span>{' '}
                              <span className="text-slate-700">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">No extra metadata</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
