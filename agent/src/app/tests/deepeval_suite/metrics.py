import os
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ToolCorrectnessMetric,
)
from langchain_openai import ChatOpenAI


class GroqDeepEvalLLM(DeepEvalBaseLLM):
    """Custom DeepEval LLM wrapper enforcing Groq-only models (llama-3.3-70b-versatile) for zero OpenAI cost evals."""

    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.model_name = model_name
        groq_key = os.getenv("GROQ_API_KEY", "").strip('"')
        if not groq_key:
            raise ValueError("GROQ_API_KEY must be set in environment for Groq evaluations.")
        self.model = ChatOpenAI(
            model=self.model_name,
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.0
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        res = self.model.invoke(prompt)
        return res.content if hasattr(res, "content") else str(res)

    async def a_generate(self, prompt: str) -> str:
        res = await self.model.ainvoke(prompt)
        return res.content if hasattr(res, "content") else str(res)

    def get_model_name(self):
        return self.model_name


groq_eval_llm = GroqDeepEvalLLM()

# 1. Faithfulness Metric (Ensures answer is grounded in retrieved context)
faithfulness_metric = FaithfulnessMetric(
    threshold=0.7,
    model=groq_eval_llm,
    async_mode=False,
    include_reason=True
)

# 2. Answer Relevancy Metric (Ensures answer directly addresses the prompt)
answer_relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7,
    model=groq_eval_llm,
    async_mode=False,
    include_reason=True
)

# 3. Contextual Precision & Recall Metrics (Evaluates search/retrieval quality)
contextual_precision_metric = ContextualPrecisionMetric(
    threshold=0.7,
    model=groq_eval_llm,
    async_mode=False,
    include_reason=True
)

contextual_recall_metric = ContextualRecallMetric(
    threshold=0.7,
    model=groq_eval_llm,
    async_mode=False,
    include_reason=True
)

# 4. Agent / Tool Correctness Metric (Evaluates agent tool selection and calls)
tool_correctness_metric = ToolCorrectnessMetric(
    threshold=0.7,
    model=groq_eval_llm,
    async_mode=False,
    include_reason=True
)


# Bundled list of all 4 requested metric suites for single-turn RAG & Tool testing
TARGET_DEEPEVAL_METRICS = [
    faithfulness_metric,
    answer_relevancy_metric,
    contextual_precision_metric,
    contextual_recall_metric,
    tool_correctness_metric,
]

