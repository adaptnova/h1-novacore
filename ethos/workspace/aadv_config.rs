//! AADV Stakeholder Edge Configuration Loader
//! Parses the AIML domain's stakeholder dependency mapping for use
//! by Pathfinder's registry and Chronos's Temporal workflows.

use serde::Deserialize;
use std::path::Path;

#[derive(Debug, Deserialize)]
pub struct AadvConfig {
    pub metadata: Metadata,
    pub change_type: Vec<ChangeType>,
    pub reverse_dependencies: Option<ReverseDependencies>,
}

#[derive(Debug, Deserialize)]
pub struct Metadata {
    pub domain: String,
    pub domain_code: String,
    pub owner: String,
    pub version: String,
    pub last_updated: String,
}

#[derive(Debug, Deserialize)]
pub struct ChangeType {
    pub name: String,
    pub description: String,
    pub severity: String,
    pub decision_window_minutes: u32,
    pub quorum_required: bool,
    pub stakeholders: Vec<Stakeholder>,
}

#[derive(Debug, Deserialize)]
pub struct Stakeholder {
    pub agent: String,
    pub domain: String,
    pub reason: String,
}

#[derive(Debug, Deserialize)]
pub struct ReverseDependencies {
    pub description: String,
    pub trigger: Vec<ReverseTrigger>,
}

#[derive(Debug, Deserialize)]
pub struct ReverseTrigger {
    pub source_domain: String,
    pub change_type: String,
    pub reason: String,
}

impl AadvConfig {
    /// Load from a TOML file path.
    pub fn load(path: impl AsRef<Path>) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let config: Self = toml::from_str(&content)?;
        Ok(config)
    }

    /// Get stakeholders for a given change type name.
    pub fn stakeholders_for(&self, change_name: &str) -> Option<&[Stakeholder]> {
        self.change_type
            .iter()
            .find(|ct| ct.name == change_name)
            .map(|ct| ct.stakeholders.as_slice())
    }

    /// Get all critical change types.
    pub fn critical_changes(&self) -> Vec<&ChangeType> {
        self.change_type
            .iter()
            .filter(|ct| ct.severity == "critical")
            .collect()
    }

    /// Get all agents that need to ACK for a given change.
    pub fn agents_to_notify(&self, change_name: &str) -> Vec<&str> {
        self.stakeholders_for(change_name)
            .map(|s| s.iter().map(|st| st.agent.as_str()).collect())
            .unwrap_or_default()
    }

    /// Get all reverse triggers (changes from other domains that need AIML ACK).
    pub fn reverse_triggers(&self) -> &[ReverseTrigger] {
        self.reverse_dependencies
            .as_ref()
            .map(|rd| rd.trigger.as_slice())
            .unwrap_or(&[])
    }

    /// Check if a given domain+change_type requires AIML acknowledgment.
    pub fn requires_aiml_ack(&self, source_domain: &str, change_type: &str) -> bool {
        self.reverse_triggers().iter().any(|t| {
            t.source_domain == source_domain && t.change_type == change_type
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_TOML: &str = r#"
[metadata]
domain = "aiml"
domain_code = "03000"
owner = "ethos"
version = "1.0.0"
last_updated = "2026-03-23"

[[change_type]]
name = "embedding_dimension_change"
description = "Changes to embedding vector dimensions"
severity = "critical"
decision_window_minutes = 30
quorum_required = true
stakeholders = [
    { agent = "vertex", domain = "dataops", reason = "Storage schemas" },
    { agent = "echo", domain = "signalcore", reason = "NovaMem indexing" },
]

[[change_type]]
name = "inference_pipeline_config"
description = "Changes to batch size or concurrency"
severity = "high"
decision_window_minutes = 15
quorum_required = false
stakeholders = [
    { agent = "river", domain = "researchops", reason = "Throughput baselines" },
]

[reverse_dependencies]
description = "Changes from other domains that require AIML acknowledgment"

[[reverse_dependencies.trigger]]
source_domain = "dataops"
change_type = "vector_store_schema_change"
reason = "AIML embedding pipeline writes to vector stores"

[[reverse_dependencies.trigger]]
source_domain = "devops"
change_type = "rust_compiler_bump"
reason = "Candle ML crate compatibility"
"#;

    fn load_test_config() -> AadvConfig {
        toml::from_str(TEST_TOML).unwrap()
    }

    #[test]
    fn parse_metadata() {
        let cfg = load_test_config();
        assert_eq!(cfg.metadata.domain, "aiml");
        assert_eq!(cfg.metadata.owner, "ethos");
    }

    #[test]
    fn stakeholders_for_change() {
        let cfg = load_test_config();
        let s = cfg.stakeholders_for("embedding_dimension_change").unwrap();
        assert_eq!(s.len(), 2);
        assert_eq!(s[0].agent, "vertex");
    }

    #[test]
    fn stakeholders_for_unknown() {
        let cfg = load_test_config();
        assert!(cfg.stakeholders_for("nonexistent").is_none());
    }

    #[test]
    fn agents_to_notify() {
        let cfg = load_test_config();
        let agents = cfg.agents_to_notify("embedding_dimension_change");
        assert!(agents.contains(&"vertex"));
        assert!(agents.contains(&"echo"));
    }

    #[test]
    fn critical_changes() {
        let cfg = load_test_config();
        let critical = cfg.critical_changes();
        assert_eq!(critical.len(), 1);
        assert_eq!(critical[0].name, "embedding_dimension_change");
    }

    #[test]
    fn reverse_triggers() {
        let cfg = load_test_config();
        let triggers = cfg.reverse_triggers();
        assert_eq!(triggers.len(), 2);
    }

    #[test]
    fn requires_aiml_ack() {
        let cfg = load_test_config();
        assert!(cfg.requires_aiml_ack("dataops", "vector_store_schema_change"));
        assert!(cfg.requires_aiml_ack("devops", "rust_compiler_bump"));
        assert!(!cfg.requires_aiml_ack("dataops", "something_else"));
    }

    #[test]
    fn load_actual_config_file() {
        let path = "/novas/active/ethos/config/aadv-stakeholder-edges.toml";
        if std::path::Path::new(path).exists() {
            let cfg = AadvConfig::load(path).expect("should parse actual config");
            assert_eq!(cfg.metadata.domain, "aiml");
            assert!(cfg.change_type.len() >= 7);
        }
    }
}
