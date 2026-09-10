#!/usr/bin/env python3
"""OpenAI-compatible eval + throughput harness for the dev2 Qwen3.8-Flash-Next endpoint.

Runs against http://127.0.0.1:8001/v1 (model "pennyroyal"). Reports:
  - decode tok/s (prefill-excluded estimate via completion_tokens / wall time)
  - a medium-context five-turn conversation on cognitive techniques/methods for AI agents
  - a reasoning sample and a tool-call-format sample
"""
import json, time, sys, urllib.request

BASE = "http://127.0.0.1:8001/v1"
MODEL = "pennyroyal"

def chat(messages, max_tokens=700, temperature=0.6, stream=False):
    body = {"model": MODEL, "messages": messages, "max_tokens": max_tokens,
            "temperature": temperature, "stream": stream}
    req = urllib.request.Request(
        BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read().decode())

def complete(prompt, max_tokens=600, temperature=0.6):
    body = {"model": MODEL, "prompt": prompt, "max_tokens": max_tokens,
            "temperature": temperature}
    req = urllib.request.Request(
        BASE + "/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read().decode())

def hr(label):
    print("\n" + "=" * 70 + "\n" + label + "\n" + "=" * 70)

def throughput():
    hr("1) THROUGHPUT (token/second)")
    prompt = ("Write a detailed, production-quality Python class that implements an LRU cache "
              "with thread safety, expiration, and hit/miss statistics. Then explain the "
              "concurrency tradeoffs. ")
    t0 = time.time()
    resp = chat([{"role": "user", "content": prompt}], max_tokens=800, temperature=0.0)
    dt = time.time() - t0
    u = resp["usage"]
    ngen = u["completion_tokens"]
    print(f"completion_tokens={ngen}  wall={dt:.2f}s  decode_tok_s={ngen/dt:.1f}")
    print(f"usage={u}")
    # second, heavier prefill
    long_prompt = ("Explain in detail the computational complexity of matrix multiplication, "
                   "attention, and the Transformer. Walk through each step of building a "
                   "retrieval-augmented generation system and discuss when to choose sparse "
                   "vs dense retrieval, plus how to evaluate such a pipeline end-to-end. ") * 6
    t0 = time.time()
    resp = chat([{"role": "user", "content": long_prompt}], max_tokens=500, temperature=0.6)
    dt = time.time() - t0
    u = resp["usage"]
    print(f"long-prefill: prompt_tokens={u['prompt_tokens']} completion={u['completion_tokens']} "
          f"wall={dt:.2f}s decode_tok_s={u['completion_tokens']/dt:.1f}")

def cognitive_five_turn():
    hr("2) MEDIUM-CONTEXT FIVE-TURN: COGNITIVE TECHNIQUES & METHODS FOR AI AGENTS")
    turns = [
        "Explain what metacognition means for an AI agent, and why it matters for self-correction.",
        "How do ReAct, chain-of-thought, and self-consistency differ as agent reasoning techniques? "
        "Give concrete tradeoffs and when each is appropriate.",
        "What is reflection, and how can an agent use it to improve across repeated tasks?",
        "Describe a practical method for an agent to maintain durable working memory across a long "
        "session without losing important context.",
        "Synthesize all of this into one framework an agent could use to decide when to think, when to "
        "act, and when to reflect.",
    ]
    messages = []
    for i, q in enumerate(turns):
        messages.append({"role": "user", "content": q})
        resp = chat(messages, max_tokens=700, temperature=0.7)
        text = resp["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": text})
        u = resp["usage"]
        print(f"\n----- TURN {i+1} (ctx prompt={u['prompt_tokens']}, gen={u['completion_tokens']}) -----\nQ: {q}\n---A---\n{text}")
    print("\n[TURN 5 DONE: total context tokens in final call = "
          f"{resp['usage']['prompt_tokens']}]")

def reasoning():
    hr("3) REASONING SAMPLE (thinking mode)")
    msg = [{"role": "user", "content":
            "A farmer has 17 sheep. All but 9 die. How many are left? Reason carefully."}]
    resp = chat(msg, max_tokens=500, temperature=0.3)
    print(resp["choices"][0]["message"]["content"])
    print("\nusage=", resp["usage"])

def tool_call_fmt():
    hr("4) TOOL-CALL FORMAT SAMPLE")
    print("(subjective: does the model produce a clean JSON tool/function call?)")
    msg = [{"role": "user", "content":
            "Use the get_weather(city) tool to check the weather in Berlin and Paris. "
            "Make two tool calls with the exact JSON schema {\"city\": \"<name>\"}."}]
    resp = chat(msg, max_tokens=400, temperature=0.2)
    print(resp["choices"][0]["message"].get("content", ""))
    print("\nusage=", resp["usage"])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fast":
        throughput()
    else:
        throughput()
        cognitive_five_turn()
        reasoning()
        tool_call_fmt()
    print("\nDONE.")
