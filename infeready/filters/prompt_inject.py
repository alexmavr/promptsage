from ..infeready import Filter
import requests
import os

class PromptInjectionDetectedError(Exception):
    def __init__(self, scores: dict):
        self.scores = scores

class PromptInject(Filter):
    def __init__(self, type: str, config: dict = {}):
        self.type = type
        if type == "llm-guard":
            # Assumes llm-guard is running as a container
            if "LLM_GUARD_URL" not in config:
                config["LLM_GUARD_URL"] = os.getenv("LLM_GUARD_URL", "http://localhost:8000")
            if "LLM_GUARD_API_KEY" not in config:
                config["LLM_GUARD_API_KEY"] = os.environ["LLM_GUARD_API_KEY"]
            self.config = config
        else:
            raise ValueError(f"Unknown prompt inject type: {type}")

    def filter(self, str_prompt: str) -> str:
        response = requests.post(
            url=f'{self.config["LLM_GUARD_URL"]}/analyze/prompt',
            json={"prompt": str_prompt},
            headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.config["LLM_GUARD_API_KEY"]}',
            },
        )

        response_json = response.json()

        if not response_json["is_valid"]:
            scores = response_json["scanners"]
            raise PromptInjectionDetectedError(scores=scores)
        return str_prompt