# align/offset.py
import json, logging
from statistics import median
from typing import List
import numpy as np

log = logging.getLogger(__name__)

def _load_candidates(path: str, mode: str, top_k: int) -> List[dict]:
    data = json.load(open(path, "r", encoding="utf-8"))
    if mode == "accepted":
        c = [d for d in data if d.get("accepted") and d.get("en_start") is not None]
    elif mode == "top_combined":
        s = sorted([d for d in data if d.get("en_start") is not None],
                   key=lambda x: x.get("combined_score", 0), reverse=True)
        c = s[:top_k]
    else:
        c = [d for d in data if d.get("en_start") is not None]
    return c

def compute_global_offset_from_verbose(path: str, mode="accepted", min_samples=10, top_k=100) -> float:
    diffs = []
    for d in _load_candidates(path, mode, top_k):
        try: diffs.append(float(d["en_start"]) - float(d["fa_start"]))
        except Exception: pass
    if not diffs: raise ValueError("No matches to compute offset.")
    if len(diffs) < min_samples: log.warning("Only %d samples (<%d). Using median.", len(diffs), min_samples)
    off = float(median(diffs)); arr = np.array(diffs)
    log.info("Offset from %d samples — median=%.3fs mean=%.3fs std=%.3fs", len(diffs), off, arr.mean(), arr.std())
    return off

def iterative_find_and_apply_offset(proc, fa_path: str, en_path: str, verbose_out: str,
                                    initial_en_offset=0.0, max_iters=3, mode="accepted") -> float:
    cur = initial_en_offset
    for it in range(1, max_iters + 1):
        log.info("ITER %d: EN offset=%.3fs", it, cur)
        fa, en = proc.parse_srt_file(fa_path), proc.parse_srt_file(en_path, time_offset=cur)
        proc.align_subtitles_verbose(fa, en, save_path=verbose_out)
        try: sug = compute_global_offset_from_verbose(verbose_out, mode=mode)
        except Exception as e: log.error("Offset failed: %s", e); break
        delta = sug - cur; log.info("Suggested=%.3fs (Δ=%.3fs)", sug, delta)
        cur = sug
        if abs(delta) < 0.05: log.info("Converged."); break
    log.info("Final EN offset: %.3fs", cur); return cur
