//! Harness-neutral, explicit memory operations. Retrieved text is reference data.
use anyhow::{Context, Result, bail, ensure};
use clap::Parser;
use reqwest::blocking::Client;
use serde::Deserialize;
use serde_json::{Value, json};
use std::{
    fs::{self, OpenOptions},
    io::{self, Read, Write},
    os::unix::fs::{DirBuilderExt, OpenOptionsExt},
    path::PathBuf,
    process::{Command, ExitCode, Stdio},
    time::Duration,
};

const TOPIC: &str = "memfab.memory.events.v1";
const SCHEMA: &str = "memfab.bridge.v1";

#[derive(Parser)]
#[command(
    version,
    about = "Read one JSON memory request from stdin; emit one JSON response"
)]
struct Config {
    #[arg(long)]
    seat: String,
    #[arg(long, default_value = "http://127.0.0.1:6333")]
    qdrant: String,
    #[arg(long, default_value = "127.0.0.1:18021")]
    brokers: String,
    /// Local retry journal. Keep persistent and reuse across harnesses.
    #[arg(long, default_value_os_t = default_state_dir())]
    state_dir: PathBuf,
}

fn default_state_dir() -> PathBuf {
    if let Some(base) = std::env::var_os("XDG_STATE_HOME") {
        PathBuf::from(base).join("memfab-bridge")
    } else if let Some(base) = std::env::var_os("HOME") {
        PathBuf::from(base).join(".local/state/memfab-bridge")
    } else {
        PathBuf::from(".memfab-bridge-state")
    }
}

#[derive(Debug, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Request {
    Status {},
    Recall {
        query: String,
        #[serde(default = "default_limit")]
        limit: usize,
    },
    Get {
        event_id: String,
    },
    Read {
        event_id: String,
        partition: i32,
        offset: i64,
    },
    Remember {
        id: String,
        text: String,
        source: String,
    },
}

fn default_limit() -> usize {
    5
}

fn identifier(value: &str) -> Result<()> {
    ensure!(
        !value.is_empty()
            && value.len() <= 100
            && value
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_'),
        "invalid identifier: use 1-100 ASCII letters, digits, hyphens or underscores"
    );
    Ok(())
}

fn validate(request: &Request) -> Result<()> {
    match request {
        Request::Recall { query, limit } => {
            ensure!(
                !query.trim().is_empty() && query.len() <= 400,
                "query must contain 1-400 bytes"
            );
            ensure!((1..=20).contains(limit), "limit must be 1-20");
        }
        Request::Remember { id, text, source } => {
            identifier(id)?;
            ensure!(
                !text.trim().is_empty() && text.len() <= 4096,
                "text must contain 1-4096 bytes"
            );
            ensure!(
                !source.trim().is_empty() && source.len() <= 300,
                "source must contain 1-300 bytes"
            );
        }
        Request::Get { event_id } | Request::Read { event_id, .. } => {
            ensure!(
                !event_id.is_empty() && event_id.len() <= 512,
                "invalid event_id"
            );
        }
        Request::Status {} => {}
    }
    if let Request::Read {
        partition, offset, ..
    } = request
    {
        ensure!(
            *partition >= 0 && *offset >= 0,
            "partition and offset must be nonnegative"
        );
    }
    Ok(())
}

struct Bridge {
    config: Config,
    http: Client,
}

impl Bridge {
    fn new(config: Config) -> Result<Self> {
        identifier(&config.seat)?;
        let url = reqwest::Url::parse(&config.qdrant).context("invalid Qdrant URL")?;
        ensure!(
            url.scheme() == "http"
                && matches!(url.host_str(), Some("127.0.0.1" | "localhost" | "[::1]")),
            "v1 requires loopback HTTP Qdrant; use a local tunnel for remote access"
        );
        ensure!(
            url.username().is_empty() && url.password().is_none(),
            "credentials in URLs are forbidden"
        );
        ensure!(
            config.brokers.starts_with("127.0.0.1:") && config.brokers[10..].parse::<u16>().is_ok(),
            "v1 requires a loopback Redpanda broker"
        );
        let http = Client::builder()
            .timeout(Duration::from_secs(10))
            .no_proxy()
            .redirect(reqwest::redirect::Policy::none())
            .build()?;
        Ok(Self { config, http })
    }

    fn qdrant(&self, path: &str, body: Option<&Value>) -> Result<Value> {
        let url = format!(
            "{}/collections/memfab_memory{}",
            self.config.qdrant.trim_end_matches('/'),
            path
        );
        let request = match body {
            Some(b) => self.http.post(url).json(b),
            None => self.http.get(url),
        };
        let response = request
            .send()
            .map_err(|_| anyhow::anyhow!("Qdrant transport failed"))?;
        ensure!(
            response.status().is_success(),
            "Qdrant HTTP {}",
            response.status().as_u16()
        );
        let mut bytes = Vec::new();
        response.take(2_000_001).read_to_end(&mut bytes)?;
        ensure!(
            bytes.len() <= 2_000_000,
            "Qdrant response exceeds 2 MB bound"
        );
        let value: Value = serde_json::from_slice(&bytes).context("invalid Qdrant response")?;
        ensure!(value["status"] == "ok", "Qdrant reported failure");
        Ok(value)
    }

    fn scroll(&self, event: Option<&str>, offset: Option<Value>) -> Result<Value> {
        let mut must = vec![json!({"key":"agent_id","match":{"value":self.config.seat}})];
        if let Some(id) = event {
            must.push(json!({"key":"event_id","match":{"value":id}}));
        }
        self.qdrant("/points/scroll", Some(&json!({"filter":{"must":must},"limit":20,"offset":offset,"with_payload":true,"with_vector":false})))
    }

    fn recall(&self, query: &str, limit: usize) -> Result<Value> {
        let mut cursor = None;
        let mut hits = Vec::new();
        let mut scanned = 0;
        let needle = query.to_lowercase();
        // Bound per-call work. This is literal recall, not a ranked semantic search.
        for _ in 0..50 {
            let page = self.scroll(None, cursor)?;
            let points = page["result"]["points"]
                .as_array()
                .context("missing Qdrant points")?;
            for point in points {
                let p = &point["payload"];
                ensure!(
                    p["agent_id"] == self.config.seat,
                    "backend returned a foreign seat"
                );
                scanned += 1;
                let content = p["content"].as_str().unwrap_or_default();
                if content.to_lowercase().contains(&needle) {
                    hits.push(reference(p));
                }
            }
            cursor = page["result"]["next_page_offset"].as_null().map_or_else(
                || Some(page["result"]["next_page_offset"].clone()),
                |_| None,
            );
            if cursor.is_none() || hits.len() >= limit {
                break;
            }
        }
        hits.truncate(limit);
        Ok(
            json!({"backend":"qdrant","mode":"literal_substring","hits":hits,"scanned":scanned,"exhaustive":cursor.is_none(),"scan_limit":1000}),
        )
    }

    fn get(&self, event_id: &str) -> Result<Value> {
        let page = self.scroll(Some(event_id), None)?;
        let points = page["result"]["points"]
            .as_array()
            .context("missing Qdrant points")?;
        let Some(point) = points.first() else {
            return Ok(json!({"found":false,"indexed":false,"event_id":event_id}));
        };
        let p = &point["payload"];
        ensure!(
            p["agent_id"] == self.config.seat && p["event_id"] == event_id,
            "backend returned a foreign event"
        );
        Ok(json!({"found":true,"indexed":true,"memory":reference(p)}))
    }

    fn read(&self, event_id: &str, partition: i32, offset: i64) -> Result<Value> {
        let raw = command(
            "rpk",
            &[
                "topic",
                "consume",
                TOPIC,
                "--brokers",
                &self.config.brokers,
                "--partitions",
                &partition.to_string(),
                "--offset",
                &offset.to_string(),
                "--num",
                "1",
                "--format",
                "json",
            ],
            None,
        )?;
        let record: Value = serde_json::from_slice(&raw).context("invalid Redpanda record")?;
        ensure!(
            record["offset"] == offset && record["partition"] == partition,
            "Redpanda returned a different location"
        );
        let envelope: Value = match record["value"].as_str() {
            Some(text) => serde_json::from_str(text).context("invalid L9 envelope")?,
            None => record["value"].clone(),
        };
        let payload = checked_payload(&envelope, &self.config.seat, event_id)?;
        Ok(
            json!({"verified":true,"event_id":event_id,"topic":TOPIC,"partition":partition,"offset":offset,"payload":payload}),
        )
    }

    fn remember(&self, id: &str, text: &str, source: &str) -> Result<Value> {
        let dir = self.config.state_dir.join(&self.config.seat);
        fs::DirBuilder::new()
            .recursive(true)
            .mode(0o700)
            .create(&dir)?;
        let path = dir.join(format!("{id}.json"));
        let intent_hash = blake3::hash(&serde_json::to_vec(
            &json!({"seat":self.config.seat,"text":text,"source":source}),
        )?)
        .to_hex()
        .to_string();
        let mut journal = match OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&path)
        {
            Ok(f) => f,
            Err(e) if e.kind() == io::ErrorKind::AlreadyExists => {
                let existing: Value = serde_json::from_slice(&fs::read(&path)?)
                    .context("retry journal incomplete; inspect before retrying")?;
                ensure!(
                    existing["intent_hash"] == intent_hash,
                    "request id already used for different content"
                );
                if existing["receipt"].is_object() {
                    let r = &existing["receipt"];
                    let verified = self.read(
                        r["event_id"].as_str().context("receipt event id")?,
                        r["partition"].as_i64().context("receipt partition")? as i32,
                        r["offset"].as_i64().context("receipt offset")?,
                    )?;
                    return Ok(json!({"deduplicated":true,"receipt":r,"read_back":verified}));
                }
                bail!(
                    "prior write outcome unknown; inspect journal and query its event_id; automatic re-publish refused"
                );
            }
            Err(e) => return Err(e.into()),
        };
        let event_id = format!("bridge-{}-{id}", self.config.seat);
        let envelope = envelope(&self.config.seat, &event_id, text, source)?;
        let pending = json!({"intent_hash":intent_hash,"event_id":event_id,"state":"pending","envelope":envelope});
        journal.write_all(&serde_json::to_vec(&pending)?)?;
        journal.sync_all()?;
        fs::File::open(&dir)?.sync_all()?;
        let raw = command(
            "rpk",
            &[
                "topic",
                "produce",
                TOPIC,
                "--brokers",
                &self.config.brokers,
                "--compression",
                "none",
                "-k",
                &self.config.seat,
            ],
            Some(&serde_json::to_vec(&envelope)?),
        )?;
        let (partition, offset) = parse_ack(&String::from_utf8(raw)?)?;
        let receipt = json!({"event_id":event_id,"topic":TOPIC,"partition":partition,"offset":offset,"declared_payload_hash":envelope["declared_payload_hash"]});
        let completed = json!({"intent_hash":intent_hash,"event_id":event_id,"state":"produced","receipt":receipt});
        let temp = dir.join(format!("{id}.receipt.tmp"));
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&temp)?;
        file.write_all(&serde_json::to_vec(&completed)?)?;
        file.sync_all()?;
        fs::rename(&temp, &path)?;
        fs::File::open(&dir)?.sync_all()?;
        let verified = self.read(&event_id, partition, offset)?;
        ensure!(
            verified["payload"]["text"] == text,
            "read-back text mismatch"
        );
        Ok(
            json!({"deduplicated":false,"receipt":receipt,"read_back":verified,"projection":"pending; use get to verify indexing"}),
        )
    }

    fn execute(&self, request: Request) -> Result<Value> {
        validate(&request)?;
        match request {
            Request::Status {} => {
                let qdrant = self.qdrant("", None)?;
                let page = self.scroll(None, None)?;
                Ok(
                    json!({"qdrant_reachable":true,"collection_points":qdrant["result"]["points_count"],"seat_has_indexed_memory":!page["result"]["points"].as_array().context("missing points")?.is_empty(),"automatic_ingestion":false,"automatic_prompt_injection":false}),
                )
            }
            Request::Recall { query, limit } => self.recall(&query, limit),
            Request::Get { event_id } => self.get(&event_id),
            Request::Read {
                event_id,
                partition,
                offset,
            } => self.read(&event_id, partition, offset),
            Request::Remember { id, text, source } => self.remember(&id, &text, &source),
        }
    }
}

fn reference(p: &Value) -> Value {
    json!({"event_id":p["event_id"],"agent_id":p["agent_id"],"text":p["content"].as_str().unwrap_or_default().chars().take(1200).collect::<String>(),"text_truncated":p["content"].as_str().is_some_and(|s| s.chars().count()>1200),"topic":p["redpanda_topic"],"partition":p["redpanda_partition"],"offset":p["redpanda_offset"],"created_at":p["created_at"]})
}

fn envelope(seat: &str, event_id: &str, text: &str, source: &str) -> Result<Value> {
    let now = chrono::Utc::now();
    let payload = serde_json::to_vec(
        &json!({"schema":"memfab.bridge.note.v1","agent_id":seat,"text":text,"excerpt":text,"kind":"episodic","source":source,"reference_only":true}),
    )?;
    Ok(
        json!({"schema":"memfab.ingest.raw_input.v1","event_id":event_id,"agent_id":seat,"sequence":now.timestamp_millis(),"event_type":"memory.fact.observed","trace_id":format!("trace-{event_id}"),"media_type":"application/json","source_authority":"edge_outbox","proposed_valid_from":now.to_rfc3339(),"proposed_valid_to":null,"assertion_time":now.to_rfc3339(),"declared_payload_hash":blake3::hash(&payload).to_hex().to_string(),"payload":payload}),
    )
}

fn checked_payload(envelope: &Value, seat: &str, event_id: &str) -> Result<Value> {
    ensure!(
        envelope["agent_id"] == seat && envelope["event_id"] == event_id,
        "event does not belong to requested seat/id"
    );
    let payload = &envelope["payload"];
    let bytes = if payload.is_object() {
        serde_json::to_vec(payload)?
    } else {
        serde_json::from_value::<Vec<u8>>(payload.clone()).context("invalid payload bytes")?
    };
    let expected = envelope["declared_payload_hash"]
        .as_str()
        .or_else(|| envelope["payload_hash"].as_str())
        .context("payload hash missing")?;
    ensure!(
        blake3::hash(&bytes).to_hex().as_str() == expected,
        "payload hash mismatch"
    );
    ensure!(bytes.len() <= 64 * 1024, "payload exceeds 64 KB read bound");
    serde_json::from_slice(&bytes).context("payload is not JSON")
}

fn parse_ack(raw: &str) -> Result<(i32, i64)> {
    let words: Vec<_> = raw.split_whitespace().collect();
    for w in words.windows(7) {
        if w[0..3] == ["Produced", "to", "partition"] && w[4..6] == ["at", "offset"] {
            let p: i32 = w[3].parse()?;
            let o: i64 = w[6].parse()?;
            ensure!(p >= 0 && o >= 0, "negative receipt location");
            return Ok((p, o));
        }
    }
    bail!("produce acknowledgement missing; write outcome unknown")
}

fn command(program: &str, args: &[&str], input: Option<&[u8]>) -> Result<Vec<u8>> {
    // GNU timeout owns the process group, including children. No shell interpolation.
    let mut child = Command::new("timeout")
        .args(["--signal=TERM", "--kill-after=2s", "20s", program])
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .context("cannot start backend command")?;
    if let Some(mut stdin) = child.stdin.take()
        && let Some(bytes) = input
    {
        stdin.write_all(bytes)?;
        stdin.write_all(b"\n")?;
    }
    let mut output = Vec::new();
    child
        .stdout
        .take()
        .context("backend stdout missing")?
        .take(2_000_001)
        .read_to_end(&mut output)?;
    let status = child.wait()?;
    ensure!(
        status.success(),
        "backend command failed or timed out; a write may have committed, inspect its journal"
    );
    ensure!(output.len() <= 2_000_000, "backend output exceeds 2 MB");
    Ok(output)
}

fn run(config: Config) -> Result<Value> {
    let bridge = Bridge::new(config)?;
    let mut input = Vec::new();
    io::stdin().take(16_385).read_to_end(&mut input)?;
    ensure!(input.len() <= 16_384, "request exceeds 16 KB");
    let request: Request = serde_json::from_slice(&input)
        .map_err(|_| anyhow::anyhow!("invalid request JSON or unknown fields"))?;
    let result = bridge.execute(request)?;
    Ok(
        json!({"schema":SCHEMA,"ok":true,"seat":bridge.config.seat,"reference_only":true,"result":result}),
    )
}

fn main() -> ExitCode {
    let result = run(Config::parse());
    let (value, code) = match result {
        Ok(v) => (v, ExitCode::SUCCESS),
        Err(e) => (
            json!({"schema":SCHEMA,"ok":false,"error":e.to_string()}),
            ExitCode::FAILURE,
        ),
    };
    match serde_json::to_writer(io::stdout().lock(), &value) {
        Ok(()) => {
            println!();
            code
        }
        Err(_) => ExitCode::FAILURE,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn traversal_and_shell_seats_rejected() {
        for bad in ["", "../iris", "$(id)", "ethos/iris", "ethos\n"] {
            assert!(identifier(bad).is_err());
        }
        assert!(identifier("ethos").is_ok());
    }
    #[test]
    fn protocol_rejects_extra_authority_and_oversized_writes() {
        assert!(serde_json::from_str::<Request>(r#"{"op":"status","seat":"iris"}"#).is_err());
        assert!(
            validate(&Request::Remember {
                id: "x".into(),
                text: "x".repeat(4097),
                source: "test".into()
            })
            .is_err()
        );
        assert!(
            validate(&Request::Read {
                event_id: "x".into(),
                partition: 0,
                offset: -1
            })
            .is_err()
        );
    }
    #[test]
    fn round_trip_preserves_text_and_detects_corruption_and_foreign_seat() -> Result<()> {
        let text = "literal $(touch /tmp/never) `id`\nUnicode: λ";
        let mut e = envelope("ethos", "bridge-test", text, "test")?;
        assert_eq!(checked_payload(&e, "ethos", "bridge-test")?["text"], text);
        assert!(checked_payload(&e, "iris", "bridge-test").is_err());
        assert!(checked_payload(&e, "ethos", "other").is_err());
        e["payload"][0] = json!(0);
        assert!(checked_payload(&e, "ethos", "bridge-test").is_err());
        Ok(())
    }
    #[test]
    fn ack_requires_partition_and_offset() -> Result<()> {
        assert_eq!(
            parse_ack("Produced to partition 0 at offset 42 with timestamp 99")?,
            (0, 42)
        );
        assert!(parse_ack("ACK").is_err());
        assert!(parse_ack("Produced to partition -1 at offset 42").is_err());
        Ok(())
    }
}
