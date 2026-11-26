# Submission email (draft; send Nov 29, deadline Nov 30 2026)

To: trusted-ai-symposium@amazon.com
From: <corresponding author, TBD>
Cc: <co-authors, TBD>
Attach: main.pdf, renamed to `sqlcf_trusted_ai_2027.pdf`

Subject: Trusted AI Symposium 2027 submission: Single-Database Rewards Are Hackable: Counterfactual Execution for Trustworthy Text-to-SQL RL

Dear Organizers,

Please find attached our submission to the Amazon Trusted AI Symposium 2027, "Single-Database Rewards Are Hackable: Counterfactual Execution for Trustworthy Text-to-SQL RL".

- Authors: Shreshth Rai, Rishii Kumar Singh, Aksh Aggarwal (affiliations and emails are in the PDF)
- Topics: Evaluation & benchmarking in RAI; Reasoning & verification; Agent safety & reliability
- Format: NeurIPS 2025 template, 4 pages plus references and appendix
- Amazon Nova: not used
- Preprint: https://arxiv.org/abs/2611.34363
- Code: https://github.com/RishiiGamer2201/counterfactual-sql-rewards (Apache-2.0)
- Data, models and demo: https://hf.co/counterfactual-sql

Abstract:
Reinforcement learning (RL) for text-to-SQL agents pays a query when its result matches the reference on one database. However, a wrong query can match by luck when the data lack the rows that expose its bug. We study a counterfactual-database (CF) reward that also runs the final query on a few hidden, code-generated copies of the database and pays only if all results match (strict form) or by the share matched (mean form). On 1,302 synthetic audit questions, the strict form lowers the share of buggy queries paid in full from 29.5% to 16.8% and of reward hacks from 54.1% to 1.9%, rejecting 0 of 2,847 correct queries; copies from a family-blind generator do about as well. In a controlled GRPO comparison on a 3.35B model with three seeds per arm, training on the mean form did not improve in-domain accuracy (8.4% vs 11.7%), because the two rewards disagreed on only 5-7% of rollouts; on Spider it gained 1.6 points. One seed reverses both signs, so single-seed reward comparisons mislead.

We understand that submissions are non-archival. We would be glad to present a poster.

Best regards,
<name>, on behalf of the authors

## Checklist before sending
- [ ] No `\placeholder` left in main.tex (`grep -n placeholder main.tex`)
- [ ] build.sh passes: check_numbers all OK, main text ends on page 4
- [ ] Repo and HF links are public and the HF demo Space runs
- [ ] Every co-author has approved the final PDF
