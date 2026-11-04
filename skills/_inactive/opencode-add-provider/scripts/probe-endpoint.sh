#!/usr/bin/env bash
# Probe an OpenAI-compatible endpoint without placing the secret in argv.
# Usage: probe-endpoint.sh <baseURL> <API_KEY_ENV> [model-id]
set -euo pipefail

BASE="${1:-}"
KEY_ENV="${2:-}"
MODEL="${3:-}"

if [[ -z "$BASE" || -z "$KEY_ENV" ]]; then
  printf 'usage: %s <baseURL> <API_KEY_ENV> [model-id]\n' "$0" >&2
  exit 2
fi

if [[ ! "$KEY_ENV" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  printf 'invalid environment variable name: %s\n' "$KEY_ENV" >&2
  exit 2
fi

KEY="${!KEY_ENV:-}"
if [[ -z "$KEY" ]]; then
  printf 'environment variable %s is not set\n' "$KEY_ENV" >&2
  exit 2
fi

for command in curl jq; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'required command not found: %s\n' "$command" >&2
    exit 2
  fi
done

BASE="${BASE%/}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

request() {
  local name="$1"
  local method="$2"
  local url="$3"
  local body="${4:-}"
  local output="$TMP/$name.json"
  local status

  if [[ "$method" == "GET" ]]; then
    status="$(curl --silent --show-error --location --max-time 30 \
      --output "$output" --write-out '%{http_code}' \
      --header "Authorization: Bearer $KEY" \
      "$url")"
  else
    status="$(curl --silent --show-error --location --max-time 60 \
      --output "$output" --write-out '%{http_code}' \
      --request "$method" \
      --header "Authorization: Bearer $KEY" \
      --header 'Content-Type: application/json' \
      --data "$body" \
      "$url")"
  fi

  printf '%s HTTP %s\n' "$name" "$status"
  if jq -e . "$output" >/dev/null 2>&1; then
    jq -c '
      if (.data | type) == "array" then
        {count: (.data | length), ids: [.data[].id]}
      elif .error != null then
        {error: .error}
      elif .choices != null then
        {id, model, choices}
      elif .output != null then
        {id, model, status, output}
      else
        .
      end
    ' "$output"
  else
    printf 'non-JSON response (%s bytes)\n' "$(wc -c < "$output" | tr -d ' ')"
  fi
}

request models GET "$BASE/models"

if [[ -z "$MODEL" ]]; then
  exit 0
fi

CHAT_BODY="$(jq -cn --arg model "$MODEL" '{
  model: $model,
  messages: [{role: "user", content: "Reply with exactly: provider-ok"}],
  max_tokens: 32,
  stream: false
}')"

RESPONSES_BODY="$(jq -cn --arg model "$MODEL" '{
  model: $model,
  input: [{role: "user", content: "Reply with exactly: provider-ok"}],
  max_output_tokens: 32,
  store: false
}')"

request chat_completions POST "$BASE/chat/completions" "$CHAT_BODY"
request responses POST "$BASE/responses" "$RESPONSES_BODY"
