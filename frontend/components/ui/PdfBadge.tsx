'use client';

import React from 'react';

export const PdfBadge: React.FC<{ className?: string }> = ({ className = 'w-7 h-8' }) => {
  return (
    <div className={`relative flex flex-col items-center justify-center shrink-0 ${className}`}>
      <svg 
        viewBox="0 0 32 38" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-xs"
      >
        {/* Document Shape with folded corner */}
        <path 
          d="M4 2C4 0.895431 4.89543 0 6 0H22L30 8V36C30 37.1046 29.1046 38 28 38H6C4.89543 38 4 37.1046 4 36V2Z" 
          fill="#FFFFFF" 
          stroke="#EF4444" 
          strokeWidth="1.5"
        />
        <path 
          d="M22 0V8H30" 
          stroke="#EF4444" 
          strokeWidth="1.5"
          fill="#FEE2E2"
        />
        {/* PDF Red Label */}
        <text 
          x="17" 
          y="26" 
          fill="#DC2626" 
          fontSize="8.5" 
          fontWeight="bold" 
          fontFamily="system-ui, -apple-system, sans-serif"
          textAnchor="middle"
        >
          PDF
        </text>
      </svg>
    </div>
  );
};
