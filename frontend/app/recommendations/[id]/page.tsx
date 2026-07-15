'use client';

import { Suspense, useEffect, useReducer, use } from 'react';
import Link from 'next/link';
import { ArrowLeft, BookOpen, User, ChevronRight } from 'lucide-react';
import RecommendationCard from '../../../components/RecommendationCard';
import { API_BASE, apiFetch, getGenreColor, type RecBook } from '../../../src/lib/api';

interface BookDetail {
  bookId: number;
  title: string;
  author: string;
  genres?: string;
  description?: string;
  error?: string;
}

type State = {
  book: BookDetail | null;
  recommendations: RecBook[];
  loading: boolean;
  recLoading: boolean;
  recFetched: boolean;
};

type Action =
  | { type: 'BOOK_LOADED'; payload: BookDetail | null }
  | { type: 'RECS_START' }
  | { type: 'RECS_LOADED'; payload: RecBook[] };

const initialState: State = {
  book: null,
  recommendations: [],
  loading: true,
  recLoading: false,
  recFetched: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'BOOK_LOADED':
      return { ...state, book: action.payload, loading: false };
    case 'RECS_START':
      return { ...state, recLoading: true };
    case 'RECS_LOADED':
      return { ...state, recommendations: action.payload, recLoading: false, recFetched: true };
  }
}

function BookDetailContent({ id }: { id: string }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    let cancelled = false;
    apiFetch(`${API_BASE}/books/${id}`)
      .then((res) => res.json())
      .then((data) => { if (!cancelled) dispatch({ type: 'BOOK_LOADED', payload: data }); })
      .catch(() => { if (!cancelled) dispatch({ type: 'BOOK_LOADED', payload: null }); });
    return () => { cancelled = true; };
  }, [id]);

  useEffect(() => {
    if (!state.book?.title || state.recFetched) return;
    let cancelled = false;
    dispatch({ type: 'RECS_START' });
    apiFetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: state.book.title }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) dispatch({ type: 'RECS_LOADED', payload: Array.isArray(data.recommendations) ? data.recommendations : [] });
      })
      .catch(() => { if (!cancelled) dispatch({ type: 'RECS_LOADED', payload: [] }); });
    return () => { cancelled = true; };
  }, [state.book?.title, state.recFetched]);

  if (state.loading) {
    return (
      <main className="max-w-6xl mx-auto px-6 pt-8">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-100 rounded w-32" />
          <div className="h-8 bg-gray-100 rounded w-2/3" />
          <div className="h-4 bg-gray-100 rounded w-1/4" />
          <div className="h-20 bg-gray-100 rounded w-full mt-6" />
        </div>
      </main>
    );
  }

  if (!state.book || state.book.error) {
    return (
      <main className="max-w-6xl mx-auto px-6 pt-8 text-center py-20">
        <BookOpen className="size-16 text-gray-200 mx-auto mb-4" />
        <p className="text-gray-400 text-lg">Buku tidak ditemukan.</p>
        <Link href="/" className="text-amber-600 hover:text-amber-700 text-sm font-medium mt-4 inline-block">
          Kembali ke beranda
        </Link>
      </main>
    );
  }

  const genres = state.book.genres
    ? [...new Set(state.book.genres.split(',').map((g) => g.trim()))].filter(Boolean)
    : [];

  return (
    <main className="max-w-6xl mx-auto px-6 pt-8 pb-16">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-gray-400 mb-6">
        <Link href="/" className="hover:text-amber-600 transition-colors">Beranda</Link>
        <ChevronRight className="size-3" />
        <span className="text-gray-600">Detail Buku</span>
      </nav>

      {/* Book Info */}
      <section className="bg-white rounded-2xl border border-gray-200 p-8">
        <div className="flex flex-col sm:flex-row gap-6">
          <div className="shrink-0 size-20 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100 flex items-center justify-center">
            <BookOpen className="size-10 text-amber-500" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 leading-tight">{state.book.title}</h1>
            <p className="text-gray-500 mt-2 flex items-center gap-1.5">
              <User className="size-4" />
              {state.book.author}
            </p>

            {genres.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-4">
                {genres.map((g) => (
                  <span key={g} className={`text-xs font-medium px-2.5 py-1 rounded-full border ${getGenreColor(g)}`}>
                    {g}
                  </span>
                ))}
              </div>
            )}

            {state.book.description && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Deskripsi</h3>
                <p className="text-gray-600 leading-relaxed text-sm max-w-3xl">{state.book.description}</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Similar Books */}
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-900 mb-5">Buku Serupa</h2>
        {state.recLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="border border-gray-200 rounded-xl p-5 bg-white animate-pulse">
                <div className="flex items-start gap-3">
                  <div className="size-10 rounded-lg bg-gray-100" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-100 rounded w-3/4" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : state.recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {state.recommendations.map((rec, i) => (
              <RecommendationCard
                key={i}
                title={rec.title}
                author={rec.author}
                similarity={rec.similarity}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Tidak ada rekomendasi tersedia.</p>
        )}
      </section>

      {/* Back link */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-amber-600 transition-colors mt-10"
      >
        <ArrowLeft className="size-4" />
        Kembali ke beranda
      </Link>
    </main>
  );
}

export default function BookDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <Suspense fallback={<main className="max-w-6xl mx-auto px-6 pt-8"><p className="text-gray-400">Memuat...</p></main>}>
      <BookDetailContent id={id} />
    </Suspense>
  );
}
