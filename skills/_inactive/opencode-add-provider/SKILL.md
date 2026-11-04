---
name: opencode-add-provider
description: Configure, import, migrate, and debug custom OpenCode model providers in opencode.json or opencode.jsonc from a baseURL, API-key environment variable, relay/LiteLLM endpoint, or partial provider snippet. Use whenever the user mentions adding an OpenCode provider, custom API, relay, gateway, proxy, 中转站, OpenAI-compatible/Responses/Anthropic endpoint, fetching /models, or enriching model metadata from models.dev, even if they only paste a URL and key variable. By default, merge the provider into config and verify it end to end; produce only a snippet when explicitly requested. Do not use for omp or models.yml.
compatibility: Requires curl and jq for endpoint discovery; OpenCode CLI is required for final validation and smoke tests.
---

# Add an OpenCode provider

Turn a URL, key reference, or partial provider fragment into a selectable and
tested OpenCode provider without exposing secrets or clobbering config.

## Goal

Finish with all of these true:

- The provider is merged into the intended `opencode.json` or `opencode.jsonc`.
- `opencode models <provider-id>` lists the intended models.
- A text/agent model answers a tiny `opencode run` smoke test.
- Model metadata is as complete as the available evidence allows.
- No raw API key is written to config, command output, or a tracked file.

Unless the user asks for a snippet only, perform the edits and verification.
Ask only when scope, destructive replacement, paid probing, or model selection
is genuinely ambiguous.

## Inputs to resolve

| Input | Required behavior |
| --- | --- |
| Config scope | Use the explicit project/global path. If unspecified, inspect project config and `~/.config/opencode/opencode.json(c)`; prefer global for a personal provider used across projects, but ask if both are plausible. |
| Provider id | Propose a short id from the service/host. Use a new id for a relay instead of overriding `openai` or `anthropic`. |
| `baseURL` | Preserve the API prefix expected by the service, usually ending in `/v1`. |
| Secret | Prefer the user's named env var as `{env:VAR}`. Support `{file:path}` or OpenCode `/connect` auth only when requested. |
| Models | Use the user's list or authenticated `GET <baseURL>/models`. Do not assume every advertised model is useful for agents. |
| Wire/API SDK | Probe the endpoint when allowed. Model family alone does not prove Chat Completions, Responses, or Anthropic Messages support. |

## Workflow

### 1. Inspect before changing anything

1. Read the target config and preserve `$schema`, comments, trailing commas,
   ordering style, and unrelated fields.
2. Fetch `https://opencode.ai/config.json` when confirming current provider or
   model fields. OpenCode rejects unknown config fields.
3. Check the current CLI with `opencode --version` and relevant command help.
4. Choose a dedicated provider id. A third-party relay named `acme` should be
   `acme`, not an override of the built-in `openai` provider.

Do not replace the whole `provider` object. Work with concurrent user changes
and patch only the new or requested provider.

### 2. Resolve the secret safely

When the user gives an environment variable name:

```json
"apiKey": "{env:ACME_API_KEY}"
```

Check only whether it is present; never print the value:

```bash
if [[ -n "$ACME_API_KEY" ]]; then print -r -- present; else print -r -- missing; fi
```

If missing, explain that the variable must exist in the environment that
launches OpenCode. Do not silently edit shell startup files. If the user gives
a raw key, do not echo it or embed it in config; ask for a secret-storage choice
or use `/connect` when appropriate.

### 3. Discover models and probe the wire

For an OpenAI-shaped endpoint, run the bundled probe with the env var name,
not its value:

```bash
skill://opencode-add-provider/scripts/probe-endpoint.sh \
  https://api.example.com/v1 ACME_API_KEY [text-model-id]
```

Without a model id, the script only lists models. With a model id, it also
tests Chat Completions and Responses. Probe Anthropic Messages separately only
when the service claims that wire format.

Choose the SDK from observed behavior:

| Working endpoint | Provider `npm` |
| --- | --- |
| `/chat/completions` | `@ai-sdk/openai-compatible` |
| `/responses` | `@ai-sdk/openai` |
| Anthropic `/messages` | `@ai-sdk/anthropic` |

If both OpenAI endpoints work, prefer the format documented by the relay and
verified with tools. LiteLLM and generic relays commonly use Chat Completions.
For mixed wires, use per-model `provider.npm` only after probing. Never copy an
upstream models.dev API URL into a relay model because that would bypass the
relay.

Treat probe responses as evidence, not success based on HTTP 200 alone. Check
for an actual assistant payload and errors about unsupported fields.

### 4. Select useful models

Follow the user's requested policy. For an agent-focused provider, retain text
models that can plausibly support chat and tools; exclude image/video/audio
generation models unless requested. Use metadata and probe results rather than
name matching alone. Ask when an unknown model is ambiguous.

Keep the exact relay model id as the config key and API id. Relay aliases such
as `model-name-account1` may map to upstream `model-name` metadata, but stripping
the alias from the request would call the wrong route.

### 5. Enrich from models.dev

Read `references/models-dev.md` before matching or copying metadata. Download
`https://models.dev/api.json`, then resolve each relay model with this order:

1. Exact model id under the likely first-party provider.
2. Exact id across all providers, ranked toward first-party, active, complete
   metadata.
3. A verified normalized alias, such as a repeated relay account suffix whose
   removal produces a catalog match.
4. A conservative custom entry if no trustworthy match exists.

Duplicate ids are common. Do not silently pick the first hit. Preserve the
relay's id and wire, then copy only schema-supported model metadata. Upstream
pricing is an estimate when a relay applies markup; state that caveat.

Precedence:

```text
live relay id/routability > explicit user values > trustworthy models.dev match > conservative defaults
```

### 6. Merge the provider

Typical Chat Completions provider:

```jsonc
"acme": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Acme",
  "options": {
    "baseURL": "https://api.example.com/v1",
    "apiKey": "{env:ACME_API_KEY}",
  },
  "models": {
    "relay-model-id": {
      "name": "Upstream Model Name",
      "family": "upstream-family",
      "release_date": "2026-01-01",
      "reasoning": true,
      "tool_call": true,
      "limit": {
        "context": 200000,
        "output": 64000,
      },
      "modalities": {
        "input": ["text", "image"],
        "output": ["text"],
      },
      "cost": {
        "input": 1.0,
        "output": 5.0,
        "cache_read": 0.1,
      },
      "variants": {
        "low": {},
        "medium": {},
        "high": {},
      },
    },
  },
}
```

Omit fields whose values are unknown rather than inventing limits, costs, or
capabilities. Do not add `options.store: false` by habit; that is specific to
some Responses-compatible services. Do not add unsupported models.dev fields
such as `description`, `knowledge`, or `reasoning_options` directly to config.

### 7. Validate and smoke test

Run these in order after editing:

```bash
opencode debug config >/dev/null
opencode models <provider-id> --verbose
opencode run --model <provider-id>/<model-id> \
  "Reply with exactly: provider-ok"
```

Suppress `opencode debug config` output because resolved config may contain the
secret value. A successful parse is not enough: confirm the intended models are
listed, then inspect the smoke response for `provider-ok`.

If the user requested agent-only models, smoke a text model rather than an
image or video model. When reasoning variants were added, optionally smoke one
with `--variant low` or another supported value.

OpenCode loads config at startup. After a successful edit, tell the user to
quit and restart existing OpenCode sessions.

## Troubleshooting

| Symptom | Likely fix |
| --- | --- |
| Config fails to load | Validate exact fields against `https://opencode.ai/config.json`; remove unsupported copied metadata. |
| Provider missing from model list | Confirm provider id, model map, `npm`, config scope, and any `enabled_providers` restriction. |
| 401/403 | Confirm `{env:VAR}` and that the variable exists in the GUI/service/shell environment that launches OpenCode. Never print it. |
| `/responses` rejects `max_output_tokens` or input shape | The relay has incomplete Responses support; use `@ai-sdk/openai-compatible` after a successful Chat Completions probe. |
| Chat works but tools fail | Probe a real tool call, verify `tool_call`, and check relay-specific schema restrictions before claiming success. |
| Model not found | Keep the exact id returned by the relay; metadata aliases must not replace the request id. |
| Wrong costs or limits | Re-check duplicate models.dev matches and prefer first-party metadata; relay pricing can differ. |
| Official provider broke | A relay probably shadowed a built-in id; move it to a dedicated provider id. |

## Output to the user

Report:

1. Config path and provider id.
2. `baseURL`, selected SDK/wire, and evidence from probing.
3. Secret reference name or auth location, never its value.
4. Models added, models intentionally skipped, and metadata match caveats.
5. Validation and smoke-test results.
6. The exact selection form: `<provider-id>/<model-id>` and restart reminder.
