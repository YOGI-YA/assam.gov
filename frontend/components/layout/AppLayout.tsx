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
    <div className="h-screen bg-[#f8fafc] flex flex-col font-sans overflow-hidden">
      <Navbar 
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)} 
        isMobileMenuOpen={mobileMenuOpen}
      />
      <div className="flex-1 flex w-full min-h-0 overflow-hidden">
        <Sidebar 
          isOpen={mobileMenuOpen} 
          onClose={() => setMobileMenuOpen(false)} 
        />
        <main className="flex-1 overflow-hidden p-2.5 sm:p-4 lg:p-5 bg-[#f8fafc] flex flex-col min-h-0">
          {children}
        </main>
      </div>
    </div>
  );
};
