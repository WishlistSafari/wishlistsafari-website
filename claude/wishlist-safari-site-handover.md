# Wishlist Safari site handover

Source of truth for the scheduled site manager. Keep current.
Last updated: 2026-10-17

## Site
- Live at https://wishlistsafari.com, hosted on Netlify, static HTML, deployed from `main`.
- Owner: Jean Smyth, Cape Town. Contact: hello@wishlistsafari.com.
- Model: direct-to-camp. Wishlist Safari introduces travellers to camps' own reservations teams. No specialist planner.

## Pages (17 HTML files)
- `index.html`: wishlist planner and traveller enquiry form.
- `lodges.html`: partner camp page, noindex, linked from footer only.
- `privacy.html`.
- 14 species guides (listed in `llms.txt` and `sitemap.xml`): lion, leopard, elephant, mountain gorilla, cheetah, African wild dog, black rhino, shoebill, Pel's fishing owl, brown hyena, pangolin, aardvark, black-maned Kalahari lion, desert-adapted elephant.

## Forms (Netlify)
- `wishlist-enquiry` on `index.html`: traveller enquiries.
- `partner-enquiry` on `lodges.html`: partner camp enquiries.
- Both must keep `form-name` and the honeypot `netlify-honeypot="bot-field"`.

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
