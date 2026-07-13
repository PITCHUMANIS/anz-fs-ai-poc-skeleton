# CORPUS CONTRACT (synthetic)

```
CORPUS CONTRACT
---------------
Sources:           data/corpus/*.md (synthetic retail bank documents)
Owners:            PoC architect (example only)
Classification:    internal / synthetic — NOT real bank content
Allowed purposes:  staff assist / contact-centre support / training demos
Forbidden content: real TFN, PAN, customer PII, employer documents
Refresh cadence:   manual (repo updates)
Chunking rules:    heading-aware sections (see rag/corpus.py)
Access model:      role stub: agent | team_leader | admin
Citation standard: doc_id + section heading + chunk preview
Jurisdiction:      AU (illustrative)
Effective dating:  metadata on each document
```

## Documents in this PoC

| doc_id | Title | Purpose |
|---|---|---|
| `HL-PG-4.2` | Home Loan Product Guide (synthetic) | Product Q&A |
| `CHP-AU-2.4` | Complaints Handling Procedure (synthetic) | Procedure Q&A |
| `FAC-2026` | Fees & Charges Schedule (synthetic) | Fee explanations (amounts still resolved via deterministic table) |

## Rules

1. Only these sources may be retrieved.
2. Dollar amounts for product fees must come from `deterministic/fees.py`, not free-form model invention.
3. No web browsing / external tools in this skeleton.
