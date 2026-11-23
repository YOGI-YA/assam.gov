'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  FileText, SquarePen, Clock, FileCheck, X
} from 'lucide-react';
import { AssamEmblem } from '@/components/ui/AssamEmblem';

// Custom Chat Bubble icon with three dots matching screenshot (...)
const ChatDotsIcon: React.FC<{ className?: string }> = ({ className = 'w-5 h-5' }) => (
  <svg 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="1.8" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    <circle cx="8" cy="12" r="0.8" fill="currentColor" />
    <circle cx="12" cy="12" r="0.8" fill="currentColor" />
    <circle cx="16" cy="12" r="0.8" fill="currentColor" />
  </svg>
);

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();

  const navItems = [
    {
      name: 'Ask gov.guide',
      href: '/chat',
      icon: ChatDotsIcon,
      isDefault: true,
    },
    {
      name: 'Documents',
      href: '/documents',
      icon: FileText,
    },
    {
      name: 'Drafting Studio',
      href: '/drafting',
      icon: SquarePen,
    },
    {
      name: 'Audit Logs',
      href: '/audit',
      icon: Clock,
    },
  ];

  const renderNavContent = () => (
    <>
      {/* Navigation list */}
      <nav className="space-y-1.5">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname === '/' && item.name === 'Ask gov.guide');
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => onClose?.()}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-[#dbeafe] text-[#2563eb] font-semibold'
                  : 'text-slate-700 hover:bg-slate-200/60 font-medium'
              }`}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-[#2563eb]' : 'text-slate-600'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom MVP (Demo) Card */}
      <div className="bg-[#f0f6ff]/80 border border-blue-200/60 rounded-xl p-3.5 space-y-1 mt-auto">
        <div className="flex items-center space-x-1.5 text-slate-900 font-bold text-xs">
          <FileCheck className="w-4 h-4 text-slate-700 shrink-0" />
          <span>MVP (Demo)</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-snug">
          Using publicly available / sample government documents.
        </p>
      </div>
    </>
  );

  return (
    <>
      {/* DESKTOP SIDEBAR: Fixed width on medium & larger screens */}
      <aside className="hidden md:flex w-56 bg-[#f8fafc] border-r border-slate-200 flex-col justify-between shrink-0 min-h-[calc(100vh-4.6rem)] p-4">
        {renderNavContent()}
      </aside>

      {/* MOBILE DRAWER: Off-canvas sidebar when toggled on small screens */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Backdrop overlay */}
          <div 
            className="fixed inset-0 bg-slate-950/40 backdrop-blur-2xs transition-opacity" 
            onClick={onClose} 
            aria-hidden="true"
          />

          {/* Slide-out Drawer */}
          <aside className="relative w-72 max-w-[85vw] bg-white h-full shadow-2xl flex flex-col justify-between p-4 z-10 animate-in slide-in-from-left duration-200 border-r border-slate-200">
            {/* Drawer Header with Logo and Close Button */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-3">
              <div className="flex items-center space-x-2.5">
                <AssamEmblem className="w-7 h-7 shrink-0" />
                <span className="font-bold text-base text-slate-900">gov.guide</span>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close menu"
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Nav content */}
            <div className="flex-1 flex flex-col justify-between overflow-y-auto">
              {renderNavContent()}
            </div>
          </aside>
        </div>
      )}
    </>
  );
};
