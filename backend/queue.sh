source .env
curl https://api.openai.com/v1/batches?limit=10 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json"