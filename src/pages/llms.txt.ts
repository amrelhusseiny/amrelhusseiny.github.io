import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const GET: APIRoute = async () => {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  const notes = (await getCollection("notes", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  const lines = [
    "# Amro's Blog",
    "",
    "> Network engineer and automation advocate. Writing about networks, Linux, AI, and automation.",
    "",
    "- Author: Amro El Husseini",
    "- Site: https://amroelhusseini.vercel.app",
    `- Last-Updated: ${new Date().toISOString().slice(0, 10)}`,
    "- Source: https://amroelhusseini.vercel.app/llms.txt",
    "- Full content: https://amroelhusseini.vercel.app/llms-full.txt",
    "",
    "This site is written by Amro El Husseini. Content covers networking, Linux, AI, and automation — technical posts aimed at engineers.",
    "",
    "## Blog",
    ...posts.slice(0, 20).map((p) => {
      const d = p.data.date.toISOString().slice(0, 10);
      const s = p.body ? p.body.replace(/[#*`>\[\]()!-]/g, "").slice(0, 120) : "";
      return `- [${p.data.title}](https://amroelhusseini.vercel.app/blog/${p.id}/): ${d} — ${s}`;
    }),
    "## Notes",
    ...notes.slice(0, 50).map((n) => {
      const d = n.data.date.toISOString().slice(0, 10);
      return `- [${n.data.title || n.id}](https://amroelhusseini.vercel.app/notes/): ${d}`;
    }),
    "",
  ];

  return new Response(lines.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
