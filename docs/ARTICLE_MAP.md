# Article → code map

Companion to the full field guide: [`GUIDE.md`](GUIDE.md). Each row links to the
relevant guide section and the code that implements it.

| Article section | Scaffold location |
|---|---|
| [§1 Reliable / Interpretable / Steerable](GUIDE.md#1-reframe-the-poc-before-you-write-a-single-prompt) | `README.md`, response `trace` fields |
| [§2 Stakeholder confidence](GUIDE.md#2-stakeholder-confidence-map--design-for-the-people-who-must-say-yes) | Eval scorecard + refusal/HITL demos |
| [§3 Use-case selection](GUIDE.md#3-choose-the-right-use-case--the-highest-leverage-sa-decision) | Retail bank staff assist (not decision replacement) |
| [§4 Gates A–D](GUIDE.md#4-poc-operating-model--timebox-roles-and-governance-lightweight) | Use golden set + audit as Gate C evidence |
| [§5 Control plane](GUIDE.md#5-reference-architecture-for-a-high-assurance-poc) | `src/anz_fs_poc/pipeline.py` + `control_plane/` |
| [§5.1 Output validation / degraded mode](GUIDE.md#5-reference-architecture-for-a-high-assurance-poc) | `control_plane/validator.py`, `Outcome.DEGRADED` in `pipeline.py` |
| [§5.3 Deterministic vs LLM](GUIDE.md#53-separation-of-concerns-that-impresses-arbs) | `deterministic/fees.py` |
| [§6 Corpus contract](GUIDE.md#6-data-and-knowledge-design--where-reliability-is-won-or-lost) | `docs/CORPUS_CONTRACT.md`, `data/corpus/` |
| [§6.3 “I don’t know”](GUIDE.md#63-the-i-dont-know-path-is-a-feature) | Retrieval threshold refuse path (`boundary-002` golden case) |
| [§7 Evaluation harness](GUIDE.md#7-evaluation-harness--the-heart-of-a-credibility-poc) | `eval/`, `data/golden_set/`, `scripts/run_eval.py` (threshold-gated) |
| [§8 Red team](GUIDE.md#8-safety-and-red-team-exercises-for-the-poc-lightweight-but-real) | Adversarial cases in `cases.json` |
| [§9 Interpretability UX](GUIDE.md#9-interpretability-design--make-the-system-explainable-in-the-ui) | Citations + system notes + prompt-pack hash in response/audit |
| [§10 Steerability layers](GUIDE.md#10-steerability-controls--policy-as-code-not-as-hope) | Policy → output validation → HITL; versioned `prompt_pack.py` |
| [§11 Residency checklist](GUIDE.md#11-security-privacy-and-residency--poc-checklist-for-anz) | `POC_REGION` + provider abstraction; redacted audit log |
| [§12 Worked example](GUIDE.md#12-worked-example--5-week-poc-outline-retail-bank-staff-policy--complaints-assist) | Same retail-bank staff assist scenario |

Public repository: <https://github.com/PITCHUMANIS/anz-fs-ai-poc-skeleton>
