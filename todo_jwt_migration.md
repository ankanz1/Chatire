# ✅ TODO – Switch Djoser auth to JWT

- **Back‑end**
  - [ ] Add `import datetime` to `settings.py`.
  - [ ] Replace `REST_FRAMEWORK` authentication with `JSONWebTokenAuthentication` (and optionally `SessionAuthentication`).
  - [ ] Add a `JWT_AUTH` block with `JWT_EXPIRATION_DELTA` (e.g., 7 days) and refresh settings.
  - [ ] (Optional) Adjust `DJOSER` config to disable the default token model.
  - [ ] Update `chatire/urls.py` – replace `djoser.urls.authtoken` with `djoser.urls.jwt`.
  - [ ] Restart Django dev server and verify no import errors.

- **Front‑end (Vue)**
  - [ ] In `UserAuth.vue` change the sign‑in POST URL to `/auth/jwt/create/` and store `data.token` in `sessionStorage` as `authToken`.
  - [ ] In `Chat.vue` change the global Ajax header from `Token` to `JWT`.
  - [ ] Test the flow: sign‑in, observe the token in `sessionStorage`, and ensure subsequent API calls include the JWT header.
  - [ ] Verify token expiry by waiting for the configured period **or** manually removing `authToken` from `sessionStorage` and confirming the app forces a re‑login.

> Once all check‑boxes are ticked, the migration is complete.
