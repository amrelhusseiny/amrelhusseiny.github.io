// Vercel serverless — returns the CV owner's contact details ONLY after
// the visitor submits a valid email + phone. Real values live in env vars,
// never in the static HTML.
import type { VercelRequest, VercelResponse } from '@vercel/node';

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRe = /^[+]?[0-9()\-\s]{7,20}$/;

export default function handler(req: VercelRequest, res: VercelResponse) {
  const { email, phone } = req.query as { email?: string; phone?: string };

  if (!email || !phone) {
    return res.status(400).json({ error: 'email and phone are required' });
  }
  if (!emailRe.test(email)) {
    return res.status(422).json({ error: 'invalid email format' });
  }
  if (!phoneRe.test(phone)) {
    return res.status(422).json({ error: 'invalid phone format' });
  }

  return res.status(200).json({
    email: process.env.CV_EMAIL || '',
    phone: process.env.CV_PHONE || '',
  });
}
