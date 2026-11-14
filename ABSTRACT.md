# When Execution Success Lies: counterfactual-database rewards for a small SQL agent

Lexsi hackathon · Track 3 · PS #6 (data and database agents) + PS #9 (reward design and reward-hacking defences)

Text-to-SQL agents trained with reinforcement learning usually get rewarded when their answer matches the gold answer on one database. A wrong query can match by luck, and then the reward teaches the luck. Our defence is to run the agent's final query on a few extra copies of the database as well, and to pay only if it is right on all of them. The agent never sees these copies, and code builds each one to expose a particular kind of bug.

We first checked the reward itself, without training anything. On a single database, almost a third of realistic buggy queries get paid. With the copies, about one in six do, and queries that try to game the reward almost never get through. No correct query was rejected. Two public SQL rewards, AgentTune's and SkyRL-SQL's, have the same holes, and we patched AgentTune's. The problem is not specific to our data: on Spider, between 8 and 15 percent of the answers that eight published systems get right fail on Zhong et al.'s test-suite databases.

We then trained Tiny Aya Global (3.35B) with GRPO, once with each reward. On our own test set the stricter reward did not help. Logging every rollout shows why: the two rewards disagreed on only about 7 percent of them, because our training questions were too easy for lucky answers to come up. On Spider, which we did not build, the result goes the other way. The model trained with the copies keeps more answers that hold up on the test-suite databases, and gets fewer lucky passes, than the model trained on one database. That is one training run per reward, so we treat it as a hint and are adding a second seed.

We also tried distilling Cohere Command A and using the copies to filter its answers. The small model got worse, because it picked up a habit of adding a filter that the copies could not catch. Self-hosted, our model is far cheaper per query than Command A, but it is much less accurate and does not replace it.

We release the data generator, the databases, every rollout with its reward on each database, a browser demo, and a script that re-derives every number. The reward audit is the main result. The training results are reported as they came out.
