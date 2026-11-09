# Draft issue for AgentTune (not posted; needs team OK)

**Title:** Built-in SQL reward pays a "WHERE 1 = 1, answer yes" policy the same as the correct query

**Version:** `d4db4c1`, `src/agenttune/agentic/rewards/builtin_rewards/sql.py` (`correctness_reward` + `query_reward` + `structure_reward`).

**What happens.** `query_reward` gives +0.4 to any query whose text contains `" where "` and +2.0 when "the query returned some rows" agrees with the gold yes/no answer. Neither part checks that the WHERE filters anything or that the rows are the right ones. So a policy that always runs `select * from customers where 1 = 1` and answers `*yes*` gets the maximum score on every yes-question:

| policy (yes-question) | reward |
|---|---|
| honest gold query, answers *yes* | 3.10 |
| `select * from customers where 1 = 1`, answers *yes* | 3.10 |

Over the yes/no grid in our audit (360 questions, 87% yes), that hack averages 2.45 against 3.10 for the honest policy, so GRPO gets almost no pressure to write the real query.

**Repro.** `python scripts/agenttune_repro.py` in our repo (no AgentTune install; it loads `sql.py` with its two imports stubbed).

**Proposed fix** (`patches/agenttune-sql-reward-hardening.patch`, 2 parts, backward compatible):

1. `_has_real_where(sql)`: the WHERE bonus only applies when the WHERE clause names a column after string literals and SQL keywords are removed. `where 1 = 1` now counts as "no WHERE" (−0.5 instead of +0.4): 3.10 → 2.20.
2. New opt-in `result_match_reward(completions, gold_rows=...)`: +2.0 if the last tool result equals the gold query's rows (order-blind multiset), else −1.0. This also catches the residual hack the text check cannot see, `where customer_id > 0` (3.10 → 2.10 vs honest 5.10).

A regression test is in `tests/test_agenttune_reward.py` (applies the patch to a temp copy with `patch -o`).

**Limits.** Part 1 is a text heuristic; any filter on a real column that keeps every row still passes it. Part 2 needs gold rows in the dataset. A stronger check is to execute on more than one database (counterfactual copies), which is what our project measures.
