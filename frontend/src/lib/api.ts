export interface Book {
  bookId: number;
  title: string;
  author: string;
  genres?: string;
  description?: string;
}

export interface RecBook {
  title: string;
  author: string;
  similarity?: number;
}

export const GENRE_COLORS: Record<string, string> = {
  Mathematics: 'bg-blue-100 text-blue-700 border-blue-200',
  Science: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  Physics: 'bg-purple-100 text-purple-700 border-purple-200',
  'Computer Science': 'bg-cyan-100 text-cyan-700 border-cyan-200',
  Programming: 'bg-violet-100 text-violet-700 border-violet-200',
  Engineering: 'bg-orange-100 text-orange-700 border-orange-200',
  Logic: 'bg-rose-100 text-rose-700 border-rose-200',
  Statistics: 'bg-teal-100 text-teal-700 border-teal-200',
  Calculus: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  Nonfiction: 'bg-gray-100 text-gray-600 border-gray-200',
};

export function getGenreColor(g: string) {
  return GENRE_COLORS[g] || 'bg-gray-100 text-gray-500 border-gray-200';
}

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiFetch(url: string, init?: RequestInit, timeoutMs = 10000): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}
