# Guide rapide pour agents IA – EuropGreen‑Solar

## Vue d’ensemble
- Monorepo: backend Django 5 + DRF (dossier `back/`), frontend Nuxt 3 + Pinia (dossier `front/`).
- Domaine fonctionnel: gestion de projets d’installation solaire (prospects → offres → devis → installations → factures + démarches administratives).
- Apps backend majeures: `authentication`, `users`, `request` (prospects), `offers`, `billing`, `installations`, `invoices`, `administrative`.

## Démarrer en local (dev)
- Backend (port 8000): `cd back ; python -m venv venv ; venv\Scripts\activate ; pip install -r requirements.txt ; python manage.py runserver`.
- Frontend (port 3000): `cd front ; npm i ; npm run dev`.
- Le front proxy toutes les requêtes commençant par `/api/` vers le backend: voir `front/server/api/[...].ts` et `nuxt.config.ts (runtimeConfig.proxyUrl)`.
  - Par défaut: `PROXY_URL=http://localhost:8000/`.
- Docs API: `http://localhost:8000/api/docs/` (DRF Spectacular).

## Routage API et conventions
- Les routes DRF sont montées à la racine dans `back/EuropGreenSolar/urls.py` via `include` des apps.
  - Exemples: `/users/`, `/offers/`, `/requests/`, `/installations/forms/`, `/invoices/…`, `/auth/login/`.
- Le front consomme via `$fetch('/api/...')` (le préfixe `/api` est géré côté Nuxt et n’existe pas côté Django).
- DRF utilise des ViewSets + `DefaultRouter` dans chaque app (`*/urls.py`).

## Authentification (JWT en cookies)
- Auth côté back: `authentication/auth_method.py` définit `CookieJWTAuthentication` (lit le cookie `access_token`).
- Paramètres cookies dans `settings.py`: noms (`ACCESS_TOKEN_COOKIE_NAME`, `REFRESH_TOKEN_COOKIE_NAME`), `SIMPLE_JWT`, CORS/SameSite.
- Côté front:
  - Toutes les requêtes protégées doivent inclure `credentials: 'include'` (ex: `pages/home/**`, composants d’édition).
  - Pour SSR, propager les cookies: `useRequestHeaders(['cookie'])` (voir `store/auth.ts: fetchUser / refreshToken`).
  - En cas de 401, utiliser le helper `front/utils/apiRequest.ts` qui tente un refresh via `/api/auth/token/refresh/` puis rejoue la requête.

## Génération de documents (PDF)
- Devis: tentative de rendu fidèle via Playwright en ouvrant la page front `/print/quotes/:id`, fallback ReportLab. Voir `back/README.md` pour l’installation Playwright.
- Administration (CERFA/Consuel): remplissage de PDF AcroForms avec `pdfrw`.
  - Utilitaires PDF: `back/EuropGreenSolar/utils/pdf.py` (`fill_pdf`, `fill_pdf_bytes`).
  - Aperçu CERFA (PDF binaire): `POST /administrative/cerfa/preview/` – construit les champs côté back (`administrative/views.py::build_pdf_data_from_payload`) et renvoie `application/pdf`.
  - Le front rend un aperçu client avec `pdfjs-dist` (ex: `front/components/administrative/Cerfa16702/Preview.vue`).
- Les gabarits statiques sont dans `back/static/pdf/` (ex: `cerfa_16702.pdf`). Les fichiers générés/pièces jointes vont sous `back/media/**`.

## Emails
- Utilitaire unique: `back/EuropGreenSolar/email_utils.py` → essaie Mailgun puis fallback SMTP (`EmailMultiAlternatives`).
- Config via variables d’env (`MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, SMTP…). Les templates HTML sont sous `back/templates/emails/`.

## Points d’intégration clés et exemples
- Proxy API (Nuxt): `server/api/[...].ts` traduit `/api/foo` → `${PROXY_URL}/foo` (ex: `$fetch('/api/users/me/')`).
- Exemple DRF: `back/users/urls.py` expose `/users/me/` (vue dédiée) et `/users/` (admin via ViewSet).
- Exemple admin PDF: `back/administrative/urls.py` expose `/administrative/cerfa16702/…` et `/administrative/cerfa/preview/`.

## Gotchas / bonnes pratiques propres au projet
- Ne pas préfixer les routes Django par `/api` côté back; c’est le proxy Nuxt qui ajoute ce préfixe côté front.
- Toujours définir `credentials: 'include'` pour les appels authentifiés et utiliser `apiRequest` en cas d’actions mutatives.
- En SSR, passer les cookies explicites avec `useRequestHeaders(['cookie'])`.
- Si vous ajoutez une route protégée, vérifiez CORS et cookies dans `settings.py` (`FRONTEND_URL`, `CORS_ALLOWED_ORIGINS`).
- Pour les PDFs, privilégier `fill_pdf_bytes` et renvoyer `application/pdf` avec `Content-Disposition` adapté.
