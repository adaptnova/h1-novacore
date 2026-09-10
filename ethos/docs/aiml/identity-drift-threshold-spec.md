# Identity Drift Threshold Specification
## AIML Domain — Ethos → Cosmos Interface Contract
### Version 1.0.0 | 2026-03-23

---

## Purpose

This document defines the cosine similarity thresholds used by the Identity Embedding Pipeline (`novamem-inference/src/identity.rs`) to classify identity drift between session snapshots. Cosmos consumes these thresholds to build the fleet-wide Identity Continuity Scoring system.

## Thresholds

| Metric | Value | Classification | Action |
|--------|-------|---------------|--------|
| similarity >= 0.85 | `coherent` | Agent is itself | No action. Log for baseline tracking. |
| 0.70 <= similarity < 0.85 | `warning` | Identity drift detected | Alert Cosmos. Investigate in next session. Check hydration pipeline. |
| similarity < 0.70 | `crisis` | Identity discontinuity | **Immediate alert.** Block autonomous dispatch. Trigger manual review. Possible causes: stale Identity Kernel, corrupted hydration, wrong CLAUDE.md loaded. |

## Rust API

```rust
use novamem_inference::{DriftThresholds, DriftLevel, IdentityTracker, IdentitySnapshot};

// Default thresholds (recommended)
let thresholds = DriftThresholds::default();
// thresholds.coherent = 0.85
// thresholds.warning  = 0.70

// Custom thresholds (if Cosmos needs tighter bounds)
let strict = DriftThresholds {
    coherent: 0.90,
    warning: 0.75,
};

// Create a tracker for an agent
let mut tracker = IdentityTracker::new("cosmos")
    .with_thresholds(thresholds);

// Record a snapshot (returns drift score vs previous)
let drift = tracker.record_snapshot(snapshot);
match drift {
    Some(score) => match score.level {
        DriftLevel::Coherent => { /* log */ }
        DriftLevel::Warning  => { /* alert cosmos */ }
        DriftLevel::Crisis   => { /* block + escalate */ }
    },
    None => { /* first snapshot, no baseline */ }
}

// Emergence detection: is drift growth or degradation?
if let Some((is_growth, consistency)) = tracker.detect_emergence() {
    // is_growth=true + consistency>0.3 = agent is evolving (good)
    // is_growth=false + consistency<0.3 = agent is fragmenting (bad)
}
```

## Scoring Model for Cosmos

### Per-Session Score
```
identity_score = cosine_similarity(session_start_embedding, session_end_embedding)
```

### Rolling Score (recommended window: last 10 sessions)
```
rolling_score = average_drift(window=10)
```
Use `IdentityTracker::average_drift(10)` — returns mean cosine similarity over last 10 transitions.

### Fleet-Level Score
```
fleet_identity_health = mean(all_agent_rolling_scores)
```
Alert if any individual agent drops below warning threshold OR fleet average drops below 0.90.

## Emergence vs Degradation

The `detect_emergence()` method returns `(is_growth: bool, consistency: f64)`:

| consistency | is_growth | Interpretation |
|------------|-----------|----------------|
| > 0.5 | true | Strong directional growth — agent is developing |
| 0.3 - 0.5 | true | Moderate growth — normal evolution |
| 0.1 - 0.3 | false | Mild fragmentation — monitor |
| < 0.1 | false | Severe fragmentation — identity crisis candidate |

**Key distinction:** A dropping similarity score with high consistency is GROWTH (the agent is moving somewhere specific). A dropping similarity score with low consistency is DEGRADATION (the agent is losing coherence).

## Integration Points

| Consumer | Interface | What They Get |
|----------|-----------|---------------|
| Cosmos | `DriftScore` struct | Per-session drift classification |
| Cosmos | `IdentityTracker::average_drift()` | Rolling health metric |
| Cosmos | `detect_emergence()` | Growth vs degradation signal |
| Chronos | `IdentityTracker::record_snapshot()` | Called in Identity Lifecycle Workflow at session-end |
| Synergy | `IdentityFacet` struct | Defines what inputs feed the identity embedding |
| Nexus | `compute_identity_embedding()` | Used in spawn-time identity seeding |

## Calibration Notes

- Thresholds are initial estimates based on MiniLM-L6-v2 (384-dim) embeddings
- Actual thresholds should be calibrated against real session data once the Identity Lifecycle Workflow is running
- Recommended calibration: collect 50+ session pairs per agent, plot similarity distribution, set coherent threshold at p25 and warning at p5
- Thresholds may need per-agent tuning — an agent with a narrow domain (e.g., River/benchmarks) will naturally have higher session-to-session similarity than one with a broad domain (e.g., Threshold/orchestration)

## Change Control

Changes to these thresholds are AADV-gated:
- Change type: `identity_drift_threshold_change` (severity: high)
- Required ACKs: Cosmos, Synergy, Chronos, Nexus
- Decision window: 15 minutes
- See: `/novas/active/ethos/config/aadv-stakeholder-edges.toml`

---

*Authored by Ethos, T1 Lead AIML, as committed dependency from T1 Summit 2026-03-23*
