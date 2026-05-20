use std::env;
use std::time::Duration;

use async_nats::Message;
use futures_util::StreamExt;
use hermes_nats_adapter::{AdapterConfig, NatsAdapter, NovaEnvelope};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct ProofReply {
    id: String,
    status: String,
    route: String,
    subject: String,
    log_subject: String,
}

#[tokio::main]
async fn main() -> hermes_nats_adapter::Result<()> {
    let raw_url = env::var("NATS_URL").unwrap_or_else(|_| "nats://localhost:18020".to_string());
    let url = if raw_url.contains("://") {
        raw_url
    } else {
        format!("nats://{raw_url}")
    };
    let subject = env::var("NOVA_NATS_PROOF_SUBJECT")
        .unwrap_or_else(|_| "nova.adapter-proof.direct".to_string());
    let log_subject = env::var("NOVA_NATS_PROOF_LOG_SUBJECT")
        .unwrap_or_else(|_| "nova.logs.adapter-proof".to_string());

    let mut config = AdapterConfig::new(url, "adapter-proof")
        .with_subject_prefix("nova")
        .with_request_timeout(Duration::from_secs(10));

    if let (Ok(user), Ok(password)) = (env::var("NATS_USER"), env::var("NATS_PASSWORD")) {
        config = config.with_auth(user, password);
    }

    let adapter = NatsAdapter::connect(config).await?;
    let responder = adapter.clone();
    let mut subscriber = adapter.subscribe(subject.clone()).await?;
    let log_subject_for_task = log_subject.clone();

    let responder_task = tokio::spawn(async move {
        if let Some(message) = subscriber.next().await {
            respond_to_proof(message, &responder, &log_subject_for_task).await?;
        }
        hermes_nats_adapter::Result::Ok(())
    });

    let envelope = NovaEnvelope::direct("latch", "isolated adapter promotion proof")
        .with_target("adapter-proof")
        .with_reply_to("nats-request-reply");
    let reply: ProofReply = adapter.request_json(subject.clone(), &envelope).await?;

    responder_task
        .await
        .map_err(|error| hermes_nats_adapter::AdapterError::Nats(error.to_string()))??;

    println!(
        "proof id={} status={} route={} subject={} log_subject={}",
        reply.id, reply.status, reply.route, reply.subject, reply.log_subject
    );

    Ok(())
}

async fn respond_to_proof(
    message: Message,
    adapter: &NatsAdapter,
    log_subject: &str,
) -> hermes_nats_adapter::Result<()> {
    let envelope: NovaEnvelope = serde_json::from_slice(&message.payload)?;
    let subject = message.subject.to_string();

    let log = NovaEnvelope::direct("adapter-proof", format!("received {}", envelope.id))
        .with_target("latch");
    adapter
        .publish_envelope(log_subject.to_string(), &log)
        .await?;

    let reply = ProofReply {
        id: envelope.id,
        status: "ok".to_string(),
        route: "isolated-adapter-proof".to_string(),
        subject,
        log_subject: log_subject.to_string(),
    };

    let Some(reply_subject) = message.reply else {
        return Err(hermes_nats_adapter::AdapterError::Nats(
            "proof request did not include a reply subject".to_string(),
        ));
    };
    let payload = serde_json::to_string(&reply)?;
    adapter
        .publish_text(reply_subject.to_string(), payload)
        .await?;

    Ok(())
}
