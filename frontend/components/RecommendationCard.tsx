'use client';

import Link from 'next/link';
import { BookOpen, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { getGenreColor } from '@/lib/api';

type Props = {
  bookId?: number;
  title: string;
  author: string;
  similarity?: number;
  genres?: string;
  description?: string;
};

export default function RecommendationCard({ bookId, title, author, similarity, genres, description }: Props) {
  const genreList = genres
    ? [...new Set(genres.split(",").map((g) => g.trim()))].filter(Boolean).slice(0, 4)
    : [];

  const content = (
    <div className="group border border-gray-200 rounded-xl p-5 bg-white hover:shadow-lg hover:border-amber-200 transition-all duration-200">
      <div className="flex items-start gap-3">
        <div className="shrink-0 size-10 rounded-lg bg-amber-50 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
          <BookOpen className="size-5 text-amber-600" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-base leading-tight line-clamp-2 group-hover:text-amber-700 transition-colors">{title}</h3>
          <p className="text-sm text-gray-600 mt-0.5 flex items-center gap-1">
            <User className="size-3" />
            {author}
          </p>
        </div>
      </div>

      {similarity !== undefined && (
        <div className="mt-3">
          <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 text-xs font-medium">
            {similarity.toFixed(1)}% match
          </Badge>
        </div>
      )}

      {genreList.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {genreList.map((g) => (
            <span key={g} className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${getGenreColor(g)}`}>
              {g}
            </span>
          ))}
        </div>
      )}

      {description && (
        <p className="text-xs text-gray-500 mt-3 line-clamp-2 leading-relaxed">{description}</p>
      )}
    </div>
  );

  if (bookId) {
    return <Link href={`/recommendations/${bookId}`}>{content}</Link>;
  }

  return content;
}
