'use client';

import { useEffect, useState } from 'react';
import SearchBar from '../components/SearchBar';
import RecommendationCard from '../components/RecommendationCard';
import { Sparkles, TrendingUp } from 'lucide-react';
import { API_BASE, apiFetch, type Book, type RecBook } from '../src/lib/api';

function SkeletonCard() {
  return (
    <div className="border border-gray-200 rounded-xl p-5 bg-white animate-pulse">
      <div className="flex items-start gap-3">
        <div className="size-10 rounded-lg bg-gray-100" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-100 rounded w-3/4" />
          <div className="h-3 bg-gray-100 rounded w-1/2" />
        </div>
      </div>
      <div className="mt-3 flex gap-1.5">
        <div className="h-5 bg-gray-100 rounded-full w-16" />
        <div className="h-5 bg-gray-100 rounded-full w-20" />
      </div>
    </div>
  );
}

export default function Home() {
  const [popularBooks, setPopularBooks] = useState<Book[]>([]);
  const [featuredBook, setFeaturedBook] = useState<Book | null>(null);
  const [recommendedBooks, setRecommendedBooks] = useState<RecBook[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const [popRes, featRes] = await Promise.allSettled([
        apiFetch(`${API_BASE}/books/popular?limit=6`),
        apiFetch(`${API_BASE}/recommend/featured`),
      ]);
      if (cancelled) return;
      if (popRes.status === 'fulfilled') {
        const data = await popRes.value.json();
        if (Array.isArray(data)) setPopularBooks(data);
      }
      if (featRes.status === 'fulfilled') {
        const data = await featRes.value.json();
        setFeaturedBook(data.book ?? null);
        if (Array.isArray(data.recommendations)) setRecommendedBooks(data.recommendations);
      }
      setLoading(false);
    }
    load();
    return () => { cancelled = true; };
  }, []);

  return (
    <main>
      {/* Hero */}
      <section className="bg-gradient-to-br from-amber-50 via-white to-orange-50 border-b">
        <div className="max-w-4xl mx-auto px-6 pt-16 pb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight">
            Smart Mathematics
            <br />
            <span className="text-amber-600">Book Recommender</span>
          </h1>
          <p className="mt-4 text-gray-500 text-lg max-w-xl mx-auto">
            Temukan buku matematika yang relevan berdasarkan minat dan topik yang kamu pelajari.
          </p>
          <div className="mt-8 max-w-lg mx-auto">
            <SearchBar />
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-6">
        {/* Rekomendasi Untukmu */}
        {featuredBook && recommendedBooks.length > 0 && (
          <section className="mt-12">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="size-5 text-amber-500" />
              <h2 className="text-xl font-bold text-gray-900">Rekomendasi Untukmu</h2>
            </div>
            <p className="text-sm text-gray-500 mb-5 ml-7">
              Karena kamu suka <span className="font-medium text-gray-600">{featuredBook.title}</span> oleh {featuredBook.author}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendedBooks.map((book, i) => (
                <RecommendationCard
                  key={i}
                  bookId={book.bookId}
                  title={book.title}
                  author={book.author}
                  similarity={book.similarity}
                />
              ))}
            </div>
          </section>
        )}

        {/* Buku Populer */}
        <section className="mt-12 mb-16">
          <div className="flex items-center gap-2 mb-5">
            <TrendingUp className="size-5 text-amber-500" />
            <h2 className="text-xl font-bold text-gray-900">Buku Populer</h2>
          </div>
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {popularBooks.map((book) => (
                <RecommendationCard
                  key={book.bookId}
                  bookId={book.bookId}
                  title={book.title}
                  author={book.author}
                  genres={book.genres}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
