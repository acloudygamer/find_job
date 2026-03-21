import { useState, useEffect } from "react";
import { Modal, Button, Input } from "../../components/ui";
import { githubApi, moduleApi } from "../../api";
import type { GitHubRepo, GeneratedModuleData } from "../../api/types";

interface GitHubImportModalProps {
  open: boolean;
  resumeId: string;
  onClose: () => void;
  onSuccess: () => void;
  showToast: (msg: string, type: "success" | "error") => void;
}

type Step = "input" | "select" | "preview" | "importing";

export default function GitHubImportModal({
  open,
  resumeId,
  onClose,
  onSuccess,
  showToast,
}: GitHubImportModalProps) {
  const [step, setStep] = useState<Step>("input");
  const [username, setUsername] = useState("");
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const [repoError, setRepoError] = useState<string | null>(null);

  const [selectedRepo, setSelectedRepo] = useState<GitHubRepo | null>(null);
  const [readmeContent, setReadmeContent] = useState("");
  const [loadingReadme, setLoadingReadme] = useState(false);

  const [generatedData, setGeneratedData] =
    useState<GeneratedModuleData | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const [importing, setImporting] = useState(false);

  useEffect(() => {
    if (!open) {
      setStep("input");
      setUsername("");
      setRepos([]);
      setSelectedRepo(null);
      setReadmeContent("");
      setGeneratedData(null);
      setRepoError(null);
      setGenerateError(null);
    }
  }, [open]);

  const handleFetchRepos = async () => {
    if (!username.trim()) return;
    setLoadingRepos(true);
    setRepoError(null);
    try {
      const data = await githubApi.listRepos(username.trim());
      setRepos(data);
      if (data.length === 0) {
        setRepoError("No repositories found for this user (or all are forks)");
      }
      setStep("select");
    } catch (err) {
      setRepoError(
        err instanceof Error ? err.message : "Failed to fetch repositories",
      );
    } finally {
      setLoadingRepos(false);
    }
  };

  const handleSelectRepo = async (repo: GitHubRepo) => {
    setSelectedRepo(repo);
    setLoadingReadme(true);
    try {
      const readme = await githubApi.getReadme(repo.owner.login, repo.name);
      setReadmeContent(readme.content);
    } catch {
      setReadmeContent("");
    } finally {
      setLoadingReadme(false);
    }
    // Auto-generate module data
    setGenerating(true);
    setGenerateError(null);
    try {
      const data = await githubApi.generateModule(
        repo.name,
        readmeContent || repo.description || "",
      );
      setGeneratedData(data);
      setStep("preview");
    } catch (err) {
      setGenerateError(
        err instanceof Error ? err.message : "Failed to generate module",
      );
      setGeneratedData(null);
      setStep("preview");
    } finally {
      setGenerating(false);
    }
  };

  const handleImport = async () => {
    if (!generatedData) return;
    setImporting(true);
    try {
      // Create project module
      const module = await moduleApi.create(resumeId, {
        module_type: "project",
        title: generatedData.title,
        content: generatedData.content,
        order_index: 999,
      });
      // Create fields
      for (const field of generatedData.fields) {
        await fetch(`/api/modules/${module.id}/fields`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            key: field.key,
            value: field.value,
            field_type: field.field_type,
            order_index: 0,
          }),
        });
      }
      showToast("GitHub project imported successfully!", "success");
      onSuccess();
      onClose();
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "Failed to import",
        "error",
      );
    } finally {
      setImporting(false);
    }
  };

  return (
    <Modal
      open={open}
      title="Import from GitHub"
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          {step === "select" && (
            <Button onClick={() => setStep("input")}>Back</Button>
          )}
        </>
      }
    >
      {/* Step 1: Username input */}
      {step === "input" && (
        <div className="flex flex-col gap-4">
          <p className="text-sm text-gray-500">
            Enter your GitHub username to see your repositories and import them
            as project modules.
          </p>
          <Input
            label="GitHub Username"
            placeholder="e.g. acloudygamer"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleFetchRepos()}
            autoFocus
          />
          {repoError && <p className="text-sm text-red-500">{repoError}</p>}
          <Button
            onClick={handleFetchRepos}
            loading={loadingRepos}
            disabled={!username.trim()}
          >
            Fetch Repositories
          </Button>
        </div>
      )}

      {/* Step 2: Repo selection */}
      {step === "select" && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-gray-500">
            Select a repository to import ({repos.length} found):
          </p>
          <div className="max-h-72 overflow-y-auto space-y-2">
            {repos.map((repo) => (
              <button
                key={repo.name}
                onClick={() => handleSelectRepo(repo)}
                disabled={loadingReadme}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-colors disabled:opacity-50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 truncate">
                        {repo.name}
                      </span>
                      {repo.language && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                          {repo.language}
                        </span>
                      )}
                    </div>
                    {repo.description && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">
                        {repo.description}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400 flex-shrink-0 ml-3">
                    <span>⭐ {repo.stargazers_count}</span>
                    <svg
                      className={`w-4 h-4 ${loadingReadme && selectedRepo?.name === repo.name ? "animate-spin" : ""}`}
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
                  </div>
                </div>
              </button>
            ))}
          </div>
          {repoError && <p className="text-sm text-red-500">{repoError}</p>}
        </div>
      )}

      {/* Step 3: Preview generated module */}
      {step === "preview" && (
        <div className="flex flex-col gap-4">
          {generating && (
            <div className="text-center py-8">
              <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-3" />
              <p className="text-sm text-gray-500">
                Claude is analyzing the README...
              </p>
            </div>
          )}

          {!generating && generatedData && (
            <>
              <p className="text-sm text-gray-500">
                Review the generated module before importing:
              </p>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                <div className="font-semibold text-gray-900">
                  📄 {generatedData.title}
                </div>
                {generatedData.fields.map((field) => (
                  <div key={field.key} className="flex gap-2 text-gray-600">
                    <span className="font-medium text-gray-700 w-24 flex-shrink-0">
                      {field.key}:
                    </span>
                    <span className="flex-1 break-all">
                      {field.field_type === "list"
                        ? field.value.split("\n").map((item, i) => (
                            <span key={i} className="block ml-3">
                              • {item}
                            </span>
                          ))
                        : field.value}
                    </span>
                  </div>
                ))}
              </div>
              {generateError && (
                <p className="text-sm text-red-500 bg-red-50 p-2 rounded">
                  ⚠️ {generateError}
                </p>
              )}
              <Button onClick={handleImport} loading={importing}>
                Import to Resume
              </Button>
            </>
          )}

          {!generating && !generatedData && generateError && (
            <div className="text-center py-8">
              <p className="text-red-500 mb-3">Failed to generate module</p>
              <p className="text-sm text-gray-500 mb-4">{generateError}</p>
              <div className="flex gap-2 justify-center">
                <Button variant="secondary" onClick={() => setStep("select")}>
                  Try Another Repo
                </Button>
                <Button onClick={handleImport} loading={importing}>
                  Import Manually
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}
