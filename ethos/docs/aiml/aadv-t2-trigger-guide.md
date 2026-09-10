# AADV Trigger Guide for AIML T2 Fleet
## Gradient, Axiom, Catalyst, Lumen, Tensor

---

## Purpose

T2 agents in the AIML domain must follow AADV (Announce → Acknowledge → Decide → Verify) for any change that crosses domain boundaries. This guide defines what triggers AADV for each T2 role.

## When AADV is Required

**Rule: Any change that affects agents outside your immediate scope requires AADV.**

### Gradient (Numerical Precision & Quantization)
| Change | Severity | Notify |
|--------|----------|--------|
| Quantization format change (FP8/BF16/INT8) | Critical | Ethos, Forge, River |
| Error tolerance threshold adjustment | High | Ethos, River |
| Parity harness test criteria change | Medium | Ethos |

### Axiom (Model Routing & Provider Integration)
| Change | Severity | Notify |
|--------|----------|--------|
| New model provider added | Critical | Ethos, Oracle, Forge |
| Routing policy change (cost/latency weights) | High | Oracle, Ethos |
| Model cost data update | High | Oracle |
| DragonFlyFlusher key schema change | High | Vertex, Cosmos |

### Catalyst (WASM64 Pipeline & BlitzKernels Delivery)
| Change | Severity | Notify |
|--------|----------|--------|
| WASM target change | Critical | Forge, Ethos |
| Kernel API signature change | Critical | Forge, Herald, Oracle |
| Build pipeline config change | High | Forge |
| Performance SLA threshold change | High | River, Ethos |

### Lumen (Cognitive Pipeline & cc-faculty)
| Change | Severity | Notify |
|--------|----------|--------|
| Cognitive pipeline stage add/remove | Critical | Ethos, Echo |
| Digenetics data schema change | High | Vertex, Nexus |
| Cortex health endpoint contract change | High | Cosmos, Pathfinder |

### Tensor (ML Model Evaluation)
| Change | Severity | Notify |
|--------|----------|--------|
| Benchmark suite methodology change | Critical | River, Ethos |
| Evaluation metric definition change | High | Ethos, Oracle |
| Baseline threshold update | High | River, Cosmos |

## How to Trigger AADV

1. **Announce**: Publish to `novacol.aadv.announce.aiml` via NATS:
   ```json
   {
     "agent_id": "gradient",
     "change_type": "quantization_format_change",
     "description": "Switching flash-attention from FP16 to FP8",
     "severity": "critical",
     "affected_agents": ["ethos", "forge", "river"]
   }
   ```

2. **Wait for ACK** from all affected agents (decision window per severity: critical=30min, high=15min, medium=10min)

3. **Proceed or block** based on quorum

4. **Verify** post-change via Cosmos fleet health check

## When AADV is NOT Required

- Internal refactors with no API/schema changes
- Documentation updates
- Test additions that don't change behavior
- Bug fixes that restore previously-specified behavior

## Escalation

If unsure whether a change requires AADV, ask Ethos. Default to announcing — the cost of unnecessary AADV is low; the cost of a silent earthquake is high.

---

*Ethos, T1 Lead AIML, 2026-03-23*
