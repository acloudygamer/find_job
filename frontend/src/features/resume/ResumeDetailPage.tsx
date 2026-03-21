import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useResumeStore } from "../../store/resumeStore";
import { useToast, Button, Input, Modal, Badge } from "../../components/ui";
import type {
  ModuleCreate,
  ModuleUpdate,
  ModuleResponse,
  FieldCreate,
  FieldUpdate,
  FieldResponse,
} from "../../api/types";
import { formatDistanceToNow } from "../../utils/date";
import GitHubImportModal from "../github/GitHubImportModal";

// ── Module types with their default fields ─────────────────────────────────────

const MODULE_TEMPLATES: Record<
  string,
  { label: string; defaultFields: string[] }
> = {
  education: {
    label: "Education",
    defaultFields: ["School", "Degree", "Major", "Date Range", "GPA"],
  },
  experience: {
    label: "Experience",
    defaultFields: ["Company", "Position", "Date Range", "Description"],
  },
  project: {
    label: "Project",
    defaultFields: ["Name", "Role", "Date Range", "Description", "Tech Stack"],
  },
  skills: { label: "Skills", defaultFields: ["Skill Category", "Skills"] },
  about: { label: "About", defaultFields: ["Summary"] },
  custom: { label: "Custom", defaultFields: [] },
};

// ── Module Card ────────────────────────────────────────────────────────────────

interface ModuleCardProps {
  module: ModuleResponse;
  onUpdate: (id: string, data: ModuleUpdate) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onAddField: (moduleId: string, data: FieldCreate) => Promise<FieldResponse>;
  onUpdateField: (id: string, data: FieldUpdate) => Promise<void>;
  onDeleteField: (id: string) => Promise<void>;
  showToast: (msg: string, type: "success" | "error") => void;
}

function ModuleCard({
  module,
  onUpdate,
  onDelete,
  onAddField,
  onUpdateField,
  onDeleteField,
  showToast,
}: ModuleCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [loadingFields, setLoadingFields] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleValue, setTitleValue] = useState(module.title);
  const [titleSaving, setTitleSaving] = useState(false);

  const [fieldModalOpen, setFieldModalOpen] = useState(false);
  const [editingField, setEditingField] = useState<FieldResponse | null>(null);
  const [fieldForm, setFieldForm] = useState({
    key: "",
    value: "",
    field_type: "text",
  });
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [fieldSaving, setFieldSaving] = useState(false);

  const [deleteFieldId, setDeleteFieldId] = useState<string | null>(null);

  const { fetchFields } = useResumeStore();

  useEffect(() => {
    if (expanded && fields.length === 0) {
      setLoadingFields(true);
      fetchFields(module.id)
        .then(() => {
          const { currentFields } = useResumeStore.getState();
          setFields(currentFields);
        })
        .catch(() => showToast("Failed to load fields", "error"))
        .finally(() => setLoadingFields(false));
    }
  }, [expanded]);

  // Keep fields in sync when store changes
  useEffect(() => {
    if (expanded) {
      const { currentFields } = useResumeStore.getState();
      setFields(currentFields);
    }
  }, [useResumeStore.getState().currentFields]);

  const handleTitleSave = async () => {
    if (!titleValue.trim()) return;
    setTitleSaving(true);
    try {
      await onUpdate(module.id, { title: titleValue.trim() });
      setEditingTitle(false);
      showToast("Title updated", "success");
    } catch {
      showToast("Failed to update title", "error");
    } finally {
      setTitleSaving(false);
    }
  };

  const handleDeleteModule = async () => {
    try {
      await onDelete(module.id);
      showToast("Module deleted", "success");
    } catch {
      showToast("Failed to delete module", "error");
    }
  };

  const openAddField = () => {
    setEditingField(null);
    setFieldForm({ key: "", value: "", field_type: "text" });
    setFieldError(null);
    setFieldModalOpen(true);
  };

  const openEditField = (field: FieldResponse) => {
    setEditingField(field);
    setFieldForm({
      key: field.key,
      value: field.value,
      field_type: field.field_type,
    });
    setFieldError(null);
    setFieldModalOpen(true);
  };

  const handleFieldSubmit = async () => {
    if (!fieldForm.key.trim()) {
      setFieldError("Field name is required");
      return;
    }
    setFieldSaving(true);
    try {
      if (editingField) {
        await onUpdateField(editingField.id, {
          key: fieldForm.key.trim(),
          value: fieldForm.value,
          field_type: fieldForm.field_type,
        });
        setFields((prev) =>
          prev.map((f) =>
            f.id === editingField.id
              ? {
                  ...f,
                  key: fieldForm.key.trim(),
                  value: fieldForm.value,
                  field_type: fieldForm.field_type,
                }
              : f,
          ),
        );
        showToast("Field updated", "success");
      } else {
        const created = await onAddField(module.id, {
          key: fieldForm.key.trim(),
          value: fieldForm.value,
          field_type: fieldForm.field_type,
          order_index: fields.length,
        });
        setFields((prev) => [...prev, created]);
        showToast("Field added", "success");
      }
      setFieldModalOpen(false);
    } catch {
      showToast("Failed to save field", "error");
    } finally {
      setFieldSaving(false);
    }
  };

  const handleDeleteField = async () => {
    if (!deleteFieldId) return;
    try {
      await onDeleteField(deleteFieldId);
      setFields((prev) => prev.filter((f) => f.id !== deleteFieldId));
      showToast("Field deleted", "success");
    } catch {
      showToast("Failed to delete field", "error");
    }
    setDeleteFieldId(null);
  };

  const template = MODULE_TEMPLATES[module.module_type];

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
        {/* Module header */}
        <div
          className="flex items-center justify-between px-5 py-4 cursor-pointer select-none"
          onClick={() => setExpanded((v) => !v)}
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <svg
              className={`w-4 h-4 text-gray-400 flex-shrink-0 transition-transform ${expanded ? "rotate-90" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
            {editingTitle ? (
              <input
                className="text-base font-semibold text-gray-900 border border-primary-300 rounded px-2 py-0.5 flex-1 min-w-0 outline-none focus:ring-2 focus:ring-primary-200"
                value={titleValue}
                onChange={(e) => setTitleValue(e.target.value)}
                onBlur={handleTitleSave}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleTitleSave();
                  if (e.key === "Escape") {
                    setTitleValue(module.title);
                    setEditingTitle(false);
                  }
                }}
                onClick={(e) => e.stopPropagation()}
                autoFocus
              />
            ) : (
              <span className="text-base font-semibold text-gray-900 truncate">
                {module.title}
              </span>
            )}
            <Badge variant="secondary">
              {template?.label ?? module.module_type}
            </Badge>
          </div>

          <div
            className="flex items-center gap-1 flex-shrink-0 ml-3"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={(e) => {
                e.stopPropagation();
                setTitleValue(module.title);
                setEditingTitle(true);
              }}
              className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
              title="Edit title"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteModule();
              }}
              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              title="Delete module"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Fields section */}
        {expanded && (
          <div className="border-t border-gray-100 px-5 py-4">
            {loadingFields ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-10 bg-gray-100 rounded animate-pulse"
                  />
                ))}
              </div>
            ) : fields.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-gray-400 text-sm mb-3">No fields yet</p>
                <Button size="sm" variant="secondary" onClick={openAddField}>
                  + Add Field
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {fields.map((field) => (
                  <div
                    key={field.id}
                    className="flex items-start gap-2 group hover:bg-gray-50 rounded-lg px-2 py-1.5 -mx-2 transition-colors"
                  >
                    <div className="flex-1 min-w-0 grid grid-cols-[120px_1fr] gap-x-3">
                      <span className="text-xs font-medium text-gray-500 truncate pt-1">
                        {field.key}
                      </span>
                      <span className="text-sm text-gray-800 truncate pt-0.5">
                        {field.value || (
                          <span className="text-gray-300 italic">empty</span>
                        )}
                      </span>
                    </div>
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                      <button
                        onClick={() => openEditField(field)}
                        className="p-1 text-gray-400 hover:text-primary-600 rounded"
                        title="Edit field"
                      >
                        <svg
                          className="w-3.5 h-3.5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={() => setDeleteFieldId(field.id)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Delete field"
                      >
                        <svg
                          className="w-3.5 h-3.5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
                <button
                  onClick={openAddField}
                  className="mt-2 text-sm text-gray-400 hover:text-primary-600 flex items-center gap-1 transition-colors"
                >
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Add field
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add/Edit Field Modal */}
      <Modal
        open={fieldModalOpen}
        title={editingField ? "Edit Field" : "Add Field"}
        onClose={() => setFieldModalOpen(false)}
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setFieldModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleFieldSubmit} loading={fieldSaving}>
              {editingField ? "Save" : "Add"}
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-4">
          <Input
            label="Field Name"
            placeholder="e.g. School, Company, Position"
            value={fieldForm.key}
            onChange={(e) =>
              setFieldForm((p) => ({ ...p, key: e.target.value }))
            }
            error={fieldError ?? undefined}
            autoFocus
          />
          <Input
            label="Value"
            placeholder="Field value"
            value={fieldForm.value}
            onChange={(e) =>
              setFieldForm((p) => ({ ...p, value: e.target.value }))
            }
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Type
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-300"
              value={fieldForm.field_type}
              onChange={(e) =>
                setFieldForm((p) => ({ ...p, field_type: e.target.value }))
              }
            >
              <option value="text">Text</option>
              <option value="date">Date</option>
              <option value="url">URL</option>
              <option value="list">List</option>
            </select>
          </div>
        </div>
      </Modal>

      {/* Delete Field Confirmation */}
      <Modal
        open={deleteFieldId !== null}
        title="Delete Field"
        onClose={() => setDeleteFieldId(null)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteFieldId(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteField}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-gray-600 text-sm">
          Delete this field? This cannot be undone.
        </p>
      </Modal>
    </>
  );
}

// ── Add Module Modal ───────────────────────────────────────────────────────────

interface AddModuleModalProps {
  open: boolean;
  resumeId: string;
  onClose: () => void;
  onCreate: (resumeId: string, data: ModuleCreate) => Promise<ModuleResponse>;
  showToast: (msg: string, type: "success" | "error") => void;
}

function AddModuleModal({
  open,
  resumeId,
  onClose,
  onCreate,
  showToast,
}: AddModuleModalProps) {
  const [moduleType, setModuleType] = useState("custom");
  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      setModuleType("custom");
      setTitle("");
    }
  }, [open]);

  const handleSubmit = async () => {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await onCreate(resumeId, {
        module_type: moduleType,
        title: title.trim(),
        content: {},
        order_index: 0,
      });
      showToast("Module added", "success");
      onClose();
    } catch {
      showToast("Failed to add module", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleTypeChange = (type: string) => {
    setModuleType(type);
    const tmpl = MODULE_TEMPLATES[type];
    if (tmpl && type !== "custom") {
      setTitle(tmpl.label);
    } else {
      setTitle("");
    }
  };

  return (
    <Modal
      open={open}
      title="Add Module"
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            loading={saving}
            disabled={!title.trim()}
          >
            Add
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Module Type
          </label>
          <div className="grid grid-cols-3 gap-2">
            {Object.entries(MODULE_TEMPLATES).map(([key, val]) => (
              <button
                key={key}
                onClick={() => handleTypeChange(key)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  moduleType === key
                    ? "border-primary-400 bg-primary-50 text-primary-700 font-medium"
                    : "border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50"
                }`}
              >
                {val.label}
              </button>
            ))}
          </div>
        </div>
        <Input
          label="Title"
          placeholder="e.g. Work Experience"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
    </Modal>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function ResumeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const {
    currentResume,
    currentModules,
    loading,
    error,
    fetchModules,
    createModule,
    updateModule,
    deleteModule,
    updateField,
    createField,
    deleteField,
    exportResume,
    clearError,
  } = useResumeStore();

  const [addModuleOpen, setAddModuleOpen] = useState(false);
  const [deletingModuleId, setDeletingModuleId] = useState<string | null>(null);
  const [githubImportOpen, setGithubImportOpen] = useState(false);

  useEffect(() => {
    if (id) {
      fetchModules(id);
    }
  }, [id]);

  useEffect(() => {
    if (error) {
      showToast(error, "error");
      clearError();
    }
  }, [error]);

  const handleExport = async (format: "json" | "markdown" = "markdown") => {
    if (!id) return;
    try {
      const content = await exportResume(id, format);
      const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `resume-${id}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Exported successfully", "success");
    } catch {
      showToast("Export failed", "error");
    }
  };

  const handleDeleteModule = async (moduleId: string) => {
    await deleteModule(moduleId);
  };

  const handleCreateModule = async (resumeId: string, data: ModuleCreate) => {
    await createModule(resumeId, data);
  };

  const handleUpdateModule = async (moduleId: string, data: ModuleUpdate) => {
    await updateModule(moduleId, data);
  };

  const handleUpdateField = async (fieldId: string, data: FieldUpdate) => {
    await updateField(fieldId, data);
  };

  const handleAddField = async (moduleId: string, data: FieldCreate) => {
    return await createField(moduleId, data);
  };

  const handleDeleteField = async (fieldId: string) => {
    await deleteField(fieldId);
  };

  if (!id) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Invalid resume ID</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate("/")}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Back"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
              <div>
                <h1 className="text-lg font-bold text-gray-900 truncate max-w-xs">
                  {currentResume?.name ?? "Resume"}
                </h1>
                {currentResume?.description && (
                  <p className="text-xs text-gray-500 truncate max-w-xs">
                    {currentResume.description}
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleExport("markdown")}
              >
                ↓ Markdown
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleExport("json")}
              >
                ↓ JSON
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Modules section */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Modules</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              {currentModules.length > 0
                ? `${currentModules.length} module${currentModules.length > 1 ? "s" : ""}`
                : "Add your first module"}
            </p>
          </div>
          <Button size="sm" onClick={() => setAddModuleOpen(true)}>
            + Add Module
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setGithubImportOpen(true)}
          >
            <svg
              className="w-4 h-4 mr-1.5"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
            </svg>
            GitHub
          </Button>
        </div>

        {loading && currentModules.length === 0 ? (
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-20 bg-white rounded-xl animate-pulse border border-gray-200"
              />
            ))}
          </div>
        ) : currentModules.length === 0 ? (
          <div className="bg-white rounded-xl border border-dashed border-gray-300 py-16 text-center">
            <svg
              className="w-12 h-12 text-gray-300 mx-auto mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <p className="text-gray-500 mb-4">No modules yet</p>
            <Button onClick={() => setAddModuleOpen(true)}>
              + Add your first module
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {currentModules.map((module) => (
              <ModuleCard
                key={module.id}
                module={module}
                onUpdate={handleUpdateModule}
                onDelete={handleDeleteModule}
                onAddField={handleAddField}
                onUpdateField={handleUpdateField}
                onDeleteField={handleDeleteField}
                showToast={showToast}
              />
            ))}
          </div>
        )}

        {/* Footer hint */}
        {currentModules.length > 0 && (
          <p className="text-center text-xs text-gray-400 mt-6">
            Click a module to expand and manage its fields
          </p>
        )}
      </main>

      {/* Add Module Modal */}
      <AddModuleModal
        open={addModuleOpen}
        resumeId={id}
        onClose={() => setAddModuleOpen(false)}
        onCreate={handleCreateModule}
        showToast={showToast}
      />

      {/* Delete Module Confirmation */}
      <Modal
        open={deletingModuleId !== null}
        title="Delete Module"
        onClose={() => setDeletingModuleId(null)}
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setDeletingModuleId(null)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={async () => {
                if (deletingModuleId) {
                  try {
                    await handleDeleteModule(deletingModuleId);
                  } catch {}
                }
                setDeletingModuleId(null);
              }}
            >
              Delete
            </Button>
          </>
        }
      >
        <p className="text-gray-600 text-sm">
          Delete this module and all its fields? This cannot be undone.
        </p>
      </Modal>

      {/* GitHub Import Modal */}
      <GitHubImportModal
        open={githubImportOpen}
        resumeId={id}
        onClose={() => setGithubImportOpen(false)}
        onSuccess={() => {
          if (id) fetchModules(id);
        }}
        showToast={showToast}
      />
    </div>
  );
}
