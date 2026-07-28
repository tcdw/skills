#!/usr/bin/env bash
# Probe an OpenAI-compatible (and optional Anthropic) relay.
# Usage:
#   KEY=sk-... ./probe-endpoint.sh https://api.example.com/v1 [model-id]
#   ./probe-endpoint.sh https://api.example.com/v1 gpt-x <<< "$KEY"  # also reads KEY env
set -euo pipefail

BASE="${1:-}"
MODEL="${2:-gpt-4o-mini}"
KEY="${KEY:-${API_KEY:-}}"

if [[ -z "$BASE" ]]; then
  echo "usage: KEY=... $0 <baseUrl> [model]" >&2
  exit 2
fi
if [[ -z "$KEY" ]]; then
  echo "set KEY or API_KEY" >&2
  exit 2
fi

BASE="${BASE%/}"
AUTH=( -H "Authorization: Bearer ${KEY}" -H "Content-Type: application/json" )

echo "== GET ${BASE}/models =="
curl -sS "${AUTH[@]}" "${BASE}/models" | head -c 4000
echo -e "\n"

echo "== POST ${BASE}/chat/completions (model=${MODEL}) =="
curl -sS "${AUTH[@]}" "${BASE}/chat/completions" \
  -d "$(jq -nc --arg m "$MODEL" '{
    model:$m,
    messages:[{role:"user",content:"ping"}],
    max_completion_tokens:16,
    stream:false
  }')" | head -c 2000
echo -e "\n"

echo "== POST ${BASE}/responses (model=${MODEL}) =="
curl -sS "${AUTH[@]}" "${BASE}/responses" \
  -d "$(jq -nc --arg m "$MODEL" '{
    model:$m,
    input:[{role:"user",content:"ping"}],
    max_output_tokens:32,
    store:false
  }')" | head -c 2000
echo -e "\n"

echo "== POST ${BASE}/messages (Anthropic-shaped, model=${MODEL}) =="
curl -sS \
  -H "x-api-key: ${KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  "${BASE}/messages" \
  -d "$(jq -nc --arg m "$MODEL" '{
    model:$m,
    max_tokens:32,
    messages:[{role:"user",content:"ping"}]
  }')" | head -c 2000
echo
