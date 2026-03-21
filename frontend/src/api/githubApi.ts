import { apiClient } from "./client";
import type { GitHubRepo, ReadmeContent, GeneratedModuleData } from "./types";

export const githubApi = {
  /** GET /api/github/repos?username=xxx — List user's GitHub repos */
  listRepos: async (
    username: string,
    token?: string,
  ): Promise<GitHubRepo[]> => {
    const params: Record<string, string> = { username };
    if (token) params["token"] = token;
    const response = await apiClient.get<GitHubRepo[]>("/github/repos", {
      params,
    });
    return response.data;
  },

  /** GET /api/github/readme?owner=xxx&repo=yyy — Fetch README content */
  getReadme: async (
    owner: string,
    repo: string,
    token?: string,
  ): Promise<ReadmeContent> => {
    const params: Record<string, string> = { owner, repo };
    if (token) params["token"] = token;
    const response = await apiClient.get<ReadmeContent>("/github/readme", {
      params,
    });
    return response.data;
  },

  /** POST /api/github/generate-module — Parse README with Claude → module data */
  generateModule: async (
    repoName: string,
    readmeContent: string,
  ): Promise<GeneratedModuleData> => {
    const response = await apiClient.post<GeneratedModuleData>(
      "/github/generate-module",
      {
        repo_name: repoName,
        readme_content: readmeContent,
      },
    );
    return response.data;
  },
};
