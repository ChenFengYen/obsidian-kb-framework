# Paper processing module

This optional module stores source PDFs, structured source notes, and extracted assets under `OV-Papers`.

## Principles

- Treat the PDF as the source of truth.
- Preserve title, author, year, identifier, and page provenance when available.
- Use `null` for unknown structured scalar values rather than plausible guesses.
- Keep supplementary material separate from the main paper record.
- Store extracted figures with source page and caption provenance.
- Mark AI-generated summaries and metadata as unreviewed until verified.
- Do not inject conceptual links solely from keyword matches.

## Suggested layout

```text
OV-Papers/
  PDF-raw/       source files
  PDF-md/        structured source notes
  PDF-assets/    extracted figures and tables
  Final-md/      reviewed notes when the workflow uses a review stage
  scripts/       optional processing tools
```

## Workflow

1. Confirm the source file and identifier.
2. Extract text or figures without overwriting the source.
3. Build a structured note with page-level provenance.
4. Validate citations, formulas, identifiers, and missing values.
5. Present the result for review before promoting it to durable knowledge.

Automation should prepare evidence and deterministic metadata. Interpretation, conceptual linking, and research claims require contextual review.
