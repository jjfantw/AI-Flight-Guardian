import { Octokit } from '@octokit/rest';

export const getCredentials = () => {
  const token = localStorage.getItem('gh_pat');
  const owner = localStorage.getItem('gh_owner') || 'jjfantw';
  const repo = localStorage.getItem('gh_repo') || 'AI-Flight-Guardian';
  return { token, owner, repo };
};

export const fetchTasks = async () => {
  const { token, owner, repo } = getCredentials();
  
  // Use API if token exists to avoid caching issues, otherwise use raw githubusercontent
  if (token) {
    const octokit = new Octokit({ auth: token });
    try {
      const response = await octokit.rest.repos.getContent({
        owner,
        repo,
        path: 'tasks.json',
      });
      const content = atob(response.data.content);
      return JSON.parse(content);
    } catch (e) {
      console.error("Failed to fetch via API, falling back or returning empty", e);
      return { tasks: [] };
    }
  } else {
    // Fallback for public viewing without token
    const res = await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/main/tasks.json`);
    if (!res.ok) return { tasks: [] };
    return await res.json();
  }
};

export const fetchRecords = async (taskId) => {
  const { token, owner, repo } = getCredentials();
  let csvText = '';
  
  if (token) {
    const octokit = new Octokit({ auth: token });
    try {
      const response = await octokit.rest.repos.getContent({
        owner,
        repo,
        path: `records/${taskId}.csv`,
      });
      csvText = decodeURIComponent(escape(atob(response.data.content))); // handle utf-8
    } catch (e) {
      console.error(`Failed to fetch records for ${taskId}`, e);
      return null;
    }
  } else {
    const res = await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/main/records/${taskId}.csv`);
    if (!res.ok) return null;
    csvText = await res.text();
  }
  
  return csvText;
};

export const commitTasks = async (tasksData) => {
  const { token, owner, repo } = getCredentials();
  if (!token) throw new Error("GitHub PAT is required to save tasks.");
  
  const octokit = new Octokit({ auth: token });
  const path = 'tasks.json';
  
  // 1. Get current file SHA
  let sha;
  try {
    const { data } = await octokit.rest.repos.getContent({
      owner,
      repo,
      path,
    });
    sha = data.sha;
  } catch (e) {
    console.log("File might not exist yet, continuing without SHA", e);
  }
  
  // 2. Update file
  const content = btoa(JSON.stringify(tasksData, null, 2));
  await octokit.rest.repos.createOrUpdateFileContents({
    owner,
    repo,
    path,
    message: 'Update tasks.json via Flight Guardian Dashboard',
    content,
    sha,
  });
};

export const fetchWorkflow = async () => {
  const { token, owner, repo } = getCredentials();
  if (!token) return null; // Requires auth

  const octokit = new Octokit({ auth: token });
  try {
    const response = await octokit.rest.repos.getContent({
      owner,
      repo,
      path: '.github/workflows/scraper.yml',
    });
    const parsed = decodeURIComponent(escape(atob(response.data.content)));
    return { content: parsed, sha: response.data.sha };
  } catch (e) {
    console.error("Failed to fetch workflow:", e);
    return null;
  }
};

export const commitWorkflow = async (workflowContent, sha) => {
  const { token, owner, repo } = getCredentials();
  if (!token) throw new Error("GitHub PAT is required.");
  
  const octokit = new Octokit({ auth: token });
  const encodedContent = btoa(unescape(encodeURIComponent(workflowContent)));
  
  await octokit.rest.repos.createOrUpdateFileContents({
    owner,
    repo,
    path: '.github/workflows/scraper.yml',
    message: 'chore: update scrap schedule times via Dashboard',
    content: encodedContent,
    sha,
  });
};
