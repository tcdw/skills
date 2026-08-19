# Enriching OpenCode models from models.dev

Use this reference after discovering the exact model ids exposed by a custom
provider. The relay answers what is routable; models.dev helps describe the
upstream model.

## API shape

`https://models.dev/api.json` is shaped like:

```json
{
  "<provider-id>": {
    "id": "<provider-id>",
    "name": "Provider Name",
    "env": ["PROVIDER_API_KEY"],
    "npm": "@ai-sdk/openai-compatible",
    "api": "https://provider.example/v1",
    "models": {
      "<model-id>": {
        "id": "<model-id>",
        "name": "Model Name"
      }
    }
  }
}
```

Custom relays usually do not have their own top-level entry. Match the relay's
model ids to upstream provider entries instead.

## Inspect candidates

Download once per run so every model uses the same snapshot:

```bash
curl --fail --silent --show-error --location \
  https://models.dev/api.json --output /tmp/models-dev.json
```

List exact-id candidates across providers:

```bash
jq --arg id "$MODEL_ID" '
  to_entries
  | map(select(.value.models[$id] != null))
  | map({provider: .key, model: .value.models[$id]})
' /tmp/models-dev.json
```

If a relay adds a suffix, search both the exact id and a proposed base id. Only
accept suffix removal when the suffix repeats as a relay routing convention and
the remaining id has a strong catalog match. Preserve the full relay id in
OpenCode config.

## Candidate ranking

Exact ids often appear under many aggregators. Rank candidates instead of
taking the first JSON object:

1. Prefer the first-party provider suggested by an org prefix or model family,
   such as `xai` for Grok or `anthropic` for Claude.
2. Reject `status: deprecated`; avoid alpha/experimental entries unless the
   user requested them.
3. Prefer complete limits, modalities, capabilities, reasoning options, and
   non-zero costs.
4. Use release/update recency only as a tie-breaker.
5. If ambiguity remains and materially changes limits or cost, show candidates
   and ask rather than guessing.

Relay pricing can include markup and may differ from first-party models.dev
pricing. Copy upstream costs only as an estimate and disclose the source.

## Safe field mapping

OpenCode's custom model schema accepts these models.dev fields directly:

| models.dev | OpenCode model entry | Notes |
| --- | --- | --- |
| `name` | `name` | Keep a clean upstream display name; provider id already identifies the relay. |
| `family` | `family` | Copy when present. |
| `release_date` | `release_date` | Copy ISO date when present. |
| `attachment` | `attachment` | Copy boolean. |
| `reasoning` | `reasoning` | Copy boolean. |
| `temperature` | `temperature` | Copy boolean. |
| `tool_call` | `tool_call` | Copy boolean; do not claim tools from name alone. |
| `interleaved` | `interleaved` | Copy boolean/string/object shape supported by schema. |
| `cost` | `cost` | Preserve snake_case keys such as `cache_read`, `cache_write`, and `context_over_200k`. |
| `limit` | `limit` | Copy `context`, optional `input`, and `output`. |
| `modalities` | `modalities` | Preserve actual input/output arrays. |
| `status` | `status` | Omit active default; do not import deprecated entries. |

Do not copy raw fields that OpenCode's provider config rejects, including
`description`, `knowledge`, `last_updated`, `structured_output`, `open_weights`,
or `reasoning_options`.

## Reasoning variants

Convert effort-style reasoning options to config variants:

```json
"reasoning_options": [
  {"type": "effort", "values": ["low", "medium", "high", "max"]}
]
```

becomes:

```jsonc
"variants": {
  "low": {},
  "medium": {},
  "high": {},
  "max": {},
}
```

Do not invent effort variants for toggle-only or budget-token-only metadata.
The selected AI SDK must know how to encode a variant; verify at least one
variant when variants matter to the user.

## Relay aliases

The config object key is the model id shown by the relay and normally sent to
the API:

```jsonc
"grok-example-account1": {
  "name": "Grok Example",
  // Metadata may come from upstream `grok-example`, but requests keep the
  // relay id `grok-example-account1`.
}
```

Use an explicit model `id` only when intentionally exposing a different local
alias. Do not overwrite relay routing suffixes merely to make names prettier.

## Unknown models

If no trustworthy catalog match exists, create the smallest useful entry:

```jsonc
"relay-model-id": {
  "name": "Relay Model ID",
}
```

Add capabilities, limits, and costs only after documentation or probing proves
them. Zero-valued invented metadata is worse than omitted metadata because it
looks authoritative in verbose model output and cost statistics.

## Wire metadata warning

Top-level and per-model models.dev records may contain `npm` and `api`. These
describe the upstream provider, not necessarily the relay. Keep the relay's
`baseURL`, and select `npm` from live relay probes. Copying an upstream `api`
URL can silently bypass the relay and send the relay's credential elsewhere.
