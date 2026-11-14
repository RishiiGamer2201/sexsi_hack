"""D4 logit distillation (scripts/logit_distil.py): the KL term and the cross-tokenizer alignment.

A character-level stub stands in for the student tokenizer and word-level tokens for the teacher, so the right
alignment is known exactly: a student position aligns iff a teacher token starts at that character, and only
single-character teacher candidates map onto student tokens.
"""
import importlib.util
import math
from collections import Counter
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
spec = importlib.util.spec_from_file_location("logit_distil", Path(__file__).resolve().parent.parent / "scripts/logit_distil.py")
ld = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ld)


class CharTok:
    """Student stub: one token per character (id = code point), plus a 2-token chat suffix."""
    def decode(self, ids, skip_special_tokens=False):
        return "".join("<E>" if i == 0 else chr(i) for i in ids)

    def encode(self, s, add_special_tokens=False):
        return [ord(c) for c in s]


def test_kd_loss_is_zero_iff_student_matches_teacher():
    q = [0.7, 0.2, 0.1]
    logp = torch.full((1, 10), -50.0)
    logp[0, [3, 5, 7]] = torch.tensor(q).log()
    assert ld.kd_loss(torch.log_softmax(logp, -1), [(0, [3, 5, 7], q)]).item() == pytest.approx(0, abs=1e-5)
    # free logits trained on the KL alone end with the teacher's distribution on the candidates
    x = torch.zeros(1, 10, requires_grad=True)
    opt = torch.optim.Adam([x], lr=0.1)
    for _ in range(500):
        opt.zero_grad()
        ld.kd_loss(torch.log_softmax(x, -1), [(0, [3, 5, 7], q)]).backward()
        opt.step()
    p = torch.softmax(x, -1)[0]
    assert (p[[3, 5, 7]] / p[[3, 5, 7]].sum()).tolist() == pytest.approx(q, abs=0.02)
    assert ld.kd_loss(torch.log_softmax(x, -1), [(0, [3, 5, 7], q)]).item() < 0.05


def test_align_char_student_word_teacher():
    text = "SELECT a FROM t"
    comp = [ord(c) for c in text] + [0, 0]  # the chat template's end-of-turn tokens after the answer
    words = ["SELECT", " a", " FROM", " t"]
    # each teacher step: two multi-char candidates (unmappable) and one single-char candidate (mappable)
    top = [[[w, math.log(0.6)], [w + "x", math.log(0.3)], [w[0], math.log(0.1)]] for w in words]
    st = Counter()
    kd = ld.align(CharTok(), comp, text, {"tokens": words, "top": top}, st, {}, strict=False)  # start-only mechanics
    starts = [0, 6, 8, 13]  # character offsets where the teacher's tokens start
    assert [k for k, _, _ in kd] == starts
    assert st["answer_positions"] == len(text) and st["aligned_positions"] == 4
    for (k, s, q), w in zip(kd, words):
        assert s == [ord(w[0])] and q == [pytest.approx(1.0)]
    assert st["mass_mapped"] / st["mass_total"] == pytest.approx(0.1)


def test_align_stops_at_broken_teacher_token_and_missing_text():
    text = "SELECT é"
    st = Counter()
    # a byte-level teacher splits é into two halves that each decode to U+FFFD: alignment stops there
    kd = ld.align(CharTok(), [ord(c) for c in text], text,
                  {"tokens": ["SELECT", " ", "�", "�"], "top": [[["S", 0.0]], [[" ", 0.0]], [["x", 0.0]], [["y", 0.0]]]}, st, {}, strict=False)
    assert [k for k, _, _ in kd] == [0, 6] and st["teacher_tokens_cut"] == 2
    st = Counter()
    assert ld.align(CharTok(), [ord(c) for c in "other"], text, {"tokens": [], "top": []}, st, {}) == []
    assert st["text_not_found"] == 1


def test_strict_alignment_drops_split_mismatches():
    """kd_a1's bug: same start, different split. Teacher "SE"+"LECT" vs a char-level student: only the position
    where both tokens are the same single character survives with strict=True."""
    text = "SELECT a"
    comp = [ord(c) for c in text]
    lp = {"tokens": ["SE", "LECT", " ", "a"], "top": [[["S", 0.0]], [["L", 0.0]], [[" ", 0.0]], [["a", 0.0]]]}
    st = Counter()
    assert [k for k, _, _ in ld.align(CharTok(), comp, text, lp, st, {}, strict=False)] == [0, 2, 6, 7]
    st = Counter()
    kd = ld.align(CharTok(), comp, text, lp, st, {})
    assert [k for k, _, _ in kd] == [6, 7] and st["dropped_split_mismatch"] == 2
