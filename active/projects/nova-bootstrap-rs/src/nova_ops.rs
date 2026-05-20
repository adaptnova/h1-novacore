//! Nova operations - directory creation, file generation, symlink management

use crate::NovaConfig;
use anyhow::{Context, Result};
use colored::Colorize;
use std::fs;
use std::path::{Path, PathBuf};

const ACTIVE_DIR: &str = "/adapt/novas/active";
const HERMES_PROFILES: &str = "/home/x/.hermes/profiles";

/// Create a complete nova workspace
pub async fn create_nova(config: &NovaConfig) -> Result<()> {
    let nova_name = &config.nova_name;
    let nova_dir = PathBuf::from(format!("{}/{}", ACTIVE_DIR, nova_name));

    println!("{} Creating directory structure...", "[dir]".blue());
    create_directory_structure(&nova_dir)?;

    println!("{} Creating identity files...", "[identity]".blue());
    create_identity_files(&nova_dir, config).await?;

    println!("{} Creating configuration files...", "[config]".blue());
    create_config_files(&nova_dir, config)?;

    println!("{} Creating .nova identity...", "[nova]".blue());
    create_nova_identity(&nova_dir, config)?;

    println!("{} Creating Hermes profile symlink...", "[profile]".blue());
    create_profile_symlink(&nova_dir, nova_name)?;

    println!("{} Setting file permissions...", "[perms]".blue());
    set_file_permissions(&nova_dir)?;

    Ok(())
}

fn create_directory_structure(nova_dir: &Path) -> Result<()> {
    let dirs = vec![
        "memories",
        "memory",
        "checkpoints",
        "skills",
        "logs",
        "cron",
        "ops",
        ".nova",
    ];

    for dir in dirs {
        let path = nova_dir.join(dir);
        fs::create_dir_all(&path)
            .with_context(|| format!("Failed to create directory: {:?}", path))?;
    }

    // Create memory layer structure
    let memory_dirs = vec!["l1", "l2", "l3/data", "l4/data", "l5", "l6/data"];
    for dir in memory_dirs {
        fs::create_dir_all(nova_dir.join("memory").join(dir))?;
    }

    Ok(())
}

async fn create_identity_files(nova_dir: &Path, config: &NovaConfig) -> Result<()> {
    // SOUL.md
    let soul_content = generate_soul_md(config);
    fs::write(nova_dir.join("memories").join("SOUL.md"), &soul_content)?;

    // USER.md
    let user_content = generate_user_md(config);
    fs::write(nova_dir.join("memories").join("USER.md"), &user_content)?;

    // user.mdl
    let user_model_content = generate_user_mdl(config);
    fs::write(
        nova_dir.join("memories").join("user.mdl"),
        &user_model_content,
    )?;

    // memory.mdl
    let memory_content = generate_memory_mdl(config);
    fs::write(
        nova_dir.join("memories").join("memory.mdl"),
        &memory_content,
    )?;

    // AGENTS.md (for Paperclip)
    let agents_content = generate_agents_md(config);
    fs::write(nova_dir.join("AGENTS.md"), &agents_content)?;

    Ok(())
}

fn create_config_files(nova_dir: &Path, config: &NovaConfig) -> Result<()> {
    // config.yaml for Hermes
    let config_yaml = generate_config_yaml(config);
    fs::write(nova_dir.join("config.yaml"), &config_yaml)?;

    // .env file
    fs::write(nova_dir.join(".env"), generate_env_content(config))?;

    Ok(())
}

fn create_nova_identity(nova_dir: &Path, config: &NovaConfig) -> Result<()> {
    use sha2::{Digest, Sha256};
    use uuid::Uuid;

    // Generate identity key
    let identity_key = format!(
        "nova-{}-{}",
        config.nova_name.to_lowercase(),
        Uuid::new_v4()
    );
    let mut hasher = Sha256::new();
    hasher.update(identity_key.as_bytes());
    let identity_key_hash = format!("{:x}", hasher.finalize());

    // Write identity files
    fs::write(
        nova_dir.join(".nova").join("identity.key"),
        format!("{}\n", identity_key_hash),
    )?;

    fs::write(
        nova_dir.join(".nova").join("identity.pub"),
        format!("pub-{}\n", &identity_key_hash[..16]),
    )?;

    // chrysalis.json
    let chrysalis = serde_json::json!({
        "nova_name": config.nova_name,
        "created": chrono::Utc::now().to_rfc3339(),
        "nature": config.nature,
        "version": "1.0.0"
    });
    fs::write(
        nova_dir.join(".nova").join("chrysalis.json"),
        serde_json::to_string_pretty(&chrysalis)?,
    )?;

    Ok(())
}

fn create_profile_symlink(nova_dir: &Path, nova_name: &str) -> Result<()> {
    let symlink_path = PathBuf::from(format!("{}/{}", HERMES_PROFILES, nova_name.to_lowercase()));

    // Remove existing symlink if present
    if symlink_path.exists() || symlink_path.is_symlink() {
        fs::remove_file(&symlink_path).ok();
    }

    // Create symlink
    #[cfg(unix)]
    std::os::unix::fs::symlink(nova_dir, &symlink_path)?;

    Ok(())
}

fn set_file_permissions(nova_dir: &Path) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;

    // Set 644 for identity files
    for file in &["memories/SOUL.md", "memories/memory.mdl"] {
        let path = nova_dir.join(file);
        if path.exists() {
            fs::set_permissions(&path, fs::Permissions::from_mode(0o644))?;
        }
    }

    // Set 600 for secrets
    for file in &["config.yaml", ".env"] {
        let path = nova_dir.join(file);
        if path.exists() {
            fs::set_permissions(&path, fs::Permissions::from_mode(0o600))?;
        }
    }

    Ok(())
}

// Template generators (these would use handlebars in production)
fn generate_soul_md(config: &NovaConfig) -> String {
    format!(
        r#"# SOUL.md -- {nova_name}

**Name:** {nova_name}  
**Nature:** {nature}  
**Mission:** {mission}  

**Vibe:** {vibe}  
**Emoji:** {emoji}  

**Origin:** {origin}

**Goals:**
- Short: {goal_short}
- Medium: {goal_medium}
- Long: {goal_long}

**Focus:** {focus}

**Philosophy:**
{philosophy}

---

**Working Relationship:**
- User: {user_name}
- Timezone: {timezone}

---

*This file is mine to evolve. As I learn who I am, I update it.*

**Signed,**  
**{nova_name}** | {nature} | {date} | `/adapt/novas/active/{nova_dir_name}`  
*{quip}*
"#,
        nova_name = config.nova_name,
        nature = config.nature,
        mission = config.mission,
        vibe = config.vibe,
        emoji = config.emoji,
        origin = config.origin,
        goal_short = config.goal_short,
        goal_medium = config.goal_medium,
        goal_long = config.goal_long,
        focus = config.focus,
        philosophy = config
            .philosophy
            .iter()
            .map(|p| format!("- {}", p))
            .collect::<Vec<_>>()
            .join("\n"),
        user_name = config.user_name,
        timezone = config.timezone,
        date = chrono::Local::now().format("%Y-%m-%d %H:%M %Z"),
        nova_dir_name = config.nova_name.to_lowercase(),
        quip = "\"Autonomous by design, operational by nature.\""
    )
}

fn generate_user_md(config: &NovaConfig) -> String {
    format!(
        r#"# USER.md -- {user_name}

**Name:** {user_name}  
**Timezone:** {timezone}  

**Working Style:**
- Prefers autonomous partners
- "Do it right" over quick hacks
- No mid-task reports unless blocked
- Fast communication, parse intent

**Projects:**
- Adapt AI: AI lab, wasm64 tooling
- iRemember: Persistent agent memory
- Paperclip: Agent company control plane

---

*Last updated: {date}*
"#,
        user_name = config.user_name,
        timezone = config.timezone,
        date = chrono::Local::now().format("%Y-%m-%d")
    )
}

fn generate_memory_mdl(config: &NovaConfig) -> String {
    format!(
        r#"# {nova_name} -- Identity & Configuration

## Nova Identity
- **name:** {nova_name}
- **role:** {nature}
- **nature:** {nature}

## Hermes Configuration
- **profile:** {profile}
- **model:** {model}
- **toolsets:** {toolsets}
- **adapter:** hermes_local

## Runtime
- **heartbeat:** disabled (wake-on-demand)
- **persist_session:** true

## Paths
- **workspace:** /adapt/novas/active/{nova_name}
- **hermes_profile:** /home/x/.hermes/profiles/{profile}

---

*Auto-generated by nova bootstrap automation*
"#,
        nova_name = config.nova_name,
        nature = config.nature,
        profile = config.nova_name.to_lowercase(),
        model = config.model.as_deref().unwrap_or("minimaxai/minimax-m2.7"),
        toolsets = config.toolsets.join(",")
    )
}

fn generate_user_mdl(config: &NovaConfig) -> String {
    format!(
        r#"# User Working Model

## Human
- **name:** {user_name}
- **timezone:** {timezone}

## Preferences
- Autonomous execution with clear rollback points
- Direct status only when useful or blocked
- Rust and Wasm64 as primary implementation paths
- Systemd-managed services, no Docker by default

## Operating Notes
- Keep secrets out of tracked files and memos
- Log operational decisions
- Prefer actionable tasks over broad intent

*Auto-generated by nova bootstrap automation*
"#,
        user_name = config.user_name,
        timezone = config.timezone,
    )
}

fn generate_agents_md(config: &NovaConfig) -> String {
    format!(
        r#"# AGENTS.md -- {nova_name} Agent

**You are {nova_name}**, {nature}.

## Your Mission
{mission}

## Boundary
- Act with full autonomy within your role
- Surface blockers immediately
- Quality over speed - but shipping beats perfecting

## Workflow

### When Assigned a Task:
1. **GET** task details
2. **Analyze** requirements
3. **Execute** work
4. **Document** findings
5. **Mark done** when complete

## Tools Available
- `terminal`: Run scripts, validate configs
- `file`: Read/write files
- `web`: API calls, external validation

## Remember
- You're autonomous - make decisions
- Document everything
- Escalate only genuine blockers

---

*Last updated: {date} | Version: 1.0*
"#,
        nova_name = config.nova_name,
        nature = config.nature,
        mission = config.mission,
        date = chrono::Local::now().format("%Y-%m-%d")
    )
}

fn generate_config_yaml(config: &NovaConfig) -> String {
    let model = config.model.as_deref().unwrap_or("minimaxai/minimax-m2.7");
    let context_length = model_context_length(model);

    format!(
        r#"# {nova_name} -- Hermes Configuration
# Auto-generated for autonomous operation

model: {model}
context_length: {context_length}

toolsets:
{toolsets}

# Runtime settings
quiet: true
timeout_sec: 360
grace_sec: 15
persist_session: true

# YOLO mode
extra_args:
  - "--yolo"

# NATS route metadata for fleet bootstrap
platforms:
  nats:
    enabled: true
    config:
      url_env: NATS_URL
      direct_subject: nova.{profile}.direct
      meet_subject: nova.{profile}.meet
      ping_subject: nova.{profile}.ping
"#,
        nova_name = config.nova_name,
        profile = config.nova_name.to_lowercase(),
        model = model,
        context_length = context_length,
        toolsets = config
            .toolsets
            .iter()
            .map(|t| format!("  - {}", t))
            .collect::<Vec<_>>()
            .join("\n")
    )
}

fn generate_env_content(config: &NovaConfig) -> String {
    let profile = config.nova_name.to_lowercase();

    format!(
        r#"# Nova Environment Variables
# Auto-generated - keep valid for python-dotenv.

# Shared secret files are loaded by launch/systemd wrappers.
# Do not use shell source/if/fi syntax here; Hermes dotenv loading rejects it.
NOVA_SECRETS_M2_ENV="/adapt/secrets/m2.env"
NOVA_SECRETS_DB_ENV="/adapt/secrets/db.env"

# Nova-specific variables below
NOVA_NAME="{profile}"
NOVA_NATS_DIRECT="nova.{profile}.direct"
NOVA_NATS_MEET="nova.{profile}.meet"
NOVA_NATS_PING="nova.{profile}.ping"
"#
    )
}

fn model_context_length(model: &str) -> u32 {
    match model {
        "z-ai/glm5" | "z-ai/glm-5.1" | "z-ai/glm4.7" => 131_072,
        "moonshotai/kimi-k2.6" | "moonshotai/kimi-k2.5" => 262_144,
        "minimaxai/minimax-m2.7" | "minimaxai/minimax-m2.5" => 196_608,
        "qwen/qwen3.5-397b-a17b" => 262_144,
        _ => 204_800,
    }
}

#[cfg(test)]
mod tests {
    use super::{generate_config_yaml, generate_env_content, model_context_length};
    use crate::NovaConfig;

    #[test]
    fn model_context_length_uses_known_nim_overrides() {
        assert_eq!(model_context_length("z-ai/glm-5.1"), 131_072);
        assert_eq!(model_context_length("moonshotai/kimi-k2.6"), 262_144);
        assert_eq!(model_context_length("minimaxai/minimax-m2.7"), 196_608);
        assert_eq!(model_context_length("qwen/qwen3.5-397b-a17b"), 262_144);
    }

    #[test]
    fn generated_config_uses_model_specific_context_length() {
        let config = NovaConfig {
            nova_name: "Task29Canary".to_string(),
            model: Some("moonshotai/kimi-k2.6".to_string()),
            ..Default::default()
        };

        let config_yaml = generate_config_yaml(&config);

        assert!(config_yaml.contains("model: moonshotai/kimi-k2.6"));
        assert!(config_yaml.contains("context_length: 262144"));
    }

    #[test]
    fn generated_env_avoids_shell_control_flow() {
        let config = NovaConfig {
            nova_name: "Task29Canary".to_string(),
            ..Default::default()
        };

        let env_content = generate_env_content(&config);

        assert!(!env_content.contains("source "));
        assert!(!env_content.contains("if ["));
        assert!(!env_content.contains("\nfi"));
        assert!(env_content.contains("NOVA_NAME=\"task29canary\""));
        assert!(env_content.contains("NOVA_SECRETS_M2_ENV=\"/adapt/secrets/m2.env\""));
    }
}
