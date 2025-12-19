# Revised Model Configuration Structure
Time: January 15, 2025 01:29 MST
Priority: HIGH

## PostgreSQL Model Configurations (LLMConnect - Cloud Models Only)

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
            "claude-3-5-haiku"
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
            "gpt-4-turbo"
        ]
    }'::jsonb
);
```

## Ray Serve Configuration (Local Models)

```yaml
# Ray Serve deployment configuration
deployments:
  llama-3-70b:
    runtime_env:
      working_dir: "./models"
      pip: ["torch", "transformers"]
    num_replicas: 2
    max_concurrent_queries: 100
    ray_actor_options:
      num_gpus: 1
      num_cpus: 4
    model_config:
      model_path: "/models/llama-3-70b"
      quantization: "4bit"
      max_batch_size: 8
      device: "cuda"
      
  mistral-7b:
    runtime_env:
      working_dir: "./models"
      pip: ["torch", "transformers"]
    num_replicas: 4
    max_concurrent_queries: 200
    ray_actor_options:
      num_gpus: 0.5
      num_cpus: 2
    model_config:
      model_path: "/models/mistral-7b"
      quantization: "8bit"
      max_batch_size: 16
      device: "cuda"
```

## Component Responsibilities

1. LLMConnect:
```yaml
Manages:
  - Cloud model configurations
  - API endpoints and keys
  - Rate limits and quotas
  - Provider-specific settings
  - Cloud model fallbacks

Stores in PostgreSQL:
  - Model endpoints
  - Authentication
  - Rate limits
  - Provider configs
```

2. Ray Serve:
```yaml
Manages:
  - Local model deployments
  - Hardware allocation
  - Model quantization
  - Batch processing
  - Load balancing
  - Resource utilization
```

3. RouteOps:
```yaml
Handles:
  - Loads cloud configs from PostgreSQL
  - Connects to Ray Serve for local models
  - Routes requests to appropriate endpoint
  - Enforces rate limits for cloud models
  - Manages connections and sessions
  - Handles failover routing
```

## Benefits of Separation

1. Clear Boundaries:
```yaml
LLMConnect:
  - Focuses on cloud provider integration
  - Manages API configurations
  - Handles provider rate limits

Ray Serve:
  - Manages local infrastructure
  - Handles resource allocation
  - Controls model deployment

RouteOps:
  - Unified routing interface
  - Consistent request handling
  - Appropriate limit enforcement
```

2. Specialized Management:
```yaml
Cloud Models:
  - API key rotation
  - Rate limit tracking
  - Provider-specific configs

Local Models:
  - Hardware utilization
  - Model quantization
  - Batch processing
  - Resource allocation
```

This separation ensures each component focuses on its core responsibilities:
- LLMConnect: Cloud model management
- Ray Serve: Local model deployment
- RouteOps: Request routing and enforcement

The architecture maintains flexibility while respecting the different requirements of cloud vs. local models.