import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ResumeResponse } from '../../api/types';
import { Badge, Button } from '../../components/ui';
import { formatDistanceToNow } from '../../utils/date';

interface ResumeCardProps {
  resume: ResumeResponse;
  onEdit: () => void;
  onDelete: () => void;
  onExport: () => void;
}

export function ResumeCard({
  resume,
  onEdit,
  onDelete,
  onExport,
}: ResumeCardProps) {
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const handleCardClick = () => {
    navigate(`/resume/${resume.id}`);
  };

  const createdAgo = formatDistanceToNow(new Date(resume.created_at));

  return (
    <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-primary-200 transition-all duration-150">
      <div className="px-5 py-4 cursor-pointer" onClick={handleCardClick}>
        {/* Title row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="text-base font-semibold text-gray-900 truncate flex-1">
            {resume.name}
          </h3>
          <Badge variant="primary">Resume</Badge>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-500 line-clamp-2 mb-3 min-h-[2.5rem]">
          {resume.description || 'No description'}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">{createdAgo}</span>
          <div
            className="flex items-center gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
              title="Edit"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu((v) => !v);
              }}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors relative"
              title="More"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01" />
              </svg>
            </button>

            {showMenu && (
              <div className="absolute right-0 mt-8 z-10 w-36 bg-white border border-gray-200 rounded-lg shadow-lg py-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onExport();
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Export
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
