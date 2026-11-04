# Filling metadata from models.dev

API: `https://models.dev/api.json`  
Shape: `{ "<provider-id>": { id, name, env, models: { "<model-id>": {…} } }, … }`

## Extract one model

```bash
curl -sL https://models.dev/api.json -o /tmp/models-dev.json
python3 - <<'PY'
import json,sys
data=json.load(open("/tmp/models-dev.json"))
provider, model = sys.argv[1], sys.argv[2]
m = data[provider]["models"][model]
print(json.dumps(m, indent=2))
PY
openai gpt-5.4
```

Search across providers when the id is unknown:

```python
for pid, p in data.items():
    for mid, m in (p.get("models") or {}).items():
        if "gpt-5.6-luna" in mid:
            print(pid, mid, m.get("limit"), m.get("cost"))
```

## Field mapping → omp model entry

| models.dev | omp `models.yml` |
| --- | --- |
| `id` | `id` |
| `name` | `name` |
| `limit.context` | `contextWindow` |
| `limit.output` | `maxTokens` |
| `cost.input` | `cost.input` |
| `cost.output` | `cost.output` |
| `cost.cache_read` | `cost.cacheRead` |
| `cost.cache_write` | `cost.cacheWrite` |
| `reasoning: true` | `reasoning: true` |
| `reasoning_options` effort `values` | `thinking.efforts` (map `none` → omit; keep low…max) |
| `modalities.input` includes `image` | `input: [text, image]` |
| `attachment: true` | prefer image-capable `input` |
| `tool_call` | informs tool expectation (omp tools still work if wire allows) |

## Also check the bundled catalog

When omp is installed via bun:

```text
$(dirname $(dirname $(which omp)))/**/pi-catalog@*/src/models.json
# or
~/.bun/install/cache/@oh-my-pi/pi-catalog@*/src/models.json
```

Official provider entries include `api`, `thinking.efforts`,
`contextPromotionTarget`, and costs aligned with omp’s runtime.

## Precedence reminder

```
live /v1/models  >  user fragment limits/names  >  models.dev  >  catalog defaults
```

Relay advertisement answers “can I call it?”. models.dev answers “what are the
card limits/costs?”. Catalog answers “how does omp usually drive this family?”.
