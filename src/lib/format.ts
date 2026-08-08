/** Clean a Markdown body into a plain-text excerpt for cards/llms. */
export function excerpt(body: string | undefined, length = 140): string {
  if (!body) return "";
  return body
    // strip images entirely, including alt text
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    // strip links, keep link text
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    // strip frontmatter
    .replace(/^---[\s\S]*?---/, "")
    // strip code fences and inline code
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    // strip remaining markdown punctuation
    .replace(/[#*_>|]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, length);
}

export function readingMinutes(body: string | undefined): number {
  const words = (body?.split(/\s+/).length || 0);
  return Math.max(1, Math.round(words / 220));
}
