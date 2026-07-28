# models.yml cheatsheet (custom providers)

Path: `~/.omp/agent/models.yml` (or `models.yaml`).

## Provider fields

| Field | Purpose |
| --- | --- |
| `baseUrl` | API root, usually ending in `/v1` |
| `apiKey` | Env var **name**, literal key, or `!shell command` (stdout trimmed). Platform default: env name off macOS, `!security` Keychain on macOS |
| `api` | Default wire: `openai-completions`, `openai-responses`, `anthropic-messages`, … |
| `authHeader` | When true, send `Authorization: Bearer <key>` |
| `auth` | `apiKey` (default), `none`, or `oauth` (custom models still need key semantics) |
| `headers` | Extra static headers (values may use `!command`) |
| `disableStrictTools` | Anthropic proxies that reject `strict` |
| `compat` | Provider-level OpenAI/Anthropic compat baseline |
| `discovery` | Runtime model list (`openai-models-list`, `proxy`, `ollama`, …) |
| `modelOverrides` | Patch built-in or discovered models by id |
| `models` | Explicit model list (non-empty ⇒ full custom provider) |

## Model fields

| Field | Purpose |
| --- | --- |
| `id` | Wire model id |
| `name` | UI label |
| `api` | Per-model wire override |
| `reasoning` | Model can think / effort |
| `input` | e.g. `[text]`, `[text, image]` |
| `contextWindow` | Context tokens |
| `maxTokens` | Max output tokens |
| `cost.input/output/cacheRead/cacheWrite` | USD / 1M tokens (display + accounting) |
| `thinking.mode` | Usually `effort` |
| `thinking.efforts` | Subset of `minimal\|low\|medium\|high\|xhigh\|max` |
| `compat` | Per-model deep-merge over provider compat |
| `contextPromotionTarget` | `provider/model` or same-provider `model` fallback on overflow |
| `headers` | Per-model header overrides |

## compat flags that matter for relays

| Flag | Effect |
| --- | --- |
| `supportsStore: true` | Emit `store: false` on Completions (and related paths) |
| `supportsReasoningEffort` | Allow `reasoning_effort` |
| `maxTokensField` | `max_completion_tokens` or `max_tokens` |
| `supportsDeveloperRole` | Use `developer` instead of `system` for reasoning models |
| `supportsUsageInStreaming` | `stream_options.include_usage` |
| `thinkingFormat` | `openai` / `openrouter` / `zai` / `qwen` / … |

## equivalence

```yaml
equivalence:
  overrides:
    my-relay/gpt-5.4: gpt-5.4
  exclude:
    - my-relay/experimental-id
```

Maps concrete `provider/id` to a canonical upstream id for coalescing.

## apiKey forms

| Form | Example | When |
| --- | --- | --- |
| Env var **name** | `apiKey: MY_RELAY_API_KEY` | default off macOS (Linux/WSL/BSD/Windows) |
| `!command` | `apiKey: "!security …"` | default on macOS (Keychain) |
| Literal | `apiKey: sk-…` | avoid; never in git-tracked files |

A bare scalar is env-name-or-literal: if an env var by that name exists, its
value wins.

### Platform-specific `!command` recipes

```yaml
# macOS only (security is not present elsewhere)
apiKey: "!security find-generic-password -a \"$USER\" -s omp.my-relay.api-key -w"

# Linux/WSL — only if the tool is actually installed (check `command -v`)
apiKey: "!pass show omp/my-relay"
apiKey: "!secret-tool lookup service omp.my-relay account api-key"

# Any platform — file with 0600 perms
apiKey: "!cat ~/.config/omp/my-relay.key"
```

- Leading `!` ⇒ run shell, trim stdout
- 10s timeout; failures omit the key (provider then looks unconfigured)
- Successful stdout cached for process lifetime

## Minimal templates

### OpenAI-compatible relay

```yaml
providers:
  my-relay:
    baseUrl: https://api.example.com/v1
    apiKey: MY_RELAY_API_KEY   # non-macOS default; on macOS use the !security form above
    api: openai-completions
    authHeader: true
    compat:
      supportsStore: true
      supportsReasoningEffort: true
      maxTokensField: max_completion_tokens
    models:
      - id: gpt-x
        name: GPT X
        reasoning: true
        input: [text, image]
        contextWindow: 200000
        maxTokens: 8192
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }
        thinking:
          mode: effort
          efforts: [low, medium, high]
```

### Anthropic-compatible proxy

```yaml
providers:
  my-claude-proxy:
    baseUrl: https://api.example.com/v1
    apiKey: MY_CLAUDE_PROXY_KEY   # non-macOS default; macOS → !security lookup
    api: anthropic-messages
    authHeader: true
    disableStrictTools: true
    models:
      - id: claude-sonnet-4
        name: Claude Sonnet 4
        reasoning: true
        input: [text, image]
        contextWindow: 200000
        maxTokens: 16384
        cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 }
```

### Keyless local OpenAI server

```yaml
providers:
  local-vllm:
    baseUrl: http://127.0.0.1:8000/v1
    auth: none
    api: openai-completions
    discovery:
      type: openai-models-list
```
