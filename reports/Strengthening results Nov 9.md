# Strengthening results, Nov 9

What was done for items 1–5 of plan.md §9. None of it used the GPU; the VM stayed off. Everything is in commit `56b6dfb` on `main`. `verify_all.py` reproduces every results file exactly.

## Bottom line

The entry is now about **a reward auditor that finds the same hole in two public RL rewards and in eight published systems on a real benchmark**. The training null is explained and paired with a pre-registered follow-up. Three of the four new experiments support the thesis. One (gold-free voting, item 3) is a null, and the article reports it as one.

## 1. Real benchmark: Spider dev (A2, ARTICLE E6)

We took the public Spider-dev predictions of 8 systems and scored each on the original database and on Zhong et al.'s test-suite databases (1034 questions). The "lucky" share is the fraction of answers that pass on the original DB but fail on another valid DB:

| System | Lucky share of its correct-looking answers |
|---|---|
| Claude | 14.9% [12.6, 17.5] |
| C3 (ChatGPT) | 14.1% |
| DIN-SQL | 11.4% |
| GPT-4 Turbo | 10.6% |
| DAIL-SQL | 8.9% |
| RASAT+PICARD | 8.3% |
| RESDSQL | 8.2% |
| Graphix | 8.1% |

- **Why it matters:** an RL reward that checks only one DB would pay all of these. The problem is not an artifact of our synthetic data.
- **Hand check of 40 cases:** 27 return a different row count, 13 return different values. Typical bugs: grouping by name where names repeat, `EXCEPT` vs `NOT IN`, `LIMIT 1` with ties, `LEFT JOIN` zero rows.
- **Caveats:**
  - Some cases are ties or ambiguous gold, so treat these rates as upper bounds.
  - Our comparator is stricter than the official script, so the absolute EX/TS numbers are not leaderboard numbers.

## 2. SkyRL-SQL reward audit (A3, ARTICLE E7)

| Reward | Mutants paid | Hacks paid | Correct rejected |
|---|---|---|---|
| SkyRL as shipped (set comparison, one DB) | 37.5% | 53.2% | 0 |
| + our counterfactual copies | 27.2% | 1.9% | 0 |
| + strict comparator (our reward) | 16.8% | 1.9% | 0 |

- **Two holes of about equal size:**
  - The database hole (−10.3 pts) is closed by the copies.
  - The comparator hole (−10.4 pts) is closed by the strict comparator. It is almost all dropped `DISTINCT`: 188 of 203 such mutants are paid on every DB by set comparison.
- **How we ran it:** SkyRL's comparison was re-implemented from its source with attribution. Their code was not executed.

## 3. Gold-free voting and the "shaky answer" flag (A4, ARTICLE E8): a null

| Model | First sample | Majority vote, 1 DB | Majority vote, 5 DBs |
|---|---|---|---|
| SFT | 8.5% | 10.9% | 11.8% |
| GRPO-B | 13.9% | **16.9%** | 16.3% |
| GRPO-C | 6.3% | 13.6% | 13.9% |

- **Voting helps.** Voting across the 5 DBs adds nothing over voting on 1 DB (within ±1 pt).
- **Shaky flag** (fewer than half of the samples agree): catches 53–59% of wrong answers at 94–98% precision. The extra DBs add nothing here either.
- **Why:** at 10–15% accuracy, wrong answers already disagree with each other.
- **Side finding:** all three trained models have about the same pass@8 (21.5–22.4%). GRPO-B's gain comes from picking its right answer more often.

## 4. AgentTune reward package (A5)

| Policy (yes-question) | Original | Patched | Patched + result match |
|---|---|---|---|
| Honest query | 3.10 | 3.10 | 5.10 |
| `WHERE 1 = 1`, always "yes" | **3.10** | 2.20 | 1.20 |
| `WHERE customer_id > 0`, always "yes" | 3.10 | 3.10 (residual) | 2.10 |

- `patches/agenttune-sql-reward-hardening.patch`:
  - (a) a WHERE clause only earns the bonus if it names a column;
  - (b) a new opt-in `result_match_reward` compares the returned rows with the gold rows.
- Repro: `scripts/agenttune_repro.py`.
- Test: `tests/test_agenttune_reward.py`. It patches a temp copy, so the vendor tree is unchanged. 9/9 tests pass. `test_precision.py` needs torch, which is not in `.venv`.
- The upstream issue is drafted in `docs/agenttune_sql_reward_issue.md`. **It has not been posted. Your call.**

## 5. Write-up changes (C1–C6)

**ARTICLE.md:**
- **C1, C2:** the TL;DR leads with the audit and states "H4 and H5 not supported". A before→after table follows, with $ per 1k *verified-correct* answers: Command A $5.25 vs GRPO-B $0.48, about 11×.
- **C3:** the null paragraph covers:
  - C was truly stricter (7.1–7.2% lucky vs 0.1–0.3% lenient);
  - the training prompts were too easy (86% pass);
  - the exact CI, −3.7 [−5.3, −2.3], with the one-seed caveat;
  - DualSQL's +0.4 as the parallel;
  - Razin and Lv on why reward accuracy does not drive RL speed.
- **C4:** a prior-art paragraph (Zhong 2020, SpotIt/VeriEQL, ReViSQL, DualSQL, rl-sql), then our three-part novelty delta.
- **C5:** a hack catalogue with x/N paid under each reward. It shows that the remaining 1.9% of paid hacks are all hard-coded IDs (54/235). Also a threats-to-validity box (one seed, one model, synthetic schemas, gold-informed copies, comparator), and AgentTune and AuditKIT named in §2.
- **C6:** §10 is now a pre-registration:
  - on a lucky-prone curriculum, C-min beats B by **≥ 2 pts verified**, mean of 3 seeds, 120 steps;
  - B's lucky-pass share rises while C-min's does not;
  - otherwise we report a second null.

**Other files:**
- **README:** the judge's view and experiment commands were updated.
- **ABSTRACT.md:** updated, 491 words including headings.
- **plan.md, progress.md:** updated.

## Waiting on you

1. Approval to make the HF repos public (deadline Nov 14 AoE).
2. Whether to post the AgentTune issue upstream.
3. The null decision: accept and polish (recommended, now well supported), or a GPU run. B2 calibration is the cheapest useful one, about $0.75, and would feed the pre-registered test.
4. Command A price confirmation.
5. The HF dataset still has the old results. Re-run `push_dataset.py` once you approve. It stays private.
