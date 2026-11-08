# Vertex AI custom training image (1x L4). Python 3.12 + vLLM 0.22.1 + torch 2.11 (AgentTune's pins).
# Build context = project root:  docker build -f vertex/Dockerfile -t $IMAGE .
FROM vllm/vllm-openai:v0.22.1
WORKDIR /app
COPY vendor/AgentTune /app/vendor/AgentTune
RUN pip install --no-cache-dir -e /app/vendor/AgentTune trl peft datasets pandas
COPY sqlcf /app/sqlcf
COPY train.py evaluate.py /app/
COPY vertex/run.sh /app/run.sh
# Only what training/eval read: item files + the DBs they reference (built on CPU beforehand).
COPY data/train /app/data/train
COPY data/test /app/data/test
COPY data/sft.jsonl /app/data/sft.jsonl
ENV PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
ENTRYPOINT ["bash", "/app/run.sh"]
