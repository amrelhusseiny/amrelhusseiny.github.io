import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import { excerpt } from "../lib/format";

export const GET: APIRoute = async () => {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  const notes = (await getCollection("notes", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  const site = "https://amroelhusseini.vercel.app";

  const lines = [
    "# Amro's Blog",
    "",
    "> Network engineer and automation advocate. Writing about networks, Linux, AI, and automation.",
    "",
    "- Author: Amro El Husseini",
    `- Site: ${site}`,
    `- Last-Updated: ${new Date().toISOString().slice(0, 10)}`,
    `- Source: ${site}/llms.txt`,
    `- Full content: ${site}/llms-full.txt`,
    "",
    "This site is written by Amro El Husseini. Content covers networking, Linux, AI, and automation — technical posts aimed at engineers.",
    "",
    "## Blog",
    ...posts.slice(0, 50).map((p) => {
      const d = p.data.date.toISOString().slice(0, 10);
      const s = excerpt(p.body, 120);
      return `- [${p.data.title}](${site}/blog/${p.id}/): ${d} — ${s}`;
    }),
    "## Notes",
    ...notes.slice(0, 100).map((n) => {
      const d = n.data.date.toISOString().slice(0, 10);
      return `- [${n.data.title || n.id}](${site}/notes/): ${d}`;
    }),
    "## Optional",
    ...posts.slice(50).map((p) => {
      const d = p.data.date.toISOString().slice(0, 10);
      return `- [${p.data.title}](${site}/blog/${p.id}/): ${d}`;
    }),
    "",
  ];

  return new Response(lines.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
