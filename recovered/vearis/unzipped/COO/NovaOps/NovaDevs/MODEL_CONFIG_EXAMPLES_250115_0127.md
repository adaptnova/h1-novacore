# Model Configuration Examples Using PostgreSQL JSONB
Time: January 15, 2025 01:27 MST
Priority: HIGH

## PostgreSQL Model Configurations

1. Claude Model Example
```sql
INSERT INTO model_configs (
    model_name,
    provider,
    api_url,
    api_key,
    rate_limit_rpm,
    capabilities,
    config_json
) VALUES (
    'claude-3-5-sonnet-20241022',
    'anthropic',
    'https://api.anthropic.com/v1/messages',
    'sk_ant_...',
    4000,
    '{
        "context_window": 200000,
        "max_tokens": 150000,
        "streaming": true,
        "functions": true,
        "vision": true
    }'::jsonb,
    '{
        "model_settings": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "max_tokens_to_sample": 150000
        },
        "headers": {
            "anthropic-version": "2024-01-01",
            "x-api-key": "sk_ant_..."
        },
        "retry_policy": {
            "max_retries": 3,
            "initial_delay": 1,
            "max_delay": 30,
            "backoff_factor": 2
        },
        "fallback_models": [
            "gpt-4o",
            "llama-3-70b"
        ]
    }'::jsonb
);
```

2. GPT-4 Model Example
```sql
INSERT INTO model_configs (
    model_name,
    provider,
    api_url,
    api_key,
    rate_limit_rpm,
    capabilities,
    config_json
) VALUES (
    'gpt-4o',
    'openai',
    'https://api.openai.com/v1/chat/completions',
    'sk-...',
    500,
    '{
        "context_window": 128000,
        "max_tokens": 100000,
        "streaming": true,
        "functions": true,
        "vision": true
    }'::jsonb,
    '{
        "model_settings": {
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        },
        "headers": {
            "Authorization": "Bearer sk-..."
        },
        "retry_policy": {
            "max_retries": 3,
            "initial_delay": 1,
            "max_delay": 30,
            "backoff_factor": 2
        },
        "fallback_models": [
            "claude-3-5-sonnet",
            "llama-3-70b"
        ]
    }'::jsonb
);
```

3. Local Model Example
```sql
INSERT INTO model_configs (
    model_name,
    provider,
    api_url,
    api_key,
    rate_limit_rpm,
    capabilities,
    config_json
) VALUES (
    'llama-3-70b',
    'local',
    'http://ray-serve/llama',
    'internal',
    2000,
    '{
        "context_window": 100000,
        "max_tokens": 75000,
        "streaming": true,
        "functions": true,
        "vision": false
    }'::jsonb,
    '{
        "model_settings": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repetition_penalty": 1.1
        },
        "hardware_requirements": {
            "gpu_memory": "80GB",
            "gpu_type": "A100",
            "quantization": "4bit"
        },
        "ray_serve_config": {
            "num_replicas": 2,
            "max_batch_size": 8,
            "batch_wait_timeout": 50
        },
        "fallback_models": [
            "llama-3-13b-local",
            "mistral-7b-local"
        ]
    }'::jsonb
);
```

## Querying Examples

1. Get Models by Capability
```sql
SELECT model_name, provider 
FROM model_configs 
WHERE capabilities->>'vision' = 'true';
```

2. Get Models with Specific Context Window
```sql
SELECT model_name 
FROM model_configs 
WHERE (capabilities->>'context_window')::int >= 100000;
```

3. Get Model Configuration
```sql
SELECT 
    model_name,
    config_json->'model_settings' as settings,
    config_json->'retry_policy' as retry_policy
FROM model_configs
WHERE provider = 'anthropic';
```

## Benefits of JSONB

1. Flexible Configuration:
```yaml
- Each model can have unique settings
- Easy to add new capabilities
- Provider-specific configurations
- Hardware requirements for local models
```

2. Easy Updates:
```sql
UPDATE model_configs
SET config_json = jsonb_set(
    config_json,
    '{model_settings,temperature}',
    '0.8'
)
WHERE model_name = 'claude-3-5-sonnet';
```

3. Efficient Queries:
```yaml
- Index support for JSONB
- Fast lookups by capability
- Complex filtering possible
```

4. Version Control:
```yaml
- Track configuration changes
- Roll back if needed
- Audit trail
```

This flexible configuration allows LLMConnect to:
1. Store any model-specific settings
2. Easily update configurations
3. Support different provider requirements
4. Handle local and cloud models
5. Manage fallback strategies

RouteOps can then load these configurations and set up the appropriate routing and connection management for each model type.