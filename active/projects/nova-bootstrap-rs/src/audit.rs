//! Audit and validation utilities

use anyhow::{Context, Result};
use colored::*;
use std::path::{Path, PathBuf};

const ACTIVE_DIR: &str = "/adapt/novas/active";
const HERMES_PROFILES: &str = "/home/x/.hermes/profiles";

/// Validate a nova's structure
pub fn validate_nova(nova_name: &str) -> Result<()> {
    let nova_dir = PathBuf::from(format!("{}/{}", ACTIVE_DIR, nova_name));

    if !nova_dir.exists() {
        anyhow::bail!("Nova directory not found: {:?}", nova_dir);
    }

    println!(
        "\n{} Validating nova: {}\n",
        "[audit]".blue(),
        nova_name.bold()
    );

    let required = vec!["memories/SOUL.md", "memories/memory.mdl", "config.yaml"];

    let recommended = vec!["memories/USER.md", "memories/user.mdl", ".env", "AGENTS.md"];

    let optional = vec![
        "memories/SYSTEM.md",
        "memories/LAYERED_MEMORY.md",
        "memory/",
        "checkpoints/",
        "skills/",
    ];

    let mut all_ok = true;

    println!("Required files:");
    for file in required {
        let path = nova_dir.join(file);
        let exists = path.exists();
        let status = if exists {
            "[ok]".green()
        } else {
            "[missing]".red()
        };
        println!("  {} {}", status, file);
        if !exists {
            all_ok = false;
        }
    }

    println!("\nRecommended files:");
    for file in recommended {
        let path = nova_dir.join(file);
        let exists = path.exists();
        let status = if exists {
            "[ok]".green()
        } else {
            "[warn]".yellow()
        };
        println!("  {} {}", status, file);
    }

    println!("\nOptional directories:");
    for dir in optional {
        let path = nova_dir.join(dir);
        let exists = path.exists();
        let status = if exists {
            "[ok]".green()
        } else {
            "[skip]".dimmed()
        };
        println!("  {} {}", status, dir);
    }

    // Check symlink
    let symlink_path = format!("{}/{}", HERMES_PROFILES, nova_name.to_lowercase());
    let symlink_exists = Path::new(&symlink_path).exists();
    let status = if symlink_exists {
        "[ok]".green()
    } else {
        "[missing]".red()
    };
    println!("\nProfile symlink:");
    println!("  {} {}", status, symlink_path);

    if all_ok && symlink_exists {
        println!("\n{} Nova validation passed!", "[ok]".bright_green());
    } else {
        println!(
            "\n{} Nova validation failed - missing critical files",
            "[failed]".bright_red()
        );
        std::process::exit(1);
    }

    Ok(())
}

/// Audit all novas in the active directory
pub fn audit_all_novas() -> Result<()> {
    use std::fs;

    println!("\n{}", "Nova Audit Report".bold());
    println!("{}", "=".repeat(80));

    let mut complete = 0;
    let mut incomplete = 0;
    let mut total = 0;

    let entries = fs::read_dir(ACTIVE_DIR)
        .with_context(|| format!("Failed to read directory: {}", ACTIVE_DIR))?;

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown");

        // Skip template and special directories
        if name.starts_with('_') || name == "a_nova_template" {
            continue;
        }

        total += 1;

        let has_soul = path.join("memories/SOUL.md").exists();
        let has_user = path.join("memories/USER.md").exists();
        let has_env = path.join(".env").exists();
        let has_nova_dir = path.join(".nova").is_dir();

        let is_complete = has_soul && has_user && has_env && has_nova_dir;

        if is_complete {
            complete += 1;
            println!("{} {}", "[ok]".green(), name);
        } else {
            incomplete += 1;
            let mut missing = Vec::new();
            if !has_soul {
                missing.push("SOUL.md");
            }
            if !has_user {
                missing.push("USER.md");
            }
            if !has_env {
                missing.push(".env");
            }
            if !has_nova_dir {
                missing.push(".nova/");
            }

            println!(
                "{} {} - Missing: {}",
                "[missing]".red(),
                name,
                missing.join(", ")
            );
        }
    }

    let complete_percent = percentage(complete, total);
    let incomplete_percent = percentage(incomplete, total);

    println!("\n{}", "Summary".bold());
    println!("{}", "=".repeat(80));
    println!("Total novas: {}", total);
    println!("Complete: {} ({}%)", complete, complete_percent);
    println!("Incomplete: {} ({}%)", incomplete, incomplete_percent);

    if incomplete > 0 {
        println!(
            "\n{} {} novas need attention",
            "[warn]".yellow(),
            incomplete
        );
    } else {
        println!("\n{} All novas are complete!", "[ok]".green());
    }

    Ok(())
}

fn percentage(count: usize, total: usize) -> u32 {
    if total == 0 {
        return 0;
    }
    (count as f64 / total as f64 * 100.0) as u32
}

#[cfg(test)]
mod tests {
    use super::percentage;

    #[test]
    fn percentage_returns_zero_for_empty_total() {
        assert_eq!(percentage(5, 0), 0);
    }

    #[test]
    fn percentage_returns_integer_percent() {
        assert_eq!(percentage(3, 4), 75);
    }
}
