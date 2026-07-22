# ESP Pilot Annotation Guidelines v0

These labels validate the candidate-retrieval protocol; they are not a substitute for the blinded human study required for a paper claim.

For each JSONL item, read `frame.scope` in the context of `source_text`. Do not consult another annotator's labels.

Record one JSON object per line with these fields:

- `item_id`: copied exactly.
- `cue_valid`: `yes` only when the matched cue expresses epistemic uncertainty or evidential qualification in this occurrence; otherwise `no`.
- `scope_text`: the smallest complete proposition whose commitment is modified by the cue. Copy a contiguous source substring where possible; use an empty string when `cue_valid=no`.
- `strength`: one of `unknown`, `possible`, `suggestive`, `likely`, `not_epistemic`.
- `attribution`: `authors`, `prior_work`, `other_actor`, or `unclear`.
- `retain_in_lay_rewrite`: `yes` when dropping or strengthening the qualification would materially change the scientific claim; `no` when the cue is non-epistemic or dispensable without changing commitment.
- `confidence`: integer 1--3.
- `note`: concise reason, especially for invalid cues or non-contiguous scope.

Strength definitions:

- `unknown`: the source explicitly says whether/why/how something holds is unknown or unclear.
- `possible`: the proposition is presented as a possibility or capability, typically `may`, epistemic `might`, or epistemic `could`.
- `suggestive`: evidence or results support but do not establish the proposition (`suggest`, `suggests`).
- `likely`: the source presents the proposition as probable (`likely`).
- `not_epistemic`: ability, permission, deontic use, month/name substring, or another non-epistemic reading.

Annotate the linguistic commitment in the source, not whether the scientific claim is actually true. A cue is not automatically valid merely because it matched the frozen lexicon. Do not rewrite the proposition into simpler language during annotation.
