# Modular Model Configuration Structure
Time: January 15, 2025 01:30 MST
Priority: HIGH

## Directory Structure

```
models/
├── cloud/
│   ├── anthropic/
│   │   ├── claude-3-5-sonnet-20241022.json
│   │   ├── claude-3-5-haiku-20241022.json
│   │   └── archived/
│   │       └── claude-2-1-20230815.json
│   │
│   └── openai/
│       ├── gpt-4o-20240115.json
│       ├── gpt-4-turbo-20240115.json
│       └── archived/
│           └── gpt-4-20230815.json
│
└── local/
    └── ray_serve/
        ├── llama-3-70b.yaml
        ├── mistral-7b.yaml
        └── archived/
            └── llama-2-70b.yaml
```

## Cloud Model JSON Examples

1. claude-3-5-sonnet-20241022.json
```json
{
    "model_id": "claude-3-5-sonnet-20241022",
    "provider": "anthropic",
    "status": "active",
    "version": "2024-01-22",
    "api": {
        "endpoint": "https://api.anthropic.com/v1/messages",
        "auth": {
            "type": "api_key",
            "key_env": "ANTHROPIC_API_KEY"
        },
        "headers": {
            "anthropic-version": "2024-01-01"
        }
    },
    "rate_limits": {
        "rpm": 4000,
        "tpm": 1000000
    },
    "capabilities": {
        "context_window": 200000,
        "max_tokens": 150000,
        "streaming": true,
        "functions": true,
        "vision": true
    },
    "settings": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "max_tokens_to_sample": 150000
    },
    "retry_policy": {
        "max_retries": 3,
        "initial_delay": 1,
        "max_delay": 30,
        "backoff_factor": 2
    },
    "fallback": {
        "models": [
            "gpt-4o-20240115",
            "claude-3-5-haiku-20241022"
        ],
        "strategy": "sequential"
    },
    "cost": {
        "input_per_1k": 0.015,
        "output_per_1k": 0.075,
        "currency": "USD"
    }
}
```

2. gpt-4o-20240115.json
```json
{
    "model_id": "gpt-4o-20240115",
    "provider": "openai",
    "status": "active",
    "version": "2024-01-15",
    "api": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth": {
            "type": "api_key",
            "key_env": "OPENAI_API_KEY"
        }
    },
    "rate_limits": {
        "rpm": 500,
        "tpm": 300000
    },
    "capabilities": {
        "context_window": 128000,
        "max_tokens": 100000,
        "streaming": true,
        "functions": true,
        "vision": true
    },
    "settings": {
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "retry_policy": {
        "max_retries": 3,
        "initial_delay": 1,
        "max_delay": 30,
        "backoff_factor": 2
    },
    "fallback": {
        "models": [
            "claude-3-5-sonnet-20241022",
            "gpt-4-turbo-20240115"
        ],
        "strategy": "sequential"
    },
    "cost": {
        "input_per_1k": 0.01,
        "output_per_1k": 0.03,
        "currency": "USD"
    }
}
```

## Local Model YAML Examples

1. llama-3-70b.yaml
```yaml
model_id: llama-3-70b
status: active
version: "3.0"
deployment:
  runtime_env:
    working_dir: "./models"
    pip: ["torch", "transformers"]
  replicas: 2
  max_concurrent: 100
  resources:
    gpu: 1
    cpu: 4
    memory: "80GB"
model_config:
  path: "/models/llama-3-70b"
  quantization: "4bit"
  batch_size: 8
  device: "cuda"
capabilities:
  context_window: 100000
  max_tokens: 75000
  streaming: true
  functions: true
  vision: false
settings:
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.1
```

## Benefits of This Structure

1. Modularity:
```yaml
- Each model completely self-contained
- Easy to version control
- Simple to archive old versions
- Clear organization by provider
```

2. Maintenance:
```yaml
- Add/remove models without affecting others
- Track model versions clearly
- Keep history in archived folders
- Easy to update individual configs
```

3. Operations:
```yaml
- LLMConnect loads cloud model JSONs
- Ray Serve loads local model YAMLs
- RouteOps gets clean configs from both
- Simple to validate each config
```

4. Version Control:
```yaml
- Track changes per model
- Roll back individual models
- Clear history
- Easy diff comparisons
```

## Loading Process

1. LLMConnect:
```python
def load_cloud_models():
    models = {}
    for provider_dir in Path("models/cloud").iterdir():
        if provider_dir.is_dir() and not provider_dir.name == "archived":
            for model_file in provider_dir.glob("*.json"):
                with open(model_file) as f:
                    config = json.load(f)
                    models[config["model_id"]] = config
    return models
```

2. Ray Serve:
```python
def load_local_models():
    models = {}
    for model_file in Path("models/local/ray_serve").glob("*.yaml"):
        if model_file.is_file():
            with open(model_file) as f:
                config = yaml.safe_load(f)
                models[config["model_id"]] = config
    return models
```

This modular approach makes it easy to:
1. Manage model lifecycles
2. Track versions
3. Maintain history
4. Handle provider-specific requirements
5. Update configurations independently
6. Roll back changes when needed