'use client';

import React from 'react';

export const AssamEmblem: React.FC<{ className?: string }> = ({ className = 'h-11' }) => {
  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      {/* State Emblem of India (Ashoka Lion Capital) high-detail vector */}
      <svg
        viewBox="0 0 100 115"
        className="w-8 h-9 text-slate-800"
        fill="currentColor"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Three Lions Silhouette */}
        {/* Central Lion Head */}
        <circle cx="50" cy="18" r="7" />
        <path d="M46 12 C46 8, 54 8, 54 12 Z" />
        <path d="M44 19 C42 16, 42 24, 46 25 Z" />
        <path d="M56 19 C58 16, 58 24, 54 25 Z" />
        
        {/* Left Lion Head */}
        <circle cx="34" cy="22" r="6" />
        <path d="M31 16 C31 13, 37 13, 37 16 Z" />
        
        {/* Right Lion Head */}
        <circle cx="66" cy="22" r="6" />
        <path d="M63 16 C63 13, 69 13, 69 16 Z" />

        {/* Mane and Chest */}
        <path d="M32 26 C30 35, 42 42, 50 42 C58 42, 70 35, 68 26 C64 34, 58 37, 50 37 C42 37, 36 34, 32 26 Z" />
        <path d="M44 26 L56 26 L54 36 L46 36 Z" />
        <circle cx="47" cy="21" r="1" fill="#fff" />
        <circle cx="53" cy="21" r="1" fill="#fff" />
        <circle cx="33" cy="24" r="0.8" fill="#fff" />
        <circle cx="67" cy="24" r="0.8" fill="#fff" />

        {/* Abacus Platform */}
        <rect x="22" y="44" width="56" height="4" rx="1" />
        
        {/* Ashoka Chakra in Center */}
        <circle cx="50" cy="54" r="5.5" fill="none" stroke="currentColor" strokeWidth="1.2" />
        <circle cx="50" cy="54" r="1.5" />
        {/* Spokes */}
        <line x1="50" y1="48.5" x2="50" y2="59.5" stroke="currentColor" strokeWidth="0.6" />
        <line x1="44.5" y1="54" x2="55.5" y2="54" stroke="currentColor" strokeWidth="0.6" />
        <line x1="46.1" y1="50.1" x2="53.9" y2="57.9" stroke="currentColor" strokeWidth="0.6" />
        <line x1="46.1" y1="57.9" x2="53.9" y2="50.1" stroke="currentColor" strokeWidth="0.6" />

        {/* Galloping Horse (Left) & Bull (Right) reliefs */}
        <path d="M28 52 C26 50, 32 49, 36 53 C33 54, 30 55, 28 52 Z" />
        <path d="M64 52 C66 50, 72 49, 70 54 C67 55, 65 54, 64 52 Z" />

        {/* Lower Base / Bell Lotus Platform */}
        <rect x="20" y="61" width="60" height="3" rx="1" />
        <path d="M24 64 C28 72, 72 72, 76 64 Z" />
        <line x1="22" y1="73" x2="78" y2="73" stroke="currentColor" strokeWidth="1.5" />

        {/* Satyameva Jayate Inscription Dots/Bar */}
        <rect x="32" y="76" width="36" height="2" rx="0.5" />
      </svg>
      <span className="text-[8px] font-bold tracking-tight text-slate-800 uppercase leading-none mt-1">
        Government of Assam
      </span>
    </div>
  );
};
