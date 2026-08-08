import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import type { APIContext } from "astro";

export async function GET(context: APIContext) {
  const posts = (await getCollection("blog", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  return rss({
    title: "Amro's Blog",
    description: "Network engineer and automation advocate. Writing about networks, Linux, AI, and automation.",
    site: context.site ?? "https://amroelhusseini.vercel.app",
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: p.data.date,
      description: p.data.description || (p.body ? p.body.replace(/[#*`>\[\]()!-]/g, "").slice(0, 160) : ""),
      link: `/blog/${p.id}/`,
    })),
  });
}
