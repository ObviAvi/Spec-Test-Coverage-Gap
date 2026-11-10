"""One structured-output call per provider. Every client returns (parsed_json, meta)."""

import json

from dotenv import load_dotenv

from . import config

load_dotenv(config.ROOT / ".env")


class LLMError(Exception):
    pass


class AnthropicClient:
    def __init__(self, model: str, effort: str = "high", **_):
        import anthropic

        self.model, self.effort = model, effort
        self.client = anthropic.Anthropic(max_retries=4)

    def complete_json(self, prompt: str, schema: dict) -> tuple[dict, dict]:
        resp = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": prompt}],
        )
        if resp.stop_reason == "refusal":
            raise LLMError(f"refused: {getattr(resp.stop_details, 'category', None)}")
        if resp.stop_reason == "max_tokens":
            raise LLMError("hit max_tokens")
        text = next(b.text for b in resp.content if b.type == "text")
        # served_model differs from model when the server-side fallback answered instead
        meta = {"served_model": resp.model, "request_id": resp._request_id,
                "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        return json.loads(text), meta


class OpenAIClient:
    def __init__(self, model: str, reasoning_effort: str | None = None, **_):
        import openai

        self.model, self.reasoning_effort = model, reasoning_effort
        self.client = openai.OpenAI(max_retries=4)

    def complete_json(self, prompt: str, schema: dict) -> tuple[dict, dict]:
        kwargs = {"reasoning": {"effort": self.reasoning_effort}} if self.reasoning_effort else {}
        resp = self.client.responses.create(
            model=self.model,
            input=prompt,
            text={"format": {"type": "json_schema", "name": "output", "schema": schema, "strict": True}},
            **kwargs,
        )
        if resp.status != "completed":
            raise LLMError(f"status {resp.status}: {resp.incomplete_details}")
        meta = {"served_model": resp.model,
                "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        return json.loads(resp.output_text), meta


PROVIDERS = {"anthropic": AnthropicClient, "openai": OpenAIClient}


def make_client(judge_name: str):
    cfg = dict(config.JUDGES[judge_name])
    return PROVIDERS[cfg.pop("provider")](**cfg)
