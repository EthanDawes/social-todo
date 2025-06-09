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
2. Download your tasks from Google Takout and put `Tasks.json` into `backend`
3. Paste your OpenAI API key into `.env`

**Reference:**
- [OpenAI pricing](https://platform.openai.com/docs/pricing)
