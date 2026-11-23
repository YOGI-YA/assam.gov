'use client';

import React from 'react';
import { Bell, ChevronDown, Menu, X } from 'lucide-react';
import { AssamEmblem } from '@/components/ui/AssamEmblem';
import Link from 'next/link';

interface NavbarProps {
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileMenu, isMobileMenuOpen }) => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
      <div className="w-full px-3.5 sm:px-6 h-16 sm:h-18 py-2.5 flex items-center justify-between">
        {/* Left: Mobile Menu Toggle + Emblem + Brand Title */}
        <div className="flex items-center space-x-2.5 sm:space-x-4">
          {/* Hamburger button for mobile */}
          <button
            type="button"
            onClick={onToggleMobileMenu}
            aria-label="Toggle Navigation Menu"
            className="md:hidden p-1.5 -ml-1 text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>

          <Link href="/" className="flex items-center space-x-2.5 sm:space-x-3.5 group">
            <AssamEmblem className="shrink-0 scale-90 sm:scale-100 origin-left" />
            <div className="flex flex-col justify-center">
              <span className="text-lg sm:text-[22px] font-bold tracking-tight text-slate-950 leading-none">
                gov.guide
              </span>
              <span className="text-[11px] sm:text-[12px] text-slate-500 font-normal mt-1 leading-none">
                <span className="hidden sm:inline">Government Knowledge Assistant (MVP)</span>
                <span className="sm:hidden">Gov Knowledge Assistant</span>
              </span>
            </div>
          </Link>
        </div>

        {/* Right: Notifications & Admin Officer Profile */}
        <div className="flex items-center space-x-3 sm:space-x-6">
          <button 
            type="button" 
            aria-label="Notifications"
            className="text-slate-600 hover:text-slate-900 p-1.5 rounded-full hover:bg-slate-100 transition-colors"
          >
            <Bell className="w-4 h-4 sm:w-5 sm:h-5 text-slate-700" strokeWidth={1.8} />
          </button>

          <div className="flex items-center space-x-2 sm:space-x-2.5 cursor-pointer hover:opacity-90 transition-opacity">
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#dbeafe] flex items-center justify-center text-[#1d4ed8] font-semibold text-xs sm:text-sm">
              A
            </div>
            <span className="hidden sm:inline text-sm font-medium text-slate-900">
              Admin Officer
            </span>
            <ChevronDown className="hidden sm:inline w-4 h-4 text-slate-600" />
          </div>
        </div>
      </div>
    </header>
  );
};
