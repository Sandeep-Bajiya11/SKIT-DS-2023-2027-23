# Audio-Language Model (ALM): Listen, Think and Understand

**Project ID:** `SKIT-DS-2023-2027-23`  
**Team:** DS-B, Swami Keshvanand Institute of Technology, Management & Gramothan, Jaipur

## Project goal
Build and evaluate a modular audio-language model that connects audio perception, cross-modal alignment, and language-model reasoning for tasks such as speech understanding and spoken question answering.

## Proposed stages
1. **Listen:** audio loading, preprocessing, and a baseline audio encoder.
2. **Think:** audio-token projection/alignment and sequence handling.
3. **Understand:** language-model integration and task-specific inference.
4. **Evaluate:** dataset documentation, reproducible evaluation, and metrics such as WER where appropriate.
5. **Demo:** API or Gradio interface after the core pipeline is working.

## Team
- Sandeep Mohanlal Bajiya — `@Sandeep-Bajiya11`
- Samyak Jain — `@Sam-Yak19`
- Tejanshu Sharma — `@Tezu17`
- Naresh Charrang — `@Naresh834`

## Repository map
- `src/` — project implementation
- `tests/` — tests
- `docs/` — architecture, decisions, setup notes
- `data/` — local datasets (not committed; see `.gitignore`)
- `notebooks/` — exploratory notebooks, if needed
- `weekly_reports/` — automated weekly Form-3 PDF reports
- `generate_report.py` — report generator
- `.github/workflows/auto_weekly_report.yml` — scheduled/manual report workflow

## Getting started
Python 3.10+ is recommended for the initial lightweight project tooling. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the report generator locally:

```bash
python generate_report.py weekly
```

The script supports `weekly`, `monthly`, and `final` report scopes. Weekly reporting uses the college week (Friday through Thursday, India time).

## Git workflow
- Each member works on their own branch: `sandeep/...`, `samyak/...`, `tejanshu/...`, `naresh/...`.
- Commit small, real changes with descriptive messages.
- Push branches and open pull requests into `main`.
- Merge only after review/tests pass.
- Never commit passwords, API keys, private tokens, large datasets, model weights, or personal data.

## Current status
This is a starter scaffold. Replace TODO notes with verified design choices, dataset sources/licences, experiments, results, and implementation details as the team develops the project. Do not claim a feature works until it has been implemented and tested.
