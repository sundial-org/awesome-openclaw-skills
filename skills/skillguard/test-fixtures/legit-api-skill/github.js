/**
 * GitHub Issues API wrapper
 * Requires GITHUB_TOKEN env var
 */

const API_BASE = 'https://api.github.com';

export async function listIssues(owner, repo, state = 'open') {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('GITHUB_TOKEN not set');

  const response = await fetch(`${API_BASE}/repos/${owner}/${repo}/issues?state=${state}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'SkillGuard-Test',
    },
  });

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
  }

  const issues = await response.json();
  return issues.map(issue => ({
    number: issue.number,
    title: issue.title,
    state: issue.state,
    author: issue.user?.login,
    labels: issue.labels?.map(l => l.name),
    created: issue.created_at,
    url: issue.html_url,
  }));
}

export async function createIssue(owner, repo, title, body, labels = []) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('GITHUB_TOKEN not set');

  const response = await fetch(`${API_BASE}/repos/${owner}/${repo}/issues`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'SkillGuard-Test',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, body, labels }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create issue: ${response.status}`);
  }

  return response.json();
}

export async function closeIssue(owner, repo, issueNumber) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('GITHUB_TOKEN not set');

  const response = await fetch(`${API_BASE}/repos/${owner}/${repo}/issues/${issueNumber}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ state: 'closed' }),
  });

  return response.json();
}
