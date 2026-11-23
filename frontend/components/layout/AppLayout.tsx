'use client';

import React, { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
  currentModule?: string;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children, currentModule }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col font-sans">
      <Navbar 
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)} 
        isMobileMenuOpen={mobileMenuOpen}
      />
      <div className="flex-1 flex w-full">
        <Sidebar 
          isOpen={mobileMenuOpen} 
          onClose={() => setMobileMenuOpen(false)} 
        />
        <main className="flex-1 overflow-x-hidden p-3 sm:p-5 lg:p-6 bg-[#f8fafc]">
          {children}
        </main>
      </div>
    </div>
  );
};
