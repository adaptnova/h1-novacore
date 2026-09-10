#!/usr/bin/env bash
# Production SGLang OpenAI-compatible endpoint for Qwen3.8-Flash-Next-NVFP4
# Single RTX PRO 6000 Blackwell (SM120), jpezzulli/sglang-rtxpro6000 build (systemd, no Docker).
# Posture: FlashInfer autotune OFF (correctness defect), HiCache OFF, MTP accept threshold
# 0.3 (unlocks NEXTN speculative accept; verified-clean on this model per SSHdotCodes recipe).
set -euo pipefail

export PATH=/usr/local/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export CUDA_VISIBLE_DEVICES=0
export HF_HOME=/home/x/sglang-cache/huggingface
export TORCHINDUCTOR_CACHE_DIR=/home/x/sglang-cache/torchinductor
export TRITON_CACHE_DIR=/home/x/sglang-cache/triton
export CUDA_CACHE_PATH=/home/x/sglang-cache/cuda
export SGLANG_CACHE_DIR=/home/x/sglang-cache/sglang
export SGLANG_JIT_CACHE_DIR=/home/x/sglang-cache/sglang/jit
export SGLANG_NUMA_BIND_V2=false
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
export SGLANG_MAMBA_CONV_DTYPE=bfloat16
export TORCH_CUDA_ARCH_LIST=12.0
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false

exec sglang serve \
  --model-path /models/flash-next \
  --served-model-name pennyroyal \
  --host 0.0.0.0 --port 8001 --tp 1 \
  --dtype bfloat16 --quantization modelopt_fp4 --kv-cache-dtype fp8_e4m3 \
  --mem-fraction-static 0.95 \
  --context-length 262144 \
  --json-model-override-args '{"text_config":{"rope_parameters":{"mrope_interleaved":true,"mrope_section":[11,11,10],"rope_type":"yarn","rope_theta":10000000,"partial_rotary_factor":0.25,"factor":1.0,"original_max_position_embeddings":262144}}}' \
  --page-size 64 --max-running-requests 4 \
  --chunked-prefill-size 4096 \
  --mamba-radix-cache-strategy extra_buffer --mamba-ssm-dtype bfloat16 \
  --max-mamba-cache-size 24 --gdn-mtp-cache-mode none \
  --linear-attn-decode-backend flashinfer --linear-attn-prefill-backend flashinfer \
  --mamba-track-interval 64 \
  --ple-offload-embedding --trust-remote-code \
  --chat-template /models/flash-next/chat_template.jinja \
  --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
  --enable-request-time-stats-logging --enable-metrics \
  --default-chat-template-kwargs '{"enable_thinking":true,"preserve_thinking":true,"reasoning_effort":"medium"}' \
  --speculative-algorithm NEXTN --speculative-num-steps 3 \
  --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 \
  --speculative-draft-model-quantization unquant \
  --speculative-accept-threshold-single 0.3 \
  --speculative-accept-threshold-acc 0.3 \
  --disable-flashinfer-autotune \
  --watchdog-timeout 1800
