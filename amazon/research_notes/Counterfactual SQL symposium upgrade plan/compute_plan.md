# Compute plan: options, prices and budget scenarios for the next phase of text-to-SQL RL (researched 2026-11-21)

Scope: which GPU or instance to use for each job, $/h (on-demand and spot), expected hours, budget scenarios at $25 / $100 / $300, quota and credit steps, and risks. Two horizons: the poster deadline on Nov 30 2026 (9 days away), then the presentation on Feb 18 2027.

Baseline from past runs (given by the coordinator, not re-measured): one 60-step GRPO run (Tiny Aya Global 3.35B, LoRA r16, vLLM rollouts, 6 rollouts x 4 prompts, 2,048 new tokens) took about 3.5 h on one L4 (GCP VM "sqlcf-l4", asia-south1-a), at about $5 per run. That is about 3.5 min per step, or about 17 steps/h. Test eval takes about 13 min per model; the Spider eval takes 36 min for 4 models (about 9 min each). SFT took 72 min on a local RTX 5070 Ti.

---

## Q1. AWS GPU instance prices (g6 / g6e / g5, cheap regions) and live CLI checks

### Takeaway
g6.xlarge (1x L4 24 GB) costs about the same as the team's GCP L4: $0.805/h on-demand in us-east-1 and us-west-2, and $0.966/h in ap-south-1. Spot in ap-south-1b was as low as $0.326/h. g6e.xlarge (1x L40S 48 GB) is $1.861/h on-demand with spot only 9–15% cheaper (about $1.58–1.70/h). Every family shows ">20%" spot interruption frequency. The read-only AWS CLI checks could not run because the CLI session in WSL has expired.

### Cited Findings
- g6.xlarge: 4 vCPU, 16 GiB RAM, 1x NVIDIA L4 24 GiB. On-demand $0.805/h ($0.8048), spot $0.599/h (default region us-east-1). Page updated 11/21/2026 8:33 AM. — [Vantage g6.xlarge](https://instances.vantage.sh/aws/ec2/g6.xlarge)
- g6e.xlarge: 4 vCPU, 32 GiB RAM, 1x NVIDIA L40S 48 GiB. On-demand $1.861/h, spot $1.666/h (us-east-1). Page updated 11/21/2026 8:33 AM. — [Vantage g6e.xlarge](https://instances.vantage.sh/aws/ec2/g6e.xlarge)
- g6.xlarge in ap-south-1 (Mumbai): on-demand $0.9664/h. Spot $0.3260/h in ap-south-1b (aps1-az3, 66% off) and $0.5264/h in ap-south-1a. Interruption frequency ">20%" (score 53/100). Labelled "live" with no timestamp; fetched 2026-11-21. — [DoiT ap-south-1 g6.xlarge](https://www.doit.com/compute/spot/ap-south-1/g6.xlarge)
- g6.xlarge in us-west-2: on-demand $0.8048/h. Spot $0.4862/h (us-west-2b), $0.5337 (2d), $0.6434 (2c), $0.7003 (2a). Interruption ">20%" (score 41/100). Fetched 2026-11-21. — [DoiT us-west-2 g6.xlarge](https://www.doit.com/compute/spot/us-west-2/g6.xlarge)
- g6e.xlarge in us-east-1: on-demand $1.8610/h. Spot $1.5848/h (1b, 15% off) to $1.7026/h (1a/1c). Interruption ">20%" (score 50/100). Fetched 2026-11-21. — [DoiT us-east-1 g6e.xlarge](https://www.doit.com/compute/spot/us-east-1/g6e.xlarge)
- g5.xlarge (1x A10G 24 GB) in us-east-1: on-demand $1.0060/h. Spot $0.6665/h (1f) to $0.8924/h (1b). Interruption ">20%" (score 56/100). Fetched 2026-11-21. — [DoiT us-east-1 g5.xlarge](https://www.doit.com/compute/spot/us-east-1/g5.xlarge)
- One aggregator lists g6, g5 and g6e all at $0.18/h on-demand in us-east-1. That figure conflicts with every other source and should be ignored. — [PricePerToken AWS GPU](https://pricepertoken.com/gpu-pricing/aws), contradicted by [Vantage](https://instances.vantage.sh/aws/ec2/g6.xlarge) and [DoiT](https://www.doit.com/compute/spot/us-east-1/g6.xlarge)
- **Live CLI check (run 2026-11-21 in WSL Ubuntu, read-only):** the AWS CLI is at `~/.local/bin/aws` and the default region is `ap-south-1`. Every call (`sts get-caller-identity`, `service-quotas get-service-quota` for L-DB2E81BA and L-3819A6DF in us-east-1/us-west-2/ap-south-1, `ec2 describe-spot-price-history`) failed with `Your session has expired. Please reauthenticate using 'aws login'.` The account type, quota values and live spot prices are therefore **unverified**. No account ID or ARN was printed. — local CLI output (no URL). **Superseded by the re-run after the user logged in again; see Q8 (Live AWS check, 2026-11-21 15:59 UTC): all G and VT quotas are 0.**

### Inferences
- With spot, ap-south-1b g6.xlarge at about $0.33/h is the cheapest L4 in this research. It is about 30% cheaper than GCP L4 spot in asia-south1 ($0.474/h, see Q5), but it needs an AWS GPU quota the account probably does not have yet (see Q2).
- g6e spot gives very little discount, so L40S is worth paying for only when the speed or the 48 GB of memory is needed (7B-class models). It does not save money for 3B runs.
- g5 (A10G) is more expensive than g6 (L4) on-demand, while A10G bandwidth (about 600 GB/s, not sourced here) beats the L4's 300 GB/s. Treat it as a fallback when g6 capacity is short.
- g6.xlarge has only 16 GiB of host RAM, versus 32 GiB on g2-standard-8 (inferred from the name; not checked on a pricing page). Loading a 7B model and running vLLM on 16 GiB RAM may OOM on the host. If AWS is used for 7B work, pick g6e.xlarge (32 GiB) or a bigger g6 size.

### Gaps
- Live quota values and live spot history from the user's account were not checked because the session had expired. To re-run after `aws login`: `aws service-quotas get-service-quota --service-code ec2 --quota-code L-DB2E81BA --region <r>` (and `L-3819A6DF`), plus `aws ec2 describe-spot-price-history --instance-types g6.xlarge g6e.xlarge --product-descriptions Linux/UNIX --region <r>`.
- No region-specific price for g6e in us-west-2 or ap-south-1, and none for g6.2xlarge or g6.4xlarge.
- No sourced pricing for p4d or p5 "fractional" options. I found no source showing a single-GPU A100 or H100 slice on EC2 at a price that fits these budgets. A full p4d.24xlarge (8x A100) is far outside the $300 envelope, so I did not price it.

---

## Q2. AWS GPU quotas, SageMaker vs raw EC2, and the Deep Learning AMI

### Takeaway
AWS documents "Running On-Demand G and VT instances" as **0 by default** (adjustable). Community reports put increases at anywhere from 1–2 days to over a week, with extra scrutiny for new or low-usage accounts. For the Nov 30 deadline, AWS is a gamble unless the quota is already granted. File the request today if AWS will be used at all. Raw EC2 with the DLAMI is simpler than SageMaker for a 9-day window. vLLM must be pip-installed, because the DLAMI does not include it.

### Cited Findings
- AWS EC2 quota docs list "Running On-Demand G and VT instances" with default 0, adjustable. — [AWS EC2 instance type quotas](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-quotas.html)
- How to request: Support Center → Create case → "Looking for service quota increases?" → EC2 Instances. — [AWS Knowledge Center](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/)
- Anecdotal timing: one user waited "over a week" for a G-quota increase even after escalating. Others advise following up if there is no reply in 24–48 h. New or low-usage accounts may face more scrutiny for GPU types. — [re:Post thread](https://repost.aws/questions/QUBBbH23A8TliNJqb8XliSYg/how-long-to-wait-for-a-response-to-a-quota-increase-reply); [re:Post GPU quota thread](https://repost.aws/questions/QUxBIRsixkTneUqAemd6QVjw/good-question-this-is-a-common-issue-when-you-try-to-launch-gpu-instances-like-g-4-dn-xlarge-in-aws-but-get-an-error-such-as-instance-limit-exceeded-you-do-not-have-sufficient-quota); [yomotherboard (anecdotal)](https://yomotherboard.com/question/whats-the-typical-timeline-for-quota-increase-requests/)
- Spot instance quotas are a separate vCPU-based limit. — [AWS Spot Instance quotas](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-limits.html)
- SageMaker Managed Spot Training: "up to 90%" savings versus SageMaker on-demand. Savings are measured as 1 − billable/training time. Spot jobs do not fall back to on-demand, and checkpointing is recommended because capacity can be reclaimed. — [SageMaker Managed Spot docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html); [AWS News Blog](https://aws.amazon.com/blogs/aws/managed-spot-training-save-up-to-90-on-your-amazon-sagemaker-training-jobs)
- DLAMI "Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.7 (Ubuntu 22.04)": releases dated 20260222 and 20260308. Supports G4dn, G5, G6, Gr6, G6e, P4, P4de, P5, P5e, P5en, P6-B200. NVIDIA driver 570.172.08 / CUDA 12.8. vLLM is not listed as pre-installed. — [DLAMI PT2.7 20260308](https://docs.amazonaws.cn/en_us/dlami/latest/devguide/aws-deep-learning-ami-gpupt27oss-ul2204-2026-03-12.html); [DLAMI PT2.7 20260222](https://docs.amazonaws.cn/en_us/dlami/latest/devguide/aws-deep-learning-ami-gpupt27oss-ul2204-2026-02-24.html)
- A separate AWS Marketplace vLLM image (Ubuntu 24.04, Qwen2.5-7B preinstalled) exists. It is an inference server, not a training image. — [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-d7rsvtxy2ltca)

### Inferences
- Quotas are counted in vCPUs. g6.xlarge and g6e.xlarge each need 4 vCPU, so ask for 16 vCPU on-demand **and** 16 vCPU spot (G and VT) in one region (ap-south-1 is the default region and has the cheapest g6 spot). That covers about 4 single-GPU runs at once.
- SageMaker training jobs would mean repackaging the AgentTune/vLLM GRPO loop as a training container, and ml.* instances carry a premium over EC2 (I found no ml.g6 price). With 9 days left, raw EC2 spot plus checkpoint/resume is the shorter path. SageMaker Managed Spot is mainly worth it for its automatic restart after interruption.
- Recommended AWS image: the DLAMI PyTorch 2.7 Ubuntu 22.04 OSS AMI, then `pip install vllm` pinned to the version the team already uses on GCP, after checking vLLM's torch requirement. Or skip the DLAMI and replicate the GCP VM environment from the repo's requirements.

### Gaps
- No official AWS turnaround SLA for G/VT quota increases. All timing figures are anecdotal.
- The default value of the G and VT **spot** quota (L-3819A6DF) was not confirmed from a primary source.
- No $/h found for SageMaker ml.g6.xlarge or ml.g6e.xlarge training.

---

## Q3. Credits: AWS Cloud Credit for Research, Activate, student programs, Trusted AI Symposium

### Takeaway
No credit program will land before Nov 30. Cloud Credit for Research takes 90–120 days, which also likely misses Feb 18 2027. Activate (Founders) needs a startup and takes 7–10 business days. The Trusted AI Symposium 2027 page lists no compute or Nova credits. Budget as if the team pays out of pocket. Activate and the symposium contact email are the only quick long-shots.

### Cited Findings
- AWS Cloud Credit for Research: graduate, post-graduate and PhD students at accredited institutions are eligible, for research outside coursework (coursework goes to AWS Educate). Student awards are capped at $5,000. Rolling review: the FAQ aims for 30 days but says up to 120. The research-credits page lists typical cycles of 90–120 days with no expedited review. Credits post within 10 business days of approval and last 1 year. Administrative, operational and ongoing projects are excluded. — [AWS research credits](https://aws.amazon.com/research-credits); [Proposal review FAQ](https://aws.amazon.com/government-education/research-and-technical-computing/cloud-credit-for-research/faqs/proposal-review-process); [Educators and students FAQ](https://aws.amazon.com/government-education/research-and-technical-computing/cloud-credit-for-research/faqs/information-for-educators-and-students)
- Some universities add their own rules (e.g., Yale requires faculty-advisor sponsorship). — [Yale AWS Research Credits](https://research.computing.yale.edu/aws-research-credits)
- AWS Activate Founders: $1,000 in credits (select startups up to $5,000 over time). Requires a pre-Series-B startup with a company website or profile, founded within 10 years, on an AWS Paid Tier plan, self-funded. Processing takes 7–10 business days (another AWS page says 5–10). — [AWS Activate guide](https://aws.amazon.com/aws-startups/learn/applying-for-aws-activate-credits-a-step-by-step-guide/); [AWS startups credits](https://aws.amazon.com/startups/credits)
- Trusted AI Symposium 2027 page: event on **February 18, 2027, New Delhi, India**. "Call for posters: Open". Non-archival, double submission acceptable. NeurIPS LaTeX template, up to 4 pages plus references and appendices, emailed to trusted-ai-symposium@amazon.com. **Deadline November 30, 2026**; notification December 31, 2026. Presenter benefits listed: networking, collaboration, jobs, visibility, Amazon Research Award information. **No compute, Nova or AWS credits are mentioned.** — [Amazon Science: Trusted AI Symposium 2027](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- The 2026 edition reportedly offered "complimentary credits to explore and experiment with Nova models" and prioritized papers using Nova (from a search summary of the 2026 page; I did not fetch the page directly). — [Amazon Science: Trusted AI Symposium 2026](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2026)
- Build on Trainium and Amazon Research Awards are separate, proposal-based credit routes (Trainium, not NVIDIA GPUs). — [Build on Trainium CFP Fall 2026](https://www.amazon.science/research-awards/call-for-proposals/build-on-trainium-agentic-recursive-improvement-of-kernels-and-frameworks-call-for-proposals-fall-2026)

### Inferences
- If Nova credits come back for 2027 (unconfirmed), they would cover Nova judges and baselines, which are cheap anyway (see Q4), not GPU training.
- A short email to trusted-ai-symposium@amazon.com asking whether 2027 presenters get Nova or AWS credits costs nothing. Any answer would most likely affect the Feb 2027 horizon only.
- Cloud Credit for Research applies only if a team member is a graduate student. An application made Nov 21 resolves by about Mar 21 2027 at worst, after the Feb 18 presentation.

### Gaps
- AWS Educate's current offering (whether it gives any usable GPU credits) was not researched in depth. I found no source saying it covers G-instance usage.
- The team's eligibility (undergraduate or graduate, startup entity or not) is unknown to me.

---

## Q4. Bedrock and API prices for baselines and judges; cost to judge about 10k SQL candidates

### Takeaway
Judging 10k SQL candidates costs **under $1 with Nova Micro or Lite**, about $6–7 with Nova 2 Lite or Llama 3.3 70B, about $11 with Nova Pro, about $15 with Claude Haiku 4.5, and about $31 with Claude Sonnet 5.5 (first-party price). Batch mode halves most of these. Judges and API baselines are a small line item at every budget level.

### Cited Findings
- Nova Micro: $0.035 / 1M input, $0.14 / 1M output. Nova Lite: $0.06 / $0.24. Nova Pro: $0.80 / $3.20. Nova 2 Lite: $0.30 / $2.50 (third-party page citing aws.amazon.com, Oct 17 2026). The official Bedrock page did not render these rows when fetched. — [developersdigest Nova Micro](https://www.developersdigest.tech/models/nova-micro); official page: [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) (tables JS-rendered, not readable by fetch)
- Bedrock: "select models from Anthropic, Meta, Mistral AI, and Amazon" are priced for batch inference "at a 50% lower price compared to on-demand". — [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- Llama 3.3 70B Instruct on Bedrock: $0.72 / 1M input and $0.72 / 1M output (several aggregators agree; one outlier lists $0.10/$0.20). — [costbench Bedrock](https://costbench.com/software/llm-api-providers/amazon-bedrock/); [cloudprice Bedrock](https://cloudprice.net/models/providers/amazon_bedrock)
- Claude Haiku 4.5 on Bedrock: $1.00 / 1M input, $5.00 / 1M output (one older aggregator lists $0.80/$4). — [Optimizely LLM utility (Bedrock)](https://llm.svc-utility-belt.optimizely.com/models/claude-haiku-4-5/aws-bedrock); [getmaxim Bedrock calculator](https://www.getmaxim.ai/bifrost/llm-cost-calculator/provider/bedrock/model/claude-haiku-4-5.md)
- Anthropic first-party API (pricing table cached 2026-11-03): Claude Haiku 5.5 $0.10 / $0.50 per 1M (prompts up to 100K). Claude Sonnet 5.5 $2 / $10. Claude Haiku 4.5 $1 / $5. Claude on Bedrock is "partner-operated with separate pricing". — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing); Bedrock: [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)

### Inferences
Cost to judge 10,000 candidates. Assumptions: about 800 input tokens each (schema excerpt, question, candidate SQL, rubric) and about 150 output tokens (short verdict), so 8M input and 1.5M output tokens in total, on-demand. The token counts are my assumption, not measured.

| Judge | Calculation | Cost (on-demand) | With batch (-50%) |
|---|---|---|---|
| Nova Micro | 8×0.035 + 1.5×0.14 | **$0.49** | ~$0.25 |
| Nova Lite | 8×0.06 + 1.5×0.24 | **$0.84** | ~$0.42 |
| Claude Haiku 5.5 (first-party) | 8×0.10 + 1.5×0.50 | **$1.55** | ~$0.78 (first-party Batch API) |
| Nova 2 Lite | 8×0.30 + 1.5×2.50 | **$6.15** | ~$3.1 |
| Llama 3.3 70B (Bedrock) | 9.5×0.72 | **$6.84** | ~$3.4 |
| Nova Pro | 8×0.80 + 1.5×3.20 | **$11.20** | ~$5.6 |
| Claude Haiku 4.5 (Bedrock) | 8×1 + 1.5×5 | **$15.50** | ~$7.8 |
| Claude Sonnet 5.5 (first-party) | 8×2 + 1.5×10 | **$31.00** | ~$15.5 |

- Full schemas (about 2,000 input tokens) roughly double the input part of each cost. Reasoning or thinking output can multiply output tokens 5–10x. Cap output with a short structured verdict.
- LLM baselines (zero- or few-shot SQL generation on the test and Spider splits): a few thousand prompts at similar token counts cost about the same as the table above, in the $1–$30 range per model.

### Gaps
- Official Bedrock per-token figures for Nova, Claude and Llama could not be read from aws.amazon.com (JS-rendered tables). The Nova figures come from one aggregator citing AWS; confirm in the Bedrock console or Pricing Calculator.
- Bedrock pricing for the newest Claude models (Haiku 5.5, Sonnet 5.5) was not found. Only first-party prices are given.

---

## Q5. GCP L4 (g2) spot and on-demand, asia-south1 vs us-central1; A100; resizing the team VM

### Takeaway
GCP L4 costs almost the same in both regions: g2-standard-8 is $0.889/h on-demand and $0.474/h spot in asia-south1, versus $0.854/h and $0.511/h in us-central1. Simply switching the existing VM's workloads to **spot** cuts GPU cost by about 47%. A100 40 GB (a2-highgpu-1g) is $3.67/h on-demand and $2.19/h spot in us-central1, and one source says it is **not offered in asia-south1** (another source disagrees).

### Cited Findings
- g2-standard-8 (1x L4): us-central1 $0.8536/h on-demand, $0.5108/h spot. asia-south1 $0.8886/h on-demand, $0.4739/h spot. 3 zones each. Last update Wed Nov 18 2026 16:45 GMT ("accuracy not guaranteed"). — [gcloud-compute g2-standard-8](https://gcloud-compute.com/g2-standard-8.html)
- g2-standard-4 (1x L4, fewer vCPU and RAM): us-central1 $0.7068 on-demand / $0.423 spot. asia-south1 $0.7358 / $0.3924. Same data date. — [gcloud-compute g2-standard-4](https://gcloud-compute.com/g2-standard-4.html)
- a2-highgpu-1g (1x A100 40 GB): us-central1 $3.6734/h on-demand, $2.188/h spot, 4 zones. Available in 10 regions, and asia-south1 is not among them per this source (Nov 18 2026 data). — [gcloud-compute a2-highgpu-1g](https://gcloud-compute.com/a2-highgpu-1g.html); contradicted by [cloudprice.net a2-highgpu-1g](https://cloudprice.net/gcp/compute/instances/a2-highgpu-1g), which lists India/asia-south1 among its regions
- Google: A2 Standard (a2-highgpu-*) machine types have A100 40 GB GPUs, and GPUs exist only in specific zones. — [GCP GPU pricing](https://cloud.google.com/products/compute/gpus-pricing)
- Live gcloud check: gcloud is **not installed** in WSL Ubuntu, so the team VM's machine type and provisioning model could not be read. — local check (no URL)

### Inferences
- The past figure of about $5/run against the listed $0.889/h × 3.5 h ≈ $3.11 suggests that about $2 per run goes to boot disk, setup and idle time, evals, or a larger machine type than g2-standard-8. Stopping the VM promptly (already a team rule) matters as much as the instance choice.
- Resizing: GCP lets you change the machine type of a *stopped* VM. A G2 VM can move between g2 sizes (e.g., g2-standard-8 → g2-standard-16 for more CPU in audits), but it cannot become an A100 VM, because A2 is a different machine series. An A100 needs a new VM in a region that has it (us-central1). This comes from general GCP behaviour and was not verified on a doc page this session.
- Spot VMs on GCP can be preempted. GRPO must checkpoint (e.g., TRL `save_steps` every 10–20 steps) and resume.

### Gaps
- No official GCP page was read for preemption rates or for GPU quotas in the team project.
- A100 availability in asia-south1 is unresolved because the sources conflict. Check with `gcloud compute accelerator-types list --filter="zone~asia-south1"`.
- The team VM's current machine type and quota headroom are unknown (gcloud is absent from WSL).

---

## Q6. Throughput estimates: GRPO steps/hour for 3B and 7B with LoRA on L4 vs L40S vs A100

### Takeaway
I found no published benchmark of GRPO+LoRA steps/hour on L4 vs L40S vs A100. Decode (rollout generation) is memory-bandwidth-bound, and L40S has about 2.9x and A100-40GB about 5.2x the bandwidth of an L4. A reasonable sizing rule is **3B: about 17 steps/h on L4, about 35–45 on L40S, about 50–65 on A100**. A 7B model is roughly 2.3x slower per step than 3B, and probably does not fit on a 24 GB L4 with colocated vLLM and LoRA training without quantization.

### Cited Findings
- Memory bandwidth: L4 about 300 GB/s (24 GB GDDR6). L40S 864 GB/s (48 GB). A100 40 GB SXM4 about 1,555 GB/s; A100 80 GB PCIe 1,935 GB/s, SXM 2,039 GB/s. — [NVIDIA L40S](https://www.nvidia.com/en-sg/data-center/l40s/); [flopper.io A100 vs L4](https://flopper.io/compare/nvidia-a100-pcie-40gb-vs-nvidia-l4-24gb); [technical.city A100 SXM4 40GB](https://technical.city/en/gpu/A100-SXM4-40-GB); [Supermicro L40S datasheet](https://www.supermicro.com/datasheet/datasheet_NVIDIA_L40S_Systems.pdf)
- A 7B model (DeepSeek-R1-Distill-Qwen-7B) reaches about 6,300 output tokens/s aggregate on one H100. A 512-rollout step with 2K-token outputs takes about 3 min on one H100. — [HF blog: Keep the Tokens Flowing](https://huggingface.co/blog/async-rl-training-landscape)
- LoRA weight sync to vLLM takes about 200 ms per sync, versus 350 ms to 5+ s for full merge sync. — [Axolotl vLLM serving docs](https://docs.axolotl.ai/docs/vllm_serving.html)
- TRL supports colocated vLLM (generation on the same GPU as training) or a separate `trl vllm-serve` server. — [HF blog: vLLM colocate in TRL](https://huggingface.co/blog/vllm-colocate); [TRL vLLM integration](https://huggingface.co/docs/trl/main/en/vllm_integration)

### Inferences
- **Measured baseline:** 3.35B on L4, 24 rollouts × up to 2,048 tokens, takes about 3.5 min/step, which is about 17 steps/h, about 3.5 h per 60 steps and **about 11.7 h per 200 steps**.
- **3B on L40S (g6e.xlarge):** bandwidth suggests up to 2.9x, but the training backward pass and Python overhead do not scale as much, so assume 2–2.5x. That gives about 35–45 steps/h, about 4.7–5.8 h per 200 steps.
- **3B on A100 40GB:** assume 3–4x, giving about 50–65 steps/h and about 3–4 h per 200 steps.
- **7B-class (Qwen2.5-7B / Qwen3-8B):** about 2.3x the parameters (7.6/3.35), so per-step time is about 2.3x. bf16 weights alone are about 15 GB, which leaves almost nothing on a 24 GB L4 for the vLLM KV cache plus LoRA activations. Expect to need L40S 48 GB or A100. Estimates: L40S about 15–20 steps/h (about 10–13 h per 200 steps); A100-40GB about 22–28 steps/h (about 7–9 h per 200 steps). On L4 it is only feasible with 4-bit or QLoRA and a smaller vLLM memory share, at about 7 steps/h (about 27 h per 200 steps).
- **Cheapest options from this:** for 3B, an L4 on spot is the cheapest per run. For 7B, L40S spot (~$1.6/h × ~11 h ≈ $18) and A100 spot on GCP (~$2.19/h × ~8 h ≈ $18) cost about the same per 200-step run. A100 finishes sooner.
- Halving max new tokens from 2,048 to 1,024, if SQL completions rarely need 2K tokens, would cut rollout time almost proportionally. That is the cheapest speed-up available on any GPU.

### Gaps
- All the L40S, A100 and 7B step rates above are bandwidth-scaled estimates, not measurements. Run a 5-step timing pilot (about $1) on the target GPU before committing to multi-seed runs.

---

## Q7. Job-to-hardware mapping, budget scenarios ($25 / $100 / $300), and risks

### Takeaway
For Nov 30, stay on the GCP L4 the team already has quota for, switch training runs to **spot**, and spend the $25 tier on 3 seeds × 2 arms of 60-step 3B runs. The $100 tier adds 200-step runs and one 7B pilot, which needs parallel VMs (more quota) to fit in 9 days. The $300 tier is the 2027 plan: 5 seeds, 200+ steps, a 7B arm, and a strong LLM judge.

### Cited Findings
- Prices used below: GCP g2-standard-8 asia-south1 $0.889 on-demand / $0.474 spot — [gcloud-compute g2-standard-8](https://gcloud-compute.com/g2-standard-8.html). AWS g6.xlarge ap-south-1 $0.966 on-demand / $0.326–0.526 spot — [DoiT](https://www.doit.com/compute/spot/ap-south-1/g6.xlarge). AWS g6e.xlarge us-east-1 $1.861 on-demand / $1.585 spot — [DoiT](https://www.doit.com/compute/spot/us-east-1/g6e.xlarge). GCP A100 us-central1 $3.67 on-demand / $2.19 spot — [gcloud-compute a2-highgpu-1g](https://gcloud-compute.com/a2-highgpu-1g.html).
- Spot interruption frequency for g6, g6e and g5 is listed as ">20%". — [DoiT g6 us-west-2](https://www.doit.com/compute/spot/us-west-2/g6.xlarge)
- The 2027 symposium deadline is Nov 30 2026, with notification Dec 31 2026 and the event Feb 18 2027. — [Amazon Science TAS 2027](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)

### Inferences

**Job → hardware**

| Job | Hardware | Why |
|---|---|---|
| SFT (3B) | Local RTX 5070 Ti (free) | Already proven at 72 min |
| GRPO 3B, 60–200 steps | GCP g2-standard-8 **spot** (asia-south1); AWS g6.xlarge spot ap-south-1b as overflow once quota exists | Cheapest $/run, and the team VM image is already set up |
| GRPO 7B-class | AWS g6e.xlarge (L40S 48 GB) spot, or GCP a2-highgpu-1g spot (us-central1) | Needs more than 24 GB of VRAM; both cost about $18 per 200-step run |
| Test/Spider eval | Same GPU box right after training (about 22 min/model), or local 5070 Ti for 3B | Avoid a separate VM spin-up |
| Counterfactual audits (CPU-heavy SQL execution) | Local workstation, or temporarily resize the stopped team VM to a bigger g2 / CPU shape | Needs no GPU; no CPU instance price was researched (gap) |
| LLM judges / baselines | Bedrock Nova Lite/Micro or Claude Haiku 5.5 via batch; Sonnet-class only for a final calibration subset | Under $2 per 10k judgements |

**Hours** (from Q6 estimates; eval ≈ 0.37 h/run):
- 3B, 60 steps: 3.5 h (L4). 3B, 200 steps: 11.7 h (L4) or about 5 h (L40S).
- 7B, 200 steps: about 11 h (L40S) or about 8 h (A100).

**Scenario A: $25 (deadline-safe, Nov 21–30)**
- 3 seeds × 2 arms × 60 steps, 3B, on the GCP L4. That is 6 runs × 3.5 h = 21 GPU-h, plus evals 6 × 0.37 = 2.2 h, for about 23 h in total.
- Cost: spot about 23 × $0.474 ≈ **$11**; on-demand about 23 × $0.889 ≈ $20. Add about $2/run of observed overhead (disk, idle) for about $12 more, unless the VM is stopped promptly.
- Judges: Nova Lite or Haiku 5.5 on 10k candidates, about $1–2.
- **Total ≈ $14–25.** Wall-clock is about 1 day sequential on one VM, which fits easily before Nov 30. No AWS quota needed.

**Scenario B: $100 (stronger poster, still Nov 30 if quota allows parallelism)**
- Scenario A (about $15 on spot).
- Plus 3 seeds × 2 arms × 200 steps, 3B, on L4 spot: 6 × 11.7 h ≈ 70 GPU-h × ~$0.40 (mix of GCP $0.474 and AWS ap-south-1b $0.326) ≈ **$28–33**.
- Plus one 7B pilot (5-step timing check, then one 200-step run per arm) on g6e spot: about 2 × 11 h × $1.59 ≈ **$35**.
- Plus judges and baselines (a Sonnet 5.5 calibration subset plus Nova bulk): about $10.
- **Total ≈ $90–100.** Wall-clock: about 70 h of 3B runs needs 3–4 VMs in parallel to finish in about 1 day each. This depends on the GCP L4 quota in the project and/or the AWS G/VT quota (request 16 vCPU **today**).

**Scenario C: $300 (2027 presentation; Dec 2026 – Feb 2027)**
- 3B: 5 seeds × 2 arms × 200 steps = 10 × 11.7 h ≈ 117 GPU-h on L4 spot, about **$45–55** (on-demand about $105).
- 7B-class: 3 seeds × 2 arms × 200 steps = 6 × ~11 h on g6e spot (~$1.6) or ~8 h on GCP A100 spot ($2.19), about **$105**.
- Longer-horizon ablation (e.g., 500 steps × 2 arms × 1 seed, 3B): about 58 GPU-h × $0.47 ≈ **$27**.
- Evals for all runs (about 25 runs × 0.37 h × ~$0.6) ≈ $6. LLM baselines and judges (Sonnet-class on 10k plus Nova bulk plus multiple baselines) ≈ **$40–60**.
- About 15% contingency for interrupted spot runs: about $35.
- **Total ≈ $260–300.**

**Quota and credit steps (in order)**
1. Today: run `aws login` in WSL, re-run the read-only quota checks, and if they show 0, file G and VT increases for 16 vCPU on-demand and 16 vCPU spot in ap-south-1 (plus us-east-1 for g6e).
2. Today: check the GCP L4 quota in the team project (`gcloud compute regions describe asia-south1`, on a machine with gcloud) to see whether 3–4 parallel L4 VMs are possible.
3. Email trusted-ai-symposium@amazon.com to ask about Nova or AWS credits for 2027 presenters (low odds, no cost).
4. Apply for AWS Cloud Credit for Research only if a team member is a graduate student, and only for the post-Feb 2027 horizon.

**Risks**
- **AWS quota delay:** default 0, and reports of more than a week. Do not put any Nov 30 run on AWS unless the quota is already granted.
- **Spot interruptions** (>20% frequency): a 12-h spot run will likely be interrupted at least once. Make checkpoint/resume (every 10–20 steps, synced to a bucket) mandatory before using spot.
- **7B memory:** a 7B model on 24 GB L4 probably OOMs with colocated vLLM. Budget L40S or A100 for it, and run a 5-step pilot first.
- **Estimate uncertainty:** L40S, A100 and 7B throughput figures are extrapolated from bandwidth (Q6). Treat costs as ±50% until a pilot is timed.
- **Idle and overhead cost:** past runs cost about $5 against about $3.1 of GPU-hours. Idle VMs and disks are a real share of spend, so automate stopping the VM after each run.
- **Cross-cloud setup time:** moving to AWS costs engineering hours (image, data and secrets setup), which matters more than dollars with 9 days left.
- **Price drift:** spot prices change hourly. All figures were fetched on 2026-11-21 (GCP data from Nov 18).

### Gaps
- No CPU-instance ($/h) price was researched for the counterfactual audits.
- Parallel-VM feasibility depends on GCP and AWS quotas that could not be read (AWS session expired; gcloud not installed in WSL).
- Not covered: storage and egress costs (checkpoints, datasets) and the HF Hub upload overhead.

---

## Q8. Live AWS check (2026-11-21, 15:59 UTC, read-only, after the user logged in again)

### Takeaway
The account has **0 vCPU of G and VT quota, on-demand and spot, in us-east-1, us-west-2 and ap-south-1**. No AWS GPU instance can be launched until an increase is granted. That rules AWS out for the Nov 30 runs and makes the GCP L4 the only GPU path for the deadline. Live spot prices match the aggregator figures, and add one new finding: **g6e.xlarge (L40S) spot in ap-south-1a is $1.26/h**, the cheapest L40S seen. Nova Micro, Lite, Pro and 2 Lite are listed ACTIVE in the Bedrock catalog in us-east-1.

### Cited Findings
All from local read-only AWS CLI output in WSL Ubuntu (no URL). Nothing was created, modified or requested, and no model was invoked. Account ID and ARN are redacted.
- **Identity:** `sts get-caller-identity` shows the CLI is authenticated as the account **root user**. Default region (`aws configure get region`): **ap-south-1**.
- **Quotas** (`service-quotas get-service-quota --service-code ec2`):

| Region | L-DB2E81BA "Running On-Demand G and VT instances" | L-3819A6DF "All G and VT Spot Instance Requests" |
|---|---|---|
| us-east-1 | 0.0 | 0.0 |
| us-west-2 | 0.0 | 0.0 |
| ap-south-1 | 0.0 | 0.0 |

- **Spot prices, Linux/UNIX, window 2026-11-20 15:59 → 2026-11-21 15:59 UTC** (`describe-spot-price-history`). Latest price per AZ, with the 24 h range in brackets:

| Region | g6.xlarge (L4) | g6e.xlarge (L40S) |
|---|---|---|
| us-east-1 | 1a $0.584 [0.559–0.584]; 1b $0.713; **1c $0.467** [0.449–0.467]; 1d $0.653; 1f $0.594 | 1a $1.703; **1b $1.585**; 1c $1.704; 1d $1.679 |
| us-west-2 | **2a $0.485** [0.485–0.500]; 2b $0.700; 2c $0.642; 2d $0.534 | 2a/2b/2c $1.836; **2d $1.766** |
| ap-south-1 | 1a $0.526; **1b $0.326** [0.326–0.330] | **1a $1.259** [1.241–1.259]; 1b $1.574 [1.529–1.574] |

- **Bedrock catalog** (`bedrock list-foundation-models --region us-east-1 --by-provider amazon`) lists these as ACTIVE: amazon.nova-micro-v1:0 (plus 24k/128k variants), amazon.nova-lite-v1:0 (plus 24k/300k), amazon.nova-pro-v1:0 (plus 24k/300k), amazon.nova-2-lite-v1:0 (plus 256k), nova-2-sonic, nova-2-5-sonic, nova-2-multimodal-embeddings.

### Inferences
- **Hardware for Nov 30: GCP L4 only.** Scenario A ($25) is unchanged. Scenario B ($100) can only run its parallel 3B runs on GCP L4 VMs if the GCP project's L4 quota allows several at once. Otherwise B shrinks to the 60-step seeds plus 1–2 of the 200-step runs on the single team VM (about 12 h each), and the 7B pilot waits.
- **7B before Nov 30 is only possible on GCP** (an A100 in us-central1 at about $2.19/h spot, if the project has A100 quota) or by quantizing to fit an L4. AWS g6e cannot be launched.
- **For the 2027 horizon,** AWS stays attractive if a quota increase is granted. g6.xlarge spot in ap-south-1b ($0.326/h) is about 31% cheaper than GCP L4 spot ($0.474/h), and g6e.xlarge spot in ap-south-1a ($1.26/h) is about 32% below g6e on-demand. With that price, a 7B 200-step L40S run costs about 11 h × $1.26 ≈ **$14**, versus about $18 at earlier prices, which lowers the Scenario C 7B line from about $105 to about $85.
- If the user decides to request an increase (I did not request one), a sensible ask is G and VT on-demand 8 vCPU and spot 16 vCPU in **ap-south-1**, the default region with the cheapest g6 and g6e spot. That covers 2–4 single-GPU xlarge instances. Expect a day to over a week (Q2), so it helps the 2027 horizon, not Nov 30.
- **Security:** the CLI is using root-user credentials. AWS best practice is an IAM user or SSO role with least privilege for day-to-day CLI and Bedrock work. Moving off root is advisable before any launch scripts or Bedrock judge jobs run from this machine.
- Bedrock "ACTIVE" in the catalog means the models are offered in us-east-1. It does not prove the account can invoke them; that was not tested (no invocation). Nova judges stay the cheapest option (Q4).

### Gaps
- Whether Nova invocation is actually enabled for this account (model access, payment method) was not tested, by instruction.
- The GCP L4 and A100 quota in the team project is still unread (gcloud is not in WSL). This is now the deciding factor for Scenario B parallelism.
