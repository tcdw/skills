# Northstar probe evidence

The base URL and key are known to be correct.

## GET `/models`

- HTTP 200
- Includes exact id `northstar-coder-route2`

## POST `/chat/completions`

- HTTP 200
- Assistant content: `provider-ok`
- Tool-call probe also returned a valid tool call

## POST `/responses`

- HTTP 400
- Error: `Unsupported parameter: max_output_tokens`
