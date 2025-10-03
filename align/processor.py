# align/processor.py
from typing import List, Dict, Optional
import json, logging, pysrt
from core.text_ops import clean, is_dialogue
from core.time_ops import to_seconds
from align.metrics import jaccard, time_scores, combined_score, confidence

log = logging.getLogger(__name__)

class SubtitleProcessor:
    def __init__(self, time_tolerance: float = 2.0, confidence_threshold: float = 0.65):
        self.tol = time_tolerance
        self.cth = confidence_threshold

    def parse_srt_file(self, path: str, time_offset: float = 0.0) -> List[pysrt.SubRipItem]:
        subs = pysrt.open(path, encoding="utf-8")
        if time_offset: subs.shift(seconds=time_offset)
        return subs

    def align_subtitles_verbose(
        self, fa: List[pysrt.SubRipItem], en: List[pysrt.SubRipItem], save_path: Optional[str] = None
    ) -> List[Dict]:
        en_texts = [clean(s.text) for s in en]
        en_starts = [to_seconds(s.start) for s in en]
        en_ends = [to_seconds(s.end) for s in en]
        out: List[Dict] = []

        for i, f in enumerate(fa):
            ft, fs, fe = clean(f.text), to_seconds(f.start), to_seconds(f.end)
            if not is_dialogue(ft):
                out.append({"fa_index": i, "fa_text": ft, "fa_start": fs, "fa_end": fe,
                            "matched": False, "reason": "non_dialogue"}); continue
            best = (-1, -1.0, 0.0, 0.0, 0.0)
            for j, et in enumerate(en_texts):
                if not is_dialogue(et): continue
                if abs(fs - en_starts[j]) > self.tol * 3: continue
                t_s, o_s = time_scores((fs, fe), (en_starts[j], en_ends[j]), self.tol)
                c = combined_score(t_s, o_s, jaccard(ft, et))
                if c > best[1]: best = (j, c, t_s, o_s, en_starts[j])
            j = best[0]
            conf = confidence(best[2], best[3]) if j >= 0 else 0.0
            acc = conf >= self.cth if j >= 0 else False
            out.append({
                "fa_index": i, "fa_text": ft, "fa_start": fs, "fa_end": fe,
                "matched": j >= 0, "en_index": j,
                "en_text": en_texts[j] if j >= 0 else "",
                "en_start": en_starts[j] if j >= 0 else None,
                "en_end": en_ends[j] if j >= 0 else None,
                "time_diff": (abs(fs - best[4]) if j >= 0 else None),
                "time_score": best[2], "overlap": best[3],
                "text_sim": 0.0, "combined_score": best[1],
                "confidence": conf, "accepted": acc,
                "reason": "accepted" if acc else "rejected_or_none"
            })

        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
                log.info("Saved verbose alignment → %s", save_path)
            except Exception as e: log.error("Save failed: %s", e)
        return out
