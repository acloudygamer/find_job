import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useResumeStore } from '../../store/resumeStore';
import { useToast, Button, Input, Modal } from '../../components/ui';
import { ResumeList } from './ResumeList';
import type { ResumeCreate, ResumeUpdate, ResumeResponse } from '../../api/types';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const {
    resumes,
    loading,
    error,
    fetchResumes,
    createResume,
    updateResume,
    deleteResume,
    exportResume,
    clearError,
  } = useResumeStore();

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingResume, setEditingResume] = useState<ResumeResponse | null>(null);
  const [formData, setFormData] = useState<{ name: string; description: string }>({
    name: '',
    description: '',
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Delete confirmation
  const [deleteId, setDeleteId] = useState<string | null>(null);

  // Export format
  const [exportingId, setExportingId] = useState<string | null>(null);

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  useEffect(() => {
    if (error) {
      showToast(error, 'error');
      clearError();
    }
  }, [error, clearError, showToast]);

  const openCreateModal = () => {
    setEditingResume(null);
    setFormData({ name: '', description: '' });
    setFormError(null);
    setModalOpen(true);
  };

  const openEditModal = (resume: ResumeResponse) => {
    setEditingResume(resume);
    setFormData({ name: resume.name, description: resume.description ?? '' });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setFormError('Name is required');
      return;
    }
    setSubmitting(true);
    try {
      if (editingResume) {
        const data: ResumeUpdate = {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
        };
        await updateResume(editingResume.id, data);
        showToast('Resume updated', 'success');
      } else {
        const data: ResumeCreate = {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
        };
        const created = await createResume(data);
        showToast('Resume created', 'success');
        navigate(`/resume/${created.id}`);
      }
      setModalOpen(false);
    } catch {
      setFormError('Failed to save resume');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteResume(deleteId);
      showToast('Resume deleted', 'success');
    } catch {
      showToast('Failed to delete resume', 'error');
    }
    setDeleteId(null);
  };

  const handleExport = async (id: string, format: 'json' | 'markdown' = 'markdown') => {
    setExportingId(id);
    try {
      const content = await exportResume(id, format);
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume-${id}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Resume exported', 'success');
    } catch {
      showToast('Failed to export resume', 'error');
    } finally {
      setExportingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-gray-900">find_job</h1>
            </div>
            <Button onClick={openCreateModal} size="sm">
              + New Resume
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">My Resumes</h2>
          <p className="text-sm text-gray-500 mt-1">
            {resumes.length > 0
              ? `${resumes.length} resume${resumes.length > 1 ? 's' : ''}`
              : 'Get started by creating your first resume'}
          </p>
        </div>

        <ResumeList
          resumes={resumes}
          loading={loading}
          onEdit={openEditModal}
          onDelete={(id) => setDeleteId(id)}
          onExport={(id) => handleExport(id)}
        />
      </main>

      {/* Create / Edit Modal */}
      <Modal
        open={modalOpen}
        title={editingResume ? 'Edit Resume' : 'Create Resume'}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} loading={submitting}>
              {editingResume ? 'Save' : 'Create'}
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-4">
          <Input
            label="Name"
            placeholder="e.g. Software Engineer Resume"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
            error={formError ?? undefined}
            autoFocus
          />
          <Input
            label="Description"
            placeholder="Brief description of this resume (optional)"
            value={formData.description}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, description: e.target.value }))
            }
          />
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        open={deleteId !== null}
        title="Delete Resume"
        onClose={() => setDeleteId(null)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-gray-600 text-sm">
          Are you sure you want to delete this resume? This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
}
