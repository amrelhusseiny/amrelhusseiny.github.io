// Vercel serverless function — fetches GoatCounter daily visitor counts.
// The GoatCounter API token stays server-side (env var GOATCOUNTER_TOKEN).
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const token = process.env.GOATCOUNTER_TOKEN;
  const site = process.env.GOATCOUNTER_SITE || 'amro.goatcounter.com';
  if (!token) {
    return res.status(501).json({ error: 'GOATCOUNTER_TOKEN not configured' });
  }
  try {
    const end = new Date();
    const start = new Date(end.getTime() - 365 * 24 * 60 * 60 * 1000);
    const url = `https://${site}/api/v0/stats/total?start=${encodeURIComponent(start.toISOString())}&end=${encodeURIComponent(end.toISOString())}&daily=1`;
    const resp = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) {
      return res.status(resp.status).json({ error: `GoatCounter: ${resp.status} ${resp.statusText}` });
    }
    const data = await resp.json();
    res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate');
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: String(err) });
  }
}
