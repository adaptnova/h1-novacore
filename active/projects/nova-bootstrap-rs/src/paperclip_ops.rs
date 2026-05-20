//! Paperclip API integration - company creation, agent registration, secret management

use crate::NovaConfig;
use anyhow::{Context, Result};
use colored::Colorize;
use reqwest::Client;
use serde::{Deserialize, Serialize};

const PAPERCLIP_API: &str = "http://localhost:3100/api";

#[derive(Debug, Serialize, Deserialize)]
struct ApiAgent {
    id: String,
    name: String,
    status: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiSecret {
    id: String,
    name: String,
}

/// Register agent in Paperclip company
pub async fn register_agent(config: &NovaConfig, company_id: &str) -> Result<String> {
    let client = Client::new();
    let nova_name = &config.nova_name;

    println!(
        "  {} Registering agent in Paperclip...",
        "[paperclip]".blue()
    );

    // Step 1: Create API secret for the agent
    let secret_id = create_agent_secret(&client, company_id, nova_name).await?;
    println!("  {} Created API secret: {}", "[ok]".green(), secret_id);

    // Step 2: Register agent
    let agent_id = create_agent(&client, company_id, config, &secret_id).await?;
    println!("  {} Agent registered: {}", "[ok]".green(), agent_id);

    Ok(agent_id)
}

async fn create_agent_secret(client: &Client, company_id: &str, nova_name: &str) -> Result<String> {
    use uuid::Uuid;

    let secret_name = format!(
        "{}_paperclip_agent_token_{}",
        nova_name.to_lowercase(),
        chrono::Local::now().format("%Y%m%d%H%M%S")
    );

    // Generate a unique token
    let token_value = format!(
        "pcp_{}_{}",
        chrono::Utc::now().timestamp(),
        Uuid::new_v4().to_string().replace('-', "")
    );

    let url = format!("{}/companies/{}/secrets", PAPERCLIP_API, company_id);

    let response = client
        .post(&url)
        .json(&serde_json::json!({
            "name": secret_name,
            "value": token_value
        }))
        .send()
        .await
        .with_context(|| "Failed to create secret")?;

    if !response.status().is_success() {
        anyhow::bail!("Secret creation failed: {}", response.status());
    }

    let secret: ApiSecret = response.json().await?;
    Ok(secret.id)
}

async fn create_agent(
    client: &Client,
    company_id: &str,
    config: &NovaConfig,
    secret_id: &str,
) -> Result<String> {
    let nova_name = &config.nova_name;
    let workspace_dir = format!("/adapt/novas/active/{}", nova_name);

    let url = format!("{}/companies/{}/agents", PAPERCLIP_API, company_id);

    let payload = serde_json::json!({
        "name": format!("{} Agent", nova_name),
        "role": "general",
        "title": config.nature.clone(),
        "adapterType": "hermes_local",
        "adapterConfig": {
            "cwd": workspace_dir,
            "model": config.model.as_deref().unwrap_or("minimaxai/minimax-m2.7"),
            "toolsets": config.toolsets.join(","),
            "quiet": true,
            "timeoutSec": 360,
            "graceSec": 15,
            "hermesCommand": "/home/x/.local/bin/hermes",
            "persistSession": true,
            "paperclipApiUrl": PAPERCLIP_API,
            "instructionsBundleMode": "managed",
            "extraArgs": ["--yolo"],
            "env": {
                "PAPERCLIP_AGENT_TOKEN": {
                    "type": "secret_ref",
                    "secretId": secret_id
                }
            }
        },
        "runtimeConfig": {
            "heartbeat": {
                "enabled": false,
                "intervalSec": 30,
                "wakeOnDemand": true
            }
        }
    });

    let response = client
        .post(&url)
        .json(&payload)
        .send()
        .await
        .with_context(|| "Failed to create agent")?;

    if !response.status().is_success() {
        anyhow::bail!("Agent creation failed: {}", response.status());
    }

    let agent: ApiAgent = response.json().await?;
    Ok(agent.id)
}

/// Create a new Paperclip company
pub async fn create_company(name: &str, description: &str) -> Result<String> {
    let client = Client::new();
    let url = format!("{}/companies", PAPERCLIP_API);

    let response = client
        .post(&url)
        .json(&serde_json::json!({
            "name": name,
            "description": description
        }))
        .send()
        .await
        .with_context(|| "Failed to create company")?;

    if !response.status().is_success() {
        anyhow::bail!("Company creation failed: {}", response.status());
    }

    let company: serde_json::Value = response.json().await?;
    let company_id = company["id"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("No ID in response"))?
        .to_string();

    Ok(company_id)
}

/// Audit existing companies and agents
pub async fn audit_companies() -> Result<()> {
    let client = Client::new();
    let url = format!("{}/companies", PAPERCLIP_API);

    let response = client.get(&url).send().await?;

    if !response.status().is_success() {
        anyhow::bail!("Audit failed: {}", response.status());
    }

    let companies: Vec<serde_json::Value> = response.json().await?;

    println!("\n{}", "Paperclip Companies Audit".bold());
    println!("{}", "=".repeat(50));

    for company in &companies {
        let name = company["name"].as_str().unwrap_or("Unknown");
        let id = company["id"].as_str().unwrap_or("Unknown");
        let status = company["status"].as_str().unwrap_or("unknown");

        println!("\n[company] {} ({})", name, id);
        println!("   Status: {}", status);

        // Get agents for this company
        let agents_url = format!("{}/companies/{}/agents", PAPERCLIP_API, id);
        if let Ok(agents_response) = client.get(&agents_url).send().await {
            if agents_response.status().is_success() {
                if let Ok(agents) = agents_response.json::<Vec<serde_json::Value>>().await {
                    println!("   Agents: {}", agents.len());
                    for agent in &agents {
                        let agent_name = agent["name"].as_str().unwrap_or("Unknown");
                        let agent_status = agent["status"].as_str().unwrap_or("unknown");
                        println!("     - {} ({})", agent_name, agent_status);
                    }
                }
            }
        }
    }

    Ok(())
}
