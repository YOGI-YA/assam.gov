import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'gov.guide — Government Knowledge Assistant (MVP)',
  description: 'AI-Powered Document Intelligence & Source-Grounded Knowledge Assistant for Assam Administration',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
