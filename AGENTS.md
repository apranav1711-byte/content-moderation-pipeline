# Moderation Pipeline — Project Notes

## Why this exists

The command that started this project was: "start building it and also create a agent.md file like what all its doing for what command i gave and explain me everything line by line."

This is an educational moderation application. Its first version accepts text, asks a pretrained transformer model for safety scores, and uses transparent rules to return **allow**, **review**, or **block**. It is not a final automated judge; uncertain content goes to human review.

## Current scope

- Text only; image moderation comes after text evaluation is working.
- Pretrained `unitary/toxic-bert`; no model training.
- No database and no saved submissions.
- One browser page and one API endpoint.

## Files and their roles

| File | What it does |
| --- | --- |
| `main.py` | Runs the web API, loads the model, and applies the policy. |
| `index.html` | The small page where a user pastes text and sees a result. |
| `test_policy.py` | Checks that the policy chooses the intended decision for example scores. |
| `requirements.txt` | Lists the Python packages the app needs. |

## Commands

Open PowerShell in this folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` in a browser. The first moderation request downloads the pretrained model, so it needs internet access and can take a few minutes.

To check the decision policy:

```powershell
python test_policy.py
```

## Request flow, from scratch

1. A visitor types text in `index.html` and clicks **Check content**.
2. Browser JavaScript sends that text to `POST /moderate/text`.
3. FastAPI receives it in `main.py` and rejects empty or overly long inputs.
4. The transformer estimates labels such as `toxic` and `threat`.
5. `make_decision` compares the scores against our written thresholds.
6. The API sends JSON back to the browser, which shows it.

## The policy in plain English

- A threat score of 0.70 or more is blocked.
- A `toxic` score of 0.90 or more is blocked.
- `toxic` from 0.55 to 0.8999 is sent to a human reviewer.
- Everything else is allowed.

These are initial guesses, not proven settings. Later, we will measure precision, recall, and false-positive rate on labelled data, then adjust the thresholds based on evidence.

## How to explain this in an interview

"I separated prediction from policy. The model only estimates risk scores. A small, auditable policy converts those scores into allow, review, or block. I reserve a review band for uncertainty because false positives matter in moderation. I will evaluate thresholds with precision, recall, and false-positive rate instead of choosing them by intuition."

## Next milestones

1. Run the app and inspect raw scores with safe example text.
2. Add a labelled evaluation dataset and calculate precision, recall, F1, and false-positive rate.
3. Tune the thresholds using those results.
4. Add a separate image-moderation endpoint and upload UI.
