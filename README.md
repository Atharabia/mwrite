# Mwrite

A simple blog app

## Installation

1. Install Docker
2. Clone this repo
3. Copy `.env.example` to `.env` and fill in the values
4. Set `DOMAIN` in `.env`:
   - For local development, leave it as `localhost`.
   - For production, set it to your domain (e.g. `blog.example.com`) and
     point its DNS `A`/`AAAA` record at this server. Also set `ACME_EMAIL`
     to a real email address for Let's Encrypt notices.
5. Run the following command:

```bash
docker compose up --build -d
```

6. The app will be available at `https://<DOMAIN>` (or
   [http://localhost](http://localhost) if `DOMAIN=localhost`). Caddy will
   automatically obtain and renew a Let's Encrypt certificate for your
   domain — make sure ports 80 and 443 are reachable from the internet.
