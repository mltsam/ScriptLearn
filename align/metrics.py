# align/metrics.py
from typing import Tuple
from core.text_ops import tokens
from core.time_ops import overlap

def jaccard(a: str, b: str) -> float:
    sa, sb = tokens(a), tokens(b)
    return 0.0 if not sa or not sb else len(sa & sb) / len(sa | sb)

def time_scores(fa: Tuple[float, float], en: Tuple[float, float], tol: float) -> Tuple[float, float]:
    (fs, fe), (es, ee) = fa, en
    diff = abs(fs - es)
    t_score = max(0.0, 1.0 - (diff / tol))
    sh = max(1e-6, min(fe - fs, ee - es))
    o_score = overlap(fs, fe, es, ee) / sh if sh > 0 else 0.0
    return t_score, o_score

def combined_score(t_score: float, o_score: float, txt_sim: float) -> float:
    return 0.6 * t_score + 0.25 * o_score + 0.15 * txt_sim

def confidence(t_score: float, o_score: float) -> float:
    return 0.7 * t_score + 0.3 * o_score
