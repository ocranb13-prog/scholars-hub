# Scholars HUB — Static Frontend

Plain HTML/CSS/JS version of the site — no Flask, no build step. Open
`index.html` directly in a browser, or host this folder as-is on any
static host (GitHub Pages, Netlify, plain web hosting).

## Pages
index.html, about.html, services.html, projects.html, gallery.html,
blog.html, contact.html, book-service.html

## Contact + Booking forms
These forms POST to a separately hosted Flask API (see the `backend/`
folder from the full project) for Firestore storage. Point them at
your deployed API by setting one variable before `js/main.js` loads,
e.g. add this in each page's `<head>` (or right before the main.js
`<script>` tag):

    <script>window.SCHOLARS_HUB_API_BASE = "https://your-api-domain.com";</script>

If you don't set it, forms default to `http://127.0.0.1:5000` (i.e.
the backend running locally) — fine for local testing, not for a
live site.

The backend already has CORS enabled on its /api/* routes so it can
accept requests from this frontend even when hosted on a different
domain.

## Backend setup (Flask, in `backend/`)

1. `cd backend && pip install -r requirements.txt`
2. Add your Firebase service account key as `backend/serviceAccountKey.json`
   (see the comment at the top of `firebase_config.py`).
3. Copy `backend/.env.example` to `backend/.env` and fill in your SMTP
   details - this is what makes the site email you whenever someone
   submits the Contact form or books a service (details below).
4. Run it: `python3 app.py` (defaults to `http://127.0.0.1:5000`).

## Email notifications on new messages/bookings

Every Contact form submission and every Book a Service request is
saved to Firestore *and* emailed to `NOTIFY_EMAIL` (defaults to
scholarshub26@outlook.com). This is configured entirely through
`backend/.env` - see `backend/.env.example` for the variables
(`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`,
`SMTP_FROM`, `NOTIFY_EMAIL`). If those variables aren't set, the site
still works fine and still saves everything to Firestore - it just
skips sending the email and logs a warning instead.

## Fixes in this update

- **Mobile "Book a Service" was unclickable**: `.site-header` had a
  `backdrop-filter` (glass-blur effect) which, on phones, was silently
  breaking the mobile menu's positioning - the whole slide-out nav
  (including the "Book a Service" button) was getting squashed into
  the header's own ~68px height instead of the full screen, so it was
  there but not tappable. Removed the blur from the header to fix it.
- **New bookings/messages now also send an email**, not just a
  Firestore write (see above).
- **Phone, email, and TikTok are now clickable** wherever they appear
  (Contact page info panel and every page's footer): phone numbers
  open the dialer (`tel:`), the email opens the mail app (`mailto:`),
  and TikTok opens the profile in a new tab.
