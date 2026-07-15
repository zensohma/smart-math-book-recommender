'use client';

import { Suspense, useEffect, useReducer, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import SearchBar from '../../components/SearchBar';
import RecommendationCard from '../../components/RecommendationCard';
import { SearchX, Filter } from 'lucide-react';
import { API_BASE, apiFetch, type Book } from '../../src/lib/api';

type State = {
  results: Book[];
  genres: string[];
  selectedGenre: string;
  loading: boolean;
  genresLoaded: boolean;
};

type Action =
  | { type: 'RESULTS_LOADED'; payload: Book[] }
  | { type: 'GENRES_LOADED'; payload: string[] }
  | { type: 'SET_GENRE'; payload: string }
  | { type: 'FETCH_START' };

const initialState: State = {
  results: [],
  genres: [],
  selectedGenre: '',
  loading: false,
  genresLoaded: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true };
    case 'RESULTS_LOADED':
      return { ...state, results: action.payload, loading: false };
    case 'GENRES_LOADED':
      return { ...state, genres: action.payload, genresLoaded: true };
    case 'SET_GENRE':
      return { ...state, selectedGenre: action.payload };
  }
}

function SearchContent() {
  const searchParams = useSearchParams();
  const q = searchParams.get('q') || '';
  const [state, dispatch] = useReducer(reducer, initialState);
  const [showAllGenres, setShowAllGenres] = useState(false);

  useEffect(() => {
    if (!q) return;
    let cancelled = false;
    dispatch({ type: 'FETCH_START' });
    apiFetch(`${API_BASE}/books?q=${encodeURIComponent(q)}`)
      .then((res) => res.json())
      .then((data) => { if (!cancelled) dispatch({ type: 'RESULTS_LOADED', payload: Array.isArray(data) ? data : [] }); })
      .catch(() => { if (!cancelled) dispatch({ type: 'RESULTS_LOADED', payload: [] }); });
    return () => { cancelled = true; };
  }, [q]);

  useEffect(() => {
    if (state.genresLoaded) return;
    let cancelled = false;
    apiFetch(`${API_BASE}/genres`)
      .then((res) => res.json())
      .then((data) => { if (!cancelled && Array.isArray(data)) dispatch({ type: 'GENRES_LOADED', payload: data }); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [state.genresLoaded]);

  const filtered = state.selectedGenre
    ? state.results.filter((b) => b.genres && b.genres.includes(state.selectedGenre))
    : state.results;

  return (
    <main className="max-w-6xl mx-auto px-6 pt-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Hasil Pencarian</h1>

      <SearchBar initialQuery={q} />

      {/* Genre Filter */}
      <div className="mt-6 bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="size-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-500">Filter Genre</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => dispatch({ type: 'SET_GENRE', payload: '' })}
            className={`text-xs font-medium px-3 py-1.5 rounded-full border transition-colors ${
              !state.selectedGenre
                ? 'bg-amber-600 text-white border-amber-600'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            Semua
          </button>
          {state.genres.slice(0, showAllGenres ? undefined : 12).map((g) => (
            <button
              key={g}
              onClick={() => dispatch({ type: 'SET_GENRE', payload: g })}
              className={`text-xs font-medium px-3 py-1.5 rounded-full border transition-colors ${
                state.selectedGenre === g
                  ? 'bg-amber-600 text-white border-amber-600'
                  : 'border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
        {state.genres.length > 12 && (
          <button
            onClick={() => setShowAllGenres(!showAllGenres)}
            className="text-xs text-amber-600 hover:text-amber-700 font-medium mt-3"
          >
            {showAllGenres ? 'Tampilkan lebih sedikit' : `Tampilkan semua (${state.genres.length})`}
          </button>
        )}
      </div>

      {/* Results */}
      <div className="mt-6 mb-16">
        {!state.loading && q && (
          <p className="text-sm text-gray-400 mb-4">
            {filtered.length} buku{state.selectedGenre ? ` dengan genre "${state.selectedGenre}"` : ''} ditemukan
          </p>
        )}

        {state.loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
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
        ) : filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((book) => (
              <RecommendationCard
                key={book.bookId}
                bookId={book.bookId}
                title={book.title}
                author={book.author}
                genres={book.genres}
                description={book.description}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <SearchX className="size-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-400">
              {q ? `Tidak ditemukan buku untuk "${q}"` : 'Masukkan kata kunci untuk mencari buku.'}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<main className="max-w-6xl mx-auto px-6 pt-8"><p className="text-gray-400">Memuat...</p></main>}>
      <SearchContent />
    </Suspense>
  );
}
