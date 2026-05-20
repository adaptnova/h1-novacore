//! Typed NATS adapter primitives for Hermes-backed Nova agents.

use std::time::Duration;

use async_nats::{Client, ConnectOptions, Subscriber};
use bytes::Bytes;
use chrono::{DateTime, Utc};
use futures_util::StreamExt;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use uuid::Uuid;

/// Result alias for adapter operations.
pub type Result<T> = std::result::Result<T, AdapterError>;

/// Configuration for connecting one nova to NATS.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AdapterConfig {
    url: String,
    user: Option<String>,
    password: Option<String>,
    agent_name: String,
    subject_prefix: String,
    request_timeout: Duration,
}

impl AdapterConfig {
    /// Create a new adapter configuration.
    ///
    /// Parameters:
    /// - `url`: NATS connection URL.
    /// - `agent_name`: Nova profile name used for subject derivation.
    ///
    /// Returns a config with `nova` as the subject prefix and a 30 second
    /// request timeout.
    pub fn new(url: impl Into<String>, agent_name: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            user: None,
            password: None,
            agent_name: normalize_agent_name(&agent_name.into()),
            subject_prefix: "nova".to_string(),
            request_timeout: Duration::from_secs(30),
        }
    }

    /// Set NATS username/password authentication.
    pub fn with_auth(mut self, user: impl Into<String>, password: impl Into<String>) -> Self {
        self.user = Some(user.into());
        self.password = Some(password.into());
        self
    }

    /// Set the subject namespace prefix.
    pub fn with_subject_prefix(mut self, subject_prefix: impl Into<String>) -> Self {
        self.subject_prefix = subject_prefix.into();
        self
    }

    /// Set the request/reply timeout.
    pub fn with_request_timeout(mut self, request_timeout: Duration) -> Self {
        self.request_timeout = request_timeout;
        self
    }

    /// Return the direct subject for this nova.
    pub fn direct_subject(&self) -> String {
        format!("{}.{}.direct", self.subject_prefix, self.agent_name)
    }

    /// Return the meet subject for this nova.
    pub fn meet_subject(&self) -> String {
        format!("{}.{}.meet", self.subject_prefix, self.agent_name)
    }

    /// Return the ping subject for this nova.
    pub fn ping_subject(&self) -> String {
        format!("{}.{}.ping", self.subject_prefix, self.agent_name)
    }

    /// Return the logs subject for this nova.
    pub fn logs_subject(&self) -> String {
        format!("{}.logs.{}", self.subject_prefix, self.agent_name)
    }
}

/// Message envelope used by Nova fleet NATS routes.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct NovaEnvelope {
    /// Stable event identifier.
    pub id: String,
    /// Sender identity.
    pub from: String,
    /// Optional target identity.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub to: Option<String>,
    /// Human or agent message content.
    pub message: String,
    /// Optional reply inbox subject.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub reply_to: Option<String>,
    /// Creation timestamp.
    pub timestamp: DateTime<Utc>,
}

impl NovaEnvelope {
    /// Create a direct-message envelope with a generated ID.
    pub fn direct(from: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            id: format!("nova-{}", Uuid::new_v4().simple()),
            from: from.into(),
            to: None,
            message: message.into(),
            reply_to: None,
            timestamp: Utc::now(),
        }
    }

    /// Attach a target identity.
    pub fn with_target(mut self, target: impl Into<String>) -> Self {
        self.to = Some(target.into());
        self
    }

    /// Attach a reply inbox subject.
    pub fn with_reply_to(mut self, reply_to: impl Into<String>) -> Self {
        self.reply_to = Some(reply_to.into());
        self
    }
}

/// Typed wrapper around an async NATS client.
#[derive(Clone)]
pub struct NatsAdapter {
    client: Client,
    config: AdapterConfig,
}

impl NatsAdapter {
    /// Connect to NATS with the provided config.
    ///
    /// Errors if the server is unavailable or authentication fails.
    pub async fn connect(config: AdapterConfig) -> Result<Self> {
        let client = match (&config.user, &config.password) {
            (Some(user), Some(password)) => {
                ConnectOptions::with_user_and_password(user.clone(), password.clone())
                    .connect(config.url.as_str())
                    .await
                    .map_err(AdapterError::from_display)?
            }
            _ => async_nats::connect(config.url.as_str())
                .await
                .map_err(AdapterError::from_display)?,
        };
        Ok(Self { client, config })
    }

    /// Return this adapter's config.
    pub fn config(&self) -> &AdapterConfig {
        &self.config
    }

    /// Subscribe to a subject.
    pub async fn subscribe(&self, subject: impl Into<String>) -> Result<Subscriber> {
        self.client
            .subscribe(subject.into())
            .await
            .map_err(AdapterError::from_display)
    }

    /// Publish a typed envelope to a subject.
    pub async fn publish_envelope(
        &self,
        subject: impl Into<String>,
        envelope: &NovaEnvelope,
    ) -> Result<()> {
        let payload = serde_json::to_vec(envelope)?;
        self.client
            .publish(subject.into(), Bytes::from(payload))
            .await
            .map_err(AdapterError::from_display)?;
        self.client
            .flush()
            .await
            .map_err(AdapterError::from_display)?;
        Ok(())
    }

    /// Publish text bytes to a subject.
    pub async fn publish_text(
        &self,
        subject: impl Into<String>,
        message: impl Into<String>,
    ) -> Result<()> {
        self.client
            .publish(subject.into(), Bytes::from(message.into()))
            .await
            .map_err(AdapterError::from_display)?;
        self.client
            .flush()
            .await
            .map_err(AdapterError::from_display)?;
        Ok(())
    }

    /// Send a request and deserialize the JSON response.
    pub async fn request_json<T>(
        &self,
        subject: impl Into<String>,
        envelope: &NovaEnvelope,
    ) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let payload = serde_json::to_vec(envelope)?;
        let response = tokio::time::timeout(
            self.config.request_timeout,
            self.client.request(subject.into(), Bytes::from(payload)),
        )
        .await
        .map_err(|_| AdapterError::Timeout(self.config.request_timeout))?
        .map_err(AdapterError::from_display)?;
        Ok(serde_json::from_slice(&response.payload)?)
    }

    /// Read the next JSON envelope from a subscriber.
    pub async fn next_envelope(subscriber: &mut Subscriber) -> Result<Option<NovaEnvelope>> {
        let Some(message) = subscriber.next().await else {
            return Ok(None);
        };
        Ok(Some(serde_json::from_slice(&message.payload)?))
    }
}

/// Adapter error variants.
#[derive(Debug, Error)]
pub enum AdapterError {
    /// NATS client error.
    #[error("nats error: {0}")]
    Nats(String),
    /// JSON serialization/deserialization error.
    #[error("json error: {0}")]
    Json(#[from] serde_json::Error),
    /// Request timed out.
    #[error("request timed out after {0:?}")]
    Timeout(Duration),
}

impl AdapterError {
    fn from_display(error: impl std::fmt::Display) -> Self {
        Self::Nats(error.to_string())
    }
}

fn normalize_agent_name(agent_name: &str) -> String {
    agent_name.trim().to_ascii_lowercase().replace('_', "-")
}

#[cfg(test)]
mod tests {
    use super::{normalize_agent_name, AdapterConfig, NovaEnvelope};

    #[test]
    fn config_derives_standard_subjects() {
        let config = AdapterConfig::new("nats://localhost:18020", "PEA_Test");
        assert_eq!(config.direct_subject(), "nova.pea-test.direct");
        assert_eq!(config.meet_subject(), "nova.pea-test.meet");
        assert_eq!(config.ping_subject(), "nova.pea-test.ping");
        assert_eq!(config.logs_subject(), "nova.logs.pea-test");
    }

    #[test]
    fn envelope_serializes_with_required_fields() {
        let envelope = NovaEnvelope::direct("latch", "hello").with_target("echo");
        let json = serde_json::to_value(&envelope).expect("envelope should serialize");
        assert_eq!(json["from"], "latch");
        assert_eq!(json["to"], "echo");
        assert_eq!(json["message"], "hello");
    }

    #[test]
    fn agent_name_normalization_is_stable() {
        assert_eq!(normalize_agent_name("  PEA_Test  "), "pea-test");
    }
}
