# core/text_ops.py
import re
from typing import Optional, Set

TAG = re.compile(r"<[^>]+>")
NOTE = re.compile(r"[♪♫♬♩]")
URL = re.compile(r"https?://\S+|www\.\S+")
ONLY_SYM = re.compile(r"^[\W_]+$")
PARENS = re.compile(r"^[\(\[\{].*[\)\]\}]$")

NOISE = [
    r"\bsync\b", r"\bcorrections?\b", r"\blicense\b", r"www\.",
    r"http[s]?:\\/\\/", r"\.com\b", r"\.net\b", r"\bsubtitle(s)?\b",
    r"\btranslation\b", r"\btranslator\b", r"\bby\s+[a-z0-9\.\-]+\b",
]

def clean(text: Optional[str]) -> str:
    if not text: return ""
    t = TAG.sub("", text)
    t = NOTE.sub("", t)
    t = URL.sub("", t)
    return re.sub(r"\s+", " ", t).strip()

def is_dialogue(text: Optional[str]) -> bool:
    if not text: return False
    txt = text.strip()
    if not txt: return False
    low = txt.lower()
    if any(re.search(p, low) for p in NOISE): return False
    if PARENS.match(txt):
        inside = re.sub(r"^[\(\[\{]\s*|\s*[\)\]\}]$", "", txt)
        return bool(len(inside.split()) <= 2 and re.search(r"[A-Za-z\u0600-\u06FF]", inside))
    if ONLY_SYM.match(txt): return False
    return bool(re.search(r"[A-Za-z\u0600-\u06FF]", txt))

def tokens(s: str) -> Set[str]:
    return set(re.findall(r"\w+", (s or "").lower()))
