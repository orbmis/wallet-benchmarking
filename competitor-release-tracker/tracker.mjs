#!/usr/bin/env node
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const DEFAULT_SOURCES = resolve(ROOT, "competitor-release-tracker", "sources.json");
export const DEFAULT_STATE = resolve(ROOT, "competitor-release-tracker", "state.json");
export const DEFAULT_REPORTS_DIR = resolve(ROOT, "reports", "competitor-release-tracker");

const USER_AGENT = "WalletCompetitorReleaseTracker/1.0";
const RELEASE_TERMS = [
  "release",
  "released",
  "launch",
  "launched",
  "shipping",
  "shipped",
  "now live",
  "now available",
  "introducing",
  "announcement",
  "announcing",
  "version",
  "changelog",
];

export async function loadJson(path, fallback = undefined) {
  if (!existsSync(path)) {
    if (fallback !== undefined) return fallback;
    throw new Error(`Missing JSON file: ${path}`);
  }
  return JSON.parse(await readFile(path, "utf8"));
}

async function saveJson(path, payload) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(payload, null, 2)}\n`);
}

export async function loadSources(path = DEFAULT_SOURCES) {
  const payload = await loadJson(path);
  if (!Array.isArray(payload.competitors)) {
    throw new Error("Source file must contain a competitors array.");
  }
  for (const competitor of payload.competitors) {
    for (const key of ["id", "name", "github_repos", "x_accounts", "blog_urls"]) {
      if (!(key in competitor)) {
        throw new Error(`Competitor source is missing ${key}: ${JSON.stringify(competitor)}`);
      }
    }
  }
  return payload.competitors;
}

async function fetchText(url, headers = {}) {
  const response = await fetch(url, {
    headers: {
      "user-agent": USER_AGENT,
      accept: "text/html,text/plain,application/json,*/*;q=0.8",
      ...headers,
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 160)}`);
  }
  return { text, finalUrl: response.url, status: response.status };
}

async function fetchJson(url, headers = {}) {
  const { text } = await fetchText(url, {
    accept: "application/json",
    ...headers,
  });
  return JSON.parse(text);
}

function githubRepoSlug(repoUrl) {
  const match = repoUrl.replace(/\/$/, "").match(/^https:\/\/github\.com\/([^/]+)\/([^/#?]+)$/);
  return match ? `${match[1]}/${match[2]}` : null;
}

export async function githubLatestRelease(repoUrl, token = process.env.GITHUB_TOKEN) {
  const slug = githubRepoSlug(repoUrl);
  if (!slug) throw new Error(`Not a GitHub repository URL: ${repoUrl}`);
  const headers = token ? { authorization: `Bearer ${token}` } : {};
  try {
    const release = await fetchJson(`https://api.github.com/repos/${slug}/releases/latest`, headers);
    return normalizeGithubRelease(release, repoUrl);
  } catch (error) {
    if (!String(error.message).includes("HTTP 404")) throw error;
    const releases = await fetchJson(`https://api.github.com/repos/${slug}/releases?per_page=1`, headers);
    return releases[0] ? normalizeGithubRelease(releases[0], repoUrl) : null;
  }
}

function normalizeGithubRelease(release, repoUrl) {
  return {
    id: String(release.id ?? release.tag_name),
    title: release.name || release.tag_name || repoUrl,
    url: release.html_url || `${repoUrl.replace(/\/$/, "")}/releases`,
    publishedAt: release.published_at || release.created_at || null,
    source: repoUrl,
  };
}

async function xJson(path, bearerToken, params = {}) {
  const qs = new URLSearchParams(params);
  const url = `https://api.x.com/2${path}${qs.size ? `?${qs}` : ""}`;
  return fetchJson(url, { authorization: `Bearer ${bearerToken}` });
}

export async function xRecentReleasePosts(handle, bearerToken = process.env.X_BEARER_TOKEN, sinceId = undefined) {
  if (!bearerToken) throw new Error("X_BEARER_TOKEN is not set");
  const cleanHandle = handle.replace(/^@/, "");
  const user = await xJson(`/users/by/username/${cleanHandle}`, bearerToken);
  const params = {
    max_results: "10",
    "tweet.fields": "created_at",
    exclude: "replies,retweets",
  };
  if (sinceId) params.since_id = sinceId;
  const timeline = await xJson(`/users/${user.data.id}/tweets`, bearerToken, params);
  const tweets = timeline.data || [];
  const newestId = tweets[0]?.id || sinceId || null;
  return {
    newestId,
    releases: tweets
      .filter((tweet) => containsReleaseSignal(tweet.text || ""))
      .map((tweet) => ({
        id: tweet.id,
        title: firstLine(tweet.text || "Release announcement"),
        url: `https://x.com/${cleanHandle}/status/${tweet.id}`,
        publishedAt: tweet.created_at || null,
        source: `https://x.com/${cleanHandle}`,
      })),
  };
}

function cleanText(text) {
  return text
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, "\"")
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function pageTitle(html, fallback) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return match ? cleanText(match[1]).slice(0, 180) || fallback : fallback;
}

function hashText(text) {
  return createHash("sha256").update(cleanText(text)).digest("hex");
}

function containsReleaseSignal(text) {
  const lower = text.toLowerCase();
  return RELEASE_TERMS.some((term) => lower.includes(term));
}

function firstLine(text) {
  const line = cleanText(text).split(". ")[0] || "Release announcement";
  return line.length > 180 ? `${line.slice(0, 177)}...` : line;
}

function releaseEvent(competitor, sourceType, release) {
  return {
    competitorId: competitor.id,
    competitor: competitor.name,
    sourceType,
    title: release.title,
    url: release.url,
    publishedAt: release.publishedAt || null,
    source: release.source,
  };
}

async function checkGithub(competitor, state, client) {
  const releases = [];
  const failures = [];
  for (const repo of competitor.github_repos) {
    const key = `github:${competitor.id}:${repo}`;
    try {
      const latest = await client(repo);
      if (!latest) {
        failures.push({ competitor: competitor.name, type: "github", source: repo, error: "No GitHub releases found" });
        continue;
      }
      const previous = state.sources[key];
      if (previous && previous.latestReleaseId !== latest.id) {
        releases.push(releaseEvent(competitor, "GitHub release", latest));
      }
      state.sources[key] = { latestReleaseId: latest.id, checkedAt: new Date().toISOString(), ...latest };
    } catch (error) {
      failures.push({ competitor: competitor.name, type: "github", source: repo, error: error.message });
    }
  }
  return { releases, failures };
}

async function checkX(competitor, state, client) {
  const releases = [];
  const failures = [];
  for (const handle of competitor.x_accounts) {
    const key = `x:${competitor.id}:${handle.replace(/^@/, "")}`;
    try {
      const result = await client(handle, process.env.X_BEARER_TOKEN, state.sources[key]?.latestPostId);
      if (state.sources[key]) {
        for (const post of [...result.releases].reverse()) {
          releases.push(releaseEvent(competitor, "X announcement", post));
        }
      }
      if (result.newestId) {
        state.sources[key] = {
          latestPostId: result.newestId,
          checkedAt: new Date().toISOString(),
          source: `https://x.com/${handle.replace(/^@/, "")}`,
        };
      }
    } catch (error) {
      failures.push({ competitor: competitor.name, type: "x", source: `https://x.com/${handle}`, error: error.message });
    }
  }
  return { releases, failures };
}

async function checkBlogs(competitor, state, client) {
  const releases = [];
  const failures = [];
  for (const url of competitor.blog_urls) {
    const key = `blog:${competitor.id}:${url}`;
    try {
      const result = await client(url);
      const digest = hashText(result.text);
      const previous = state.sources[key];
      if (previous && previous.hash !== digest && containsReleaseSignal(cleanText(result.text))) {
        releases.push(
          releaseEvent(competitor, "Blog/release page", {
            title: pageTitle(result.text, result.finalUrl || url),
            url: result.finalUrl || url,
            publishedAt: null,
            source: url,
          }),
        );
      }
      state.sources[key] = {
        hash: digest,
        checkedAt: new Date().toISOString(),
        title: pageTitle(result.text, result.finalUrl || url),
        source: url,
        finalUrl: result.finalUrl || url,
      };
    } catch (error) {
      failures.push({ competitor: competitor.name, type: "blog", source: url, error: error.message });
    }
  }
  return { releases, failures };
}

export async function run(options = {}) {
  const sourcesPath = resolve(options.sourcesPath || DEFAULT_SOURCES);
  const statePath = resolve(options.statePath || DEFAULT_STATE);
  const reportsDir = resolve(options.reportsDir || DEFAULT_REPORTS_DIR);
  const now = options.now || new Date();
  const competitorFilter = options.competitorIds ? new Set(options.competitorIds) : null;
  const clients = {
    githubLatestRelease: options.githubLatestRelease || githubLatestRelease,
    xRecentReleasePosts: options.xRecentReleasePosts || xRecentReleasePosts,
    fetchText: options.fetchText || fetchText,
  };

  let competitors = await loadSources(sourcesPath);
  if (competitorFilter) competitors = competitors.filter((competitor) => competitorFilter.has(competitor.id));
  const state = await loadJson(statePath, { version: 1, sources: {} });
  state.sources ||= {};

  const releases = [];
  const failures = [];
  for (const competitor of competitors) {
    for (const result of [
      await checkGithub(competitor, state, clients.githubLatestRelease),
      await checkX(competitor, state, clients.xRecentReleasePosts),
      await checkBlogs(competitor, state, clients.fetchText),
    ]) {
      releases.push(...result.releases);
      failures.push(...result.failures);
    }
  }

  state.lastRunAt = now.toISOString();
  state.competitorCount = competitors.length;
  if (options.writeState !== false) await saveJson(statePath, state);

  await mkdir(reportsDir, { recursive: true });
  const reportPath = resolve(reportsDir, `${now.toISOString().slice(0, 10)}-wallet-releases.md`);
  await writeFile(reportPath, renderReport(now, competitors, releases, failures));
  return { reportPath, releases, failures };
}

export function renderReport(now, competitors, releases, failures) {
  const lines = [
    `# Self-Custody Wallet Competitor Releases - ${now.toISOString().slice(0, 10)}`,
    "",
    "## Summary",
    "",
    `- Competitors checked: ${competitors.length}`,
    `- New releases detected: ${releases.length}`,
    `- Source check failures: ${failures.length}`,
    "",
    "## New Releases",
    "",
  ];
  if (!releases.length) {
    lines.push("None detected.", "");
  } else {
    for (const item of [...releases].sort((a, b) => `${a.competitor}${a.sourceType}${a.title}`.localeCompare(`${b.competitor}${b.sourceType}${b.title}`))) {
      const date = item.publishedAt ? ` (${item.publishedAt})` : "";
      lines.push(
        `### ${item.competitor}`,
        "",
        `- Type: ${item.sourceType}`,
        `- Release: [${item.title}](${item.url})${date}`,
        `- Source monitored: ${item.source}`,
        "",
      );
    }
  }

  lines.push("## Source Check Failures", "");
  if (!failures.length) {
    lines.push("None.", "");
  } else {
    for (const failure of failures) {
      lines.push(`- ${failure.competitor} \`${failure.type}\` [${failure.source}](${failure.source}): ${failure.error}`);
    }
    lines.push("");
  }
  lines.push(
    "## Notes",
    "",
    "- First run establishes a baseline and normally reports no releases.",
    "- This tracker records release detection only; it does not analyze release notes.",
    "- X checks require `X_BEARER_TOKEN`; GitHub checks can use optional `GITHUB_TOKEN` for higher rate limits.",
    "",
  );
  return lines.join("\n");
}

function parseArgs(argv) {
  const args = {
    sourcesPath: DEFAULT_SOURCES,
    statePath: DEFAULT_STATE,
    reportsDir: DEFAULT_REPORTS_DIR,
    competitorIds: [],
    writeState: true,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--sources") args.sourcesPath = argv[++i];
    else if (arg === "--state") args.statePath = argv[++i];
    else if (arg === "--reports-dir") args.reportsDir = argv[++i];
    else if (arg === "--competitor") args.competitorIds.push(argv[++i]);
    else if (arg === "--no-state-write") args.writeState = false;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!args.competitorIds.length) delete args.competitorIds;
  return args;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const result = await run(parseArgs(process.argv.slice(2)));
    console.log(result.reportPath);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
