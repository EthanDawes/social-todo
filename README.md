# Social TODO

A social media spoof (not affiliated or endorsed by any company) to make doomscrolling more productive: remind you of your tasks.

## Apps
- Tumblr
- 4chan
- Twitter

## Usage
Click one of these app links, then "Add to homescreen" from your browser

## Developing

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

### Backend
**Prerequisites:**
- Python 3.13
- PDM

**Setup:**
1.
    ```bash
    cd backend
    cp .sample.env .env
    pdm install
    ```
2. Paste your OpenAI API key into `.env`
3. Create a [Google Cloud Project](https://console.cloud.google.com/auth/clients/)
   1. Create desktop OAuth client
   2. Download `client_secret_*.json` to `backend`. Rename to `credentials.json`
   3. Add the Google tasks library
   4. Add the read permission
   5. Add yourself as a test user

**Reference:**
- [OpenAI pricing](https://platform.openai.com/docs/pricing)
- [Batch API](https://platform.openai.com/docs/guides/batch?lang=python)
