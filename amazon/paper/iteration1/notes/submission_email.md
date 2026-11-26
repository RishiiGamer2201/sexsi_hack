# Submission email (final draft; deadline Nov 30 2026)

To: trusted-ai-symposium@amazon.com
From: Rishii Kumar Singh <rishiikumarsingh_ene_25b18073@dtu.ac.in>
Cc: shreshthrai_mc24b06_039@dtu.ac.in, akshaggarwal_cse_25a01023@dtu.ac.in
Attach: main.pdf, renamed to `sqlcf_trusted_ai_2027.pdf`

Subject: Trusted AI Symposium 2027 poster submission: Single-Database Rewards Are Hackable: Counterfactual Execution for Trustworthy Text-to-SQL RL

Dear Organizers,

Please find attached our poster submission to the Trusted AI Symposium 2027:

"Single-Database Rewards Are Hackable: Counterfactual Execution for Trustworthy Text-to-SQL RL"

- Authors: Shreshth Rai, Rishii Kumar Singh, Aksh Aggarwal
- Affiliation: Artificial Intelligence and Machine Learning Society (AIMS-DTU), Delhi Technological University, New Delhi
- Emails: shreshthrai_mc24b06_039@dtu.ac.in, rishiikumarsingh_ene_25b18073@dtu.ac.in, akshaggarwal_cse_25a01023@dtu.ac.in
- Topics: Evaluation & benchmarking in RAI; Reasoning & verification; Agent safety & reliability; Red-teaming & stress testing
- Format: NeurIPS 2025 LaTeX template, 4 pages plus references and appendix
- Preprint: https://arxiv.org/abs/2611.34363 (we understand the symposium is non-archival and that double submission is acceptable)
- Code: https://github.com/RishiiGamer2201/counterfactual-sql-rewards
- Data, models and an in-browser demo: https://huggingface.co/counterfactual-sql

Summary: Reinforcement learning for text-to-SQL agents usually pays a query when its result matches the reference on one database, so a wrong query can be rewarded by luck. We study a counterfactual-database reward that also checks the final query on a few hidden, code-generated copies of the database. On 1,302 audit questions it lowers the share of buggy queries paid in full from 29.5% to 16.8% and of reward hacks from 54.1% to 1.9%, while rejecting none of 2,847 correct queries. In a controlled three-seed GRPO comparison on a 3.35B model, training on this reward did not improve in-domain accuracy but gained 1.6 points on Spider, and one seed reverses both results, so single-seed reward comparisons can mislead.

We would be glad to present this work as a poster. Thank you for organising the symposium.

Best regards,
Rishii Kumar Singh
on behalf of Shreshth Rai and Aksh Aggarwal
AIMS-DTU, Delhi Technological University

## Checklist before sending
- [ ] Shreshth and Aksh have approved the final PDF (same as arXiv 2611.34363)
- [ ] Attachment is the current build: amazon/paper/iteration1/main.pdf, renamed `sqlcf_trusted_ai_2027.pdf`
- [ ] Sent from the DTU address, co-authors in Cc
- [ ] Sent before Nov 30 2026 (any time zone; aim for Nov 28-29 IST)
