---
name: omp-add-provider
description: >
  Configure a custom or third-party model provider for oh-my-pi (omp) in
  ~/.omp/agent/models.yml — OpenAI-compatible relays, Anthropic-fronted proxies,
  dual-key gateways, incomplete opencode/Claude/Codex config fragments,
  models.dev metadata fill-in, platform-aware API key storage (macOS Keychain vs
  env vars elsewhere), endpoint probing, 400
  dump triage, and smoke tests. Use whenever the user wants to add, import,
  migrate, or debug a provider, baseURL/baseUrl, relay, 中转站, proxy API,
  custom models list, store:false variants, or convert an opencode/Claude Code
  provider snippet into omp — even if they only paste a partial JSON/YAML
  fragment, say "帮我配一下这个 API", or hit max_output_tokens / strict-tool 400s
  on a custom relay.
---

# Add an omp provider

Turn a partial provider config (opencode JSON, Claude snippet, URL + key, or
"this relay") into a working entry in `~/.omp/agent/models.yml`.

Why this skill exists: third-party relays rarely match official OpenAI/Anthropic
wire behavior, and agent configs (opencode, etc.) omit fields omp needs
(`thinking`, `cost`, `compat`, secret indirection). Guessing `api:` from the
model name is how you get silent 400s.

## Docs to open on demand

- `omp://providers.md` — credentials, custom providers, `disabledProviders`
- `omp://models.md` — full `models.yml` schema, `compat`, discovery, equivalence
- `omp://provider-endpoint-constraints.md` — Completions vs Responses quirks
- `skill://omp-add-provider/references/models-yml-cheatsheet.md` — field map
- `skill://omp-add-provider/references/models-dev.md` — models.dev extraction
- `skill://omp-add-provider/scripts/probe-endpoint.sh` — curl probe helper

## Goal

A selectable provider: `omp models <id>` lists it, and a one-shot prompt
returns. Prefer a **new provider id** over hijacking built-in `openai` /
`anthropic`, so `/login` and official endpoints stay intact.

## Workflow

### 1. Collect inputs

| Input | Examples | Required? |
| --- | --- | --- |
| Provider id | `oproxy`, `my-gateway` | yes (propose from host/name) |
| `baseUrl` | `https://api.example.com/v1` | yes |
| API key | env var, `{file:…}`, macOS Keychain, pasted `sk-…` | unless `auth: none` |
| Platform | `uname -s` → `Darwin` vs Linux/WSL/Windows | yes (decides key storage, §3) |
| Model ids | fragment list and/or `GET /models` | ≥1 path |
| Wire family | Completions / Responses / Anthropic Messages | probe when allowed |
| Partial metadata | limits, variants, `store: false` | optional |

**opencode → omp map**

| opencode | omp |
| --- | --- |
| `baseURL` | `baseUrl` |
| `apiKey` / `{file:/path}` | env name (non-macOS default), `!security` Keychain lookup (macOS default), or `!cat` (see §3) |
| `models.<id>.limit.context` | `contextWindow` |
| `models.<id>.limit.output` | `maxTokens` |
| `options.store: false` | `compat.supportsStore: true` (omp then **emits** `store: false`) |
| `variants.low…max` | `thinking.mode: effort` + `efforts: […]` |
| `modalities.input` | `input: [text, image, …]` |
| `npm: @ai-sdk/anthropic` | start from `api: anthropic-messages` |

Same host, two keys (common 中转): **two provider ids** (e.g. `oproxy` +
`oproxy-claude`), not one provider with mixed wires.

Do **not** invent secrets from `sk-***` placeholders. Search the machine
(opencode `keys/`, env, macOS Keychain) or ask.

### 2. Dedicated provider id

| Situation | Choice |
| --- | --- |
| Third-party relay / 中转 | New id |
| Intentionally force all OpenAI traffic through a corp proxy | `providers.openai.baseUrl` override (rare; say so) |
| Local no-auth server | `auth: none` + discovery |

### 3. Store the key (machine-local, platform-dependent)

**Check the platform first** — `security` is macOS-only, so the default differs:

```bash
uname -s   # Darwin => macOS; Linux/MINGW/MSYS => env var path
```

| Platform | Default | Config value |
| --- | --- | --- |
| macOS (`Darwin`) | Keychain + `!security` | `apiKey: "!security …"` |
| Linux / WSL / BSD / Windows | Env var **name** | `apiKey: MY_RELAY_API_KEY` |

An existing convention in the user's `models.yml` overrides this table — match
siblings. If the file already mixes both, follow the platform default for new
entries.

**macOS — Keychain**

```bash
security add-generic-password -a "$USER" -s "omp.<provider-id>.api-key" -w "$KEY" -U
```

```yaml
apiKey: "!security find-generic-password -a \"$USER\" -s omp.<provider-id>.api-key -w"
```

**Non-macOS — env var name** (omp treats a bare scalar as env-name-or-literal;
if the env var exists its value wins)

```yaml
apiKey: MY_RELAY_API_KEY
```

The var must be exported in the environment omp actually launches from. Tell the
user where to put it and **do not** silently edit their shell rc — show the line:

```bash
export MY_RELAY_API_KEY='…'   # ~/.zshrc, ~/.bashrc, ~/.config/environment.d/*.conf, or a systemd unit
```

Naming: `<PROVIDER_ID>_API_KEY`, uppercased with `-`→`_` (e.g. `oproxy` →
`OPROXY_API_KEY`). If models.dev lists an `env` name for the upstream provider,
prefer that only when it is not a built-in omp provider var you would shadow.

Non-macOS secret-store alternatives (only when the tool is already installed —
verify with `command -v`; never assume a headless box has a keyring daemon):

```yaml
apiKey: "!pass show omp/<provider-id>"                                    # password-store
apiKey: "!secret-tool lookup service omp.<provider-id> account api-key"   # libsecret / GNOME Keyring
```

**File-based (any platform)** — opencode `{file:…}`, or when env vars are
awkward (systemd services, containers):

```yaml
apiKey: "!cat ~/.config/omp/<provider-id>.key"
```

```bash
chmod 600 ~/.config/omp/<provider-id>.key
```

Never write raw keys into git-tracked files. In the user-facing summary, name
the Keychain service / env var / key path only — never the value.

### 4. Enrich model metadata

Fragments are usually incomplete. Layer sources:

1. **Live relay** `GET {baseUrl}/models` — what is routable today  
2. **User fragment** — names, limits, variants (intent)  
3. **models.dev** `https://models.dev/api.json` — cost, limits, reasoning, modalities  
4. **Bundled catalog** `pi-catalog` `models.json` — efforts, default `api`, promotion targets  

**Merge rules**

- **id**: wire id from relay + fragment
- **name**: clean upstream display name from fragment/models.dev/catalog
  (e.g. `Claude Sonnet 4`, `GPT-5.4`). omp already shows **provider id + name**
  in the picker, so do **not** append `(proxy)`, `(relay)`, `(中转)` unless the
  user explicitly wants that disambiguator.
- **contextWindow / maxTokens**: fragment if set, else models.dev `limit.*`, else catalog  
- **cost**: always try models.dev for the upstream family (`cache_read`→`cacheRead`,
  `cache_write`→`cacheWrite`). **Do not leave `0/0/0/0` when models.dev has
  numbers** — zero costs hide spend and break ranking UX. Unknown after search
  may stay zero with a comment.  
- **reasoning / thinking.efforts**: catalog or models.dev `reasoning_options`
  (drop effort value `none` unless the user wants an off switch)  
- **input**: `[text]` or `[text, image]` when attachment/image is claimed  
- Fragment-only models missing from relay `/models`: still add if requested;
  comment that the relay did not advertise them  

Placeholder / offline hosts (no probe allowed): still fill costs from
models.dev; set `api` from fragment npm/hints or default
`openai-completions` for OpenAI-shaped relays.

### 5. Probe the wire before locking `api:`

Model family ≠ wire support. Relays often:

- fully implement `/v1/chat/completions`
- expose `/v1/responses` but reject `max_output_tokens` or need list `input`
- serve Anthropic `/v1/messages` on the same origin with another key

When network to the relay is allowed, run
`skill://omp-add-provider/scripts/probe-endpoint.sh` (or equivalent):

1. `GET /models`  
2. Tiny Completions (`max_completion_tokens`)  
3. Tiny Responses (list `input`, `store: false`)  
4. Anthropic-shaped `POST /messages` if relevant  

| Probe result | `api` |
| --- | --- |
| Completions OK, Responses broken/partial | `openai-completions` |
| Responses OK end-to-end | `openai-responses` |
| Anthropic messages OK | `anthropic-messages` |
| Both OpenAI OK | Prefer upstream-native; use Responses for GPT-5-class **only if** the host is complete |

Anthropic-fronted proxies: default `disableStrictTools: true` — many 400 on
`strict` tool schemas.

Typical OpenAI-relay `compat`:

```yaml
compat:
  supportsStore: true                 # → omp emits store: false
  supportsReasoningEffort: true
  maxTokensField: max_completion_tokens
  supportsDeveloperRole: true         # if host accepts developer role
```

`supportsStore: true` means “send `store: false`”, not “enable storage”.

### 6. Write `~/.omp/agent/models.yml`

1. Read the current file.  
2. **Merge** under `providers:`; never replace the whole file.  
3. Keep existing comments and secret conventions.  
4. Optionally add `equivalence.overrides` for canonical ids.  

Skeleton:

```yaml
providers:
  <id>:
    baseUrl: https://api.example.com/v1
    # macOS default (Keychain):
    apiKey: "!security find-generic-password -a \"$USER\" -s omp.<id>.api-key -w"
    # non-macOS default (env var NAME, exported in omp's environment):
    # apiKey: <ID>_API_KEY
    api: openai-completions   # or openai-responses / anthropic-messages
    authHeader: true
    # anthropic proxies:
    # disableStrictTools: true
    compat:
      supportsStore: true
      supportsReasoningEffort: true
      maxTokensField: max_completion_tokens
    models:
      - id: some-model
        name: Some Model
        reasoning: true
        input: [text, image]
        contextWindow: 1050000
        maxTokens: 128000
        cost:
          input: 1.0
          output: 5.0
          cacheRead: 0.1
          cacheWrite: 0
        thinking:
          mode: effort
          efforts: [low, medium, high, xhigh]
```

Also useful: `discovery.type: openai-models-list`,
`contextPromotionTarget: <provider>/<larger-model>`.

### 7. Verify

```bash
omp models <provider-id>
omp models find <provider-id>/<model>
```

```bash
cd /tmp && timeout 90 omp -p --no-session --model <provider>/<model>:<effort> --no-tools \
  "Reply with exactly: provider-ok"
```

On `400`, open the newest file under `~/.omp/logs/http-400-requests/`:

1. Confirm `api` and rejected body fields  
2. Adjust `api` / `compat` / `disableStrictTools`  
3. Smoke again  

Done when: model lists, smoke answers, secret not in git.

### 8. Optional (only if asked)

- `modelRoles` in `~/.omp/agent/config.yml`  
- Second provider id for the Anthropic key on the same relay  
- `contextPromotion.enabled` when spark→full targets exist  

## Decision cheatsheet

| Symptom | Fix |
| --- | --- |
| Missing from `omp models` | Schema error or unresolved `apiKey` |
| `Unsupported parameter: max_output_tokens` | Incomplete Responses → `api: openai-completions` |
| `Input must be a list` | Responses wants list `input` |
| `store` rejected | `supportsStore: false` / omit |
| Anthropic strict-tool 400 | `disableStrictTools: true` |
| 401 with “valid” key | `apiKey` must resolve: env var exported in omp's env, or Keychain entry present |
| `!security: command not found` (Linux/WSL) | macOS-only recipe on the wrong platform → switch to env var / `pass` / `!cat` |
| Env var works in your shell, not in omp | Exported only interactively; omp launched from a GUI/systemd/container env |
| Official OpenAI broken after edit | You shadowed `openai`; split to a new id |

## Anti-patterns

- Clobbering all of `models.yml`  
- Pasting live secrets into the file or chat logs you will commit  
- Skipping probe when the relay is reachable  
- GPT-5\* ⇒ always Responses on every 中转  
- opencode `provider.openai` → omp `openai` without meaning to shadow  
- Shipping `cost: {input: 0, output: 0, …}` despite models.dev prices  
- Suffixing model `name` with `(proxy)` / `(relay)` when the provider id already
  disambiguates (omp UI shows both)  
- Declaring “fixed” after a 400 without a new smoke  
- Emitting `!security …` on Linux/WSL/Windows (macOS-only binary)  
- Assuming `pass` / `secret-tool` exists on a non-macOS box without `command -v`  
- Editing the user's `~/.zshrc` / `~/.bashrc` yourself instead of showing the
  `export` line  

## Output to the user

1. Provider id + `baseUrl` + `api`  
2. Secret location — Keychain service (macOS) or env var name / key path
   (elsewhere), plus where to export it. Never the value.  
3. Models added (+ which `/models` omitted)  
4. Smoke command + result  
5. Select: `omp --model <provider>/<model>:<effort>`  
