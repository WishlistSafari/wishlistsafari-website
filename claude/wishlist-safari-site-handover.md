# Wishlist Safari site handover

Source of truth for the scheduled site manager. Keep current.
Last updated: 2026-10-23

## Site
- Live at https://wishlistsafari.com, hosted on Netlify, static HTML, deployed from `main`.
- Owner: Jean Smyth, Cape Town. Contact: hello@wishlistsafari.com.
- Model: direct-to-camp. Wishlist Safari introduces travellers to camps' own reservations teams. No specialist planner.

## Pages (26 HTML files at 2026-10-17)
- `index.html`: wishlist planner and traveller enquiry form.
- `lodges.html`: partner camp page, noindex, linked from footer only.
- `privacy.html`.
- `sightings.html`.
- 22 species and guide pages (everything else, e.g. lion, leopard, meerkat, whale shark). Check `sitemap.xml` and `llms.txt` list them.

## Forms (Netlify)
- `wishlist-enquiry` on `index.html`: traveller enquiries.
- `partner-enquiry` on `lodges.html`: partner camp enquiries.
- `wishlist-updates` on `index.html`: email signup. Confirmed 2026-10-20: has `form-name` and honeypot `bot-field`.
- Wishlist and partner forms must keep `form-name` and the honeypot `netlify-honeypot="bot-field"`.

## Rules
- Never quote prices or commission.
- Wildlife locations at regional level only. None for rhino or pangolin.
- Plain British English, no em dashes.
- Commit as: `git -c user.name="Wishlist Safari" -c user.email="hello@wishlistsafari.com" commit`. Push to `main`.
- After any species or page change, update `sitemap.xml` and `llms.txt`.

## Tests before pushing
- Pages load, no script errors, counts match, both forms keep `form-name` and honeypot.

## Signed camps
- None recorded yet. Add here when confirmed.

## Decisions
- 2026-10-16: switched to direct-to-camp model, specialist planner removed.
- 2026-10-16: lodges link moved to footer, lodges page set to noindex.
- 2026-10-17: Northern Tuli and Mashatu added.
- 2026-10-17: this doc and the change request list created.

## Known limits
- The cloud sandbox blocked wishlistsafari.com on 2026-10-17, so live health checks need network access allowed.
- 2026-10-20: still blocked (proxy 403). Netlify connector found no project matching "wishlist", so form submissions cannot be read.
- 2026-10-21: still blocked (curl failed, no response). Netlify team "wishlistsafari" has no projects visible, so forms cannot be read. Site likely not linked to this Netlify team.
- 2026-10-23: still blocked (curl 000 on all four URLs). Netlify get-projects "wishlist" returns empty, so forms cannot be read. Jean to link the site to the Netlify team or allow the domain.
