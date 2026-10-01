import type { APIRoute } from "astro";
import { cvMarkdown } from "../lib/cvMarkdown";

// Serves the CV as plain Markdown at /cv.md — the agent-friendly twin of /cv/.
export const GET: APIRoute = () =>
  new Response(cvMarkdown, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });