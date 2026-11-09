"""Small, explainable text-moderation demo."""

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

MODEL_NAME = "unitary/toxic-bert"
BASE_DIR = Path(__file__).parent

app = FastAPI(title="Moderation Pipeline")


class TextSubmission(BaseModel):
    text: str = Field(min_length=1, max_length=5_000)


@lru_cache
def get_classifier():
    """Load the model only on the first request, not every request."""
    from transformers import pipeline

    return pipeline("text-classification", model=MODEL_NAME, top_k=None)


def make_decision(scores: dict[str, float]) -> tuple[str, str]:
    """Turn model probabilities into a clear product decision."""
    threat = scores.get("threat", 0.0)
    # This model calls the label "toxic"; accept "toxicity" too so the rule is clear.
    toxicity = scores.get("toxic", scores.get("toxicity", 0.0))

    if threat >= 0.70:
        return "block", "Threat score is at least 0.70."
    if toxicity >= 0.90:
        return "block", "Toxicity score is at least 0.90."
    if toxicity >= 0.55:
        return "review", "Toxicity is uncertain, so a human should review it."
    return "allow", "No score crossed the review threshold."


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/moderate/text")
def moderate_text(submission: TextSubmission):
    try:
        raw_scores = get_classifier()(submission.text)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="The moderation model could not be loaded. Check your internet connection on first run.",
        ) from error

    # For one text, Transformers returns [[{label, score}, ...]].
    # We unwrap that outer list, then make a simple label-to-score dictionary.
    predictions = raw_scores[0] if raw_scores and isinstance(raw_scores[0], list) else raw_scores
    scores = {item["label"].lower(): round(item["score"], 4) for item in predictions}
    decision, reason = make_decision(scores)
    return {"decision": decision, "reason": reason, "scores": scores}
