import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const GET: APIRoute = async () => {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  const notes = (await getCollection("notes", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  const out = [
    "# Amro's Blog — Full Content",
    "",
    "> Network engineer and automation advocate. Writing about networks, Linux, AI, and automation.",
    "",
    "- Author: Amro El Husseini",
    "- Site: https://amroelhusseini.vercel.app",
    `- Last-Updated: ${new Date().toISOString().slice(0, 10)}`,
    "",
    "---",
    "# BLOG POSTS",
    "---",
  ];

  for (const p of posts.slice(0, 50)) {
    out.push("", "---", "", `## ${p.data.title}`, "",
      `*Published: ${p.data.date.toISOString().slice(0, 10)}*`, "",
      `URL: https://amroelhusseini.vercel.app/blog/${p.id}/`, "",
      p.data.tags?.length ? `Tags: ${p.data.tags.join(", ")}` : "",
      "", p.body || "");
  }

  out.push("", "---", "# NOTES", "---");
  for (const n of notes.slice(0, 100)) {
    out.push("", "---", "", `## ${n.data.title || n.id}`, "",
      `*Published: ${n.data.date.toISOString().slice(0, 10)}*`, "",
      `URL: https://amroelhusseini.vercel.app/notes/`, "",
      n.body || "");
  }

  return new Response(out.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
