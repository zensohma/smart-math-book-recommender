import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import Link from 'next/link';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Smart Math Book Recommender',
  description: 'Temukan buku matematika yang relevan untuk studimu',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-gray-50/50">
        <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 font-bold text-lg">
              <span className="text-amber-600">&#x03A3;</span>
              <span>Books</span>
            </Link>
            <nav className="text-sm text-gray-500">Smart Book Recommender</nav>
          </div>
        </header>

        <div className="flex-1">{children}</div>

        <footer className="border-t bg-white mt-16">
          <div className="max-w-6xl mx-auto px-6 py-6 text-center text-sm text-gray-500">Smart Book Recommender &mdash; Hada, July 2026</div>
        </footer>
      </body>
    </html>
  );
}
