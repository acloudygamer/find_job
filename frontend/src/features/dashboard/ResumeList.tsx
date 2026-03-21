import type { ResumeResponse } from '../../api/types';
import { ResumeCard } from './ResumeCard';

interface ResumeListProps {
  resumes: ResumeResponse[];
  loading: boolean;
  onEdit: (resume: ResumeResponse) => void;
  onDelete: (id: string) => void;
  onExport: (id: string) => void;
}

export function ResumeList({
  resumes,
  loading,
  onEdit,
  onDelete,
  onExport,
}: ResumeListProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (resumes.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {resumes.map((resume) => (
        <ResumeCard
          key={resume.id}
          resume={resume}
          onEdit={() => onEdit(resume)}
          onDelete={() => onDelete(resume.id)}
          onExport={() => onExport(resume.id)}
        />
      ))}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-3/4 mb-3" />
      <div className="h-3 bg-gray-100 rounded w-full mb-4" />
      <div className="flex justify-between items-center">
        <div className="h-3 bg-gray-100 rounded w-1/3" />
        <div className="flex gap-2">
          <div className="h-7 w-7 bg-gray-200 rounded" />
          <div className="h-7 w-7 bg-gray-200 rounded" />
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 mb-4 text-gray-300">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-700 mb-1">No resumes yet</h3>
      <p className="text-sm text-gray-400 max-w-xs">
        Create your first resume to get started with building your professional profile.
      </p>
    </div>
  );
}
