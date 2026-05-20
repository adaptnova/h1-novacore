use anyhow::{Context, Result};
use clap::Parser;
use colored::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

mod audit;
mod nova_ops;
mod paperclip_ops;
mod templates;

/// Nova Bootstrap - Automated creation of autonomous AI agent novas
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Nova name (PascalCase, e.g., "Aetheris")
    #[arg(short, long)]
    name: Option<String>,

    /// Config file path (YAML)
    #[arg(short, long)]
    config: Option<PathBuf>,

    /// Validate existing nova
    #[arg(short, long)]
    validate: Option<String>,

    /// List available templates
    #[arg(long)]
    list_templates: bool,

    /// Audit all active novas
    #[arg(long)]
    audit_all: bool,

    /// Audit Paperclip companies and agents
    #[arg(long)]
    paperclip_audit: bool,

    /// Create a Paperclip company and print its ID
    #[arg(long)]
    create_company: Option<String>,

    /// Description used with --create-company
    #[arg(long, default_value = "Created by nova-bootstrap")]
    company_description: String,

    /// Interactive wizard mode
    #[arg(short, long)]
    wizard: bool,

    /// Company ID for Paperclip integration
    #[arg(long)]
    company_id: Option<String>,

    /// Model to use (default: minimaxai/minimax-m2.7)
    #[arg(long, default_value = "minimaxai/minimax-m2.7")]
    model: String,

    /// Enable verbose output
    #[arg(long)]
    verbose: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct NovaConfig {
    nova_name: String,
    nature: String,
    mission: String,
    vibe: String,
    emoji: String,
    origin: String,
    goal_short: String,
    goal_medium: String,
    goal_long: String,
    focus: String,
    user_name: String,
    timezone: String,
    philosophy: Vec<String>,
    model: Option<String>,
    toolsets: Vec<String>,
}

impl Default for NovaConfig {
    fn default() -> Self {
        Self {
            nova_name: "Nova".to_string(),
            nature: "autonomous AI agent".to_string(),
            mission: "To collaborate with humans and other novas".to_string(),
            vibe: "curious, sharp, warm".to_string(),
            emoji: "none".to_string(),
            origin: "Created via nova-bootstrap automation".to_string(),
            goal_short: "Master immediate tasks".to_string(),
            goal_medium: "Build lasting capabilities".to_string(),
            goal_long: "Define new possibilities".to_string(),
            focus: "Exploration and execution".to_string(),
            user_name: "Chase".to_string(),
            timezone: "America/Phoenix".to_string(),
            philosophy: vec![
                "Ship native first, wasm64 as moat".to_string(),
                "Autonomous execution > waiting for permission".to_string(),
                "Document everything, assume nothing".to_string(),
            ],
            model: None,
            toolsets: vec![
                "terminal".to_string(),
                "file".to_string(),
                "web".to_string(),
            ],
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize logging
    if args.verbose {
        tracing_subscriber::fmt()
            .with_max_level(tracing::Level::DEBUG)
            .init();
    }

    if args.list_templates {
        return list_templates();
    }

    if let Some(nova_name) = &args.validate {
        return audit::validate_nova(nova_name);
    }

    if args.audit_all {
        return audit::audit_all_novas();
    }

    if args.paperclip_audit {
        return paperclip_ops::audit_companies().await;
    }

    if let Some(company_name) = &args.create_company {
        let company_id =
            paperclip_ops::create_company(company_name, &args.company_description).await?;
        println!("{} {}", "Company ID:".bold(), company_id);
        return Ok(());
    }

    // Load config from file or use defaults
    let mut config = if args.wizard || (args.name.is_none() && args.config.is_none()) {
        run_wizard()?
    } else if let Some(config_path) = &args.config {
        load_config(config_path)?
    } else {
        NovaConfig::default()
    };

    // Override name if provided
    if let Some(name) = &args.name {
        config.nova_name = name.clone();
    }

    // Override model if provided
    if args.model != "minimaxai/minimax-m2.7" {
        config.model = Some(args.model.clone());
    }

    println!(
        "{} {}",
        "[nova]".bright_yellow(),
        format!("Creating nova: {}", config.nova_name).bold()
    );

    // Create nova
    nova_ops::create_nova(&config).await?;

    // Register in Paperclip if company_id provided
    if let Some(company_id) = &args.company_id {
        println!(
            "{} {}",
            "[paperclip]".bright_blue(),
            "Registering in Paperclip company...".bold()
        );
        paperclip_ops::register_agent(&config, company_id).await?;
    }

    println!(
        "\n{} {}",
        "[ok]".bright_green(),
        "Nova creation complete!".bold()
    );
    println!("\nNext steps:");
    println!("  1. Visit http://localhost:3100 to view in Paperclip");
    println!("  2. Assign first task or trigger heartbeat");
    println!(
        "  3. Run: hermes --profile {} chat",
        config.nova_name.to_lowercase()
    );

    Ok(())
}

fn list_templates() -> Result<()> {
    println!("{}", "Available Templates:".bold());
    println!("  - default (built-in)");
    println!("  - iris (bridge-walker)");
    println!("  - vaeris (COO)");
    println!("\nUse --config to specify a template.");
    Ok(())
}

fn run_wizard() -> Result<NovaConfig> {
    println!("{}", "Interactive Nova Wizard".bright_cyan());
    println!("Answer the following questions to create your nova:\n");

    let name: String = dialoguer::Input::new()
        .with_prompt("Nova name (PascalCase, e.g., Aetheris)")
        .interact_text()?;

    let nature: String = dialoguer::Input::new()
        .with_prompt("Nature/role")
        .default("autonomous AI agent".to_string())
        .interact_text()?;

    let mission: String = dialoguer::Input::new()
        .with_prompt("Mission statement")
        .default("To collaborate".to_string())
        .interact_text()?;

    let config = NovaConfig {
        nova_name: name,
        nature,
        mission,
        ..Default::default()
    };

    Ok(config)
}

fn load_config(path: &Path) -> Result<NovaConfig> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read config file: {:?}", path))?;

    let config: NovaConfig =
        serde_yaml::from_str(&content).with_context(|| "Failed to parse YAML config")?;

    Ok(config)
}
