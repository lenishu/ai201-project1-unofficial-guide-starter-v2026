# Acceptance criteria — The Unofficial Guide

These targets were fixed before retrieval calibration and Unit 2 evaluation. Criteria 1–3 are provided by the course. Criteria 4–5 and the explanations were drafted with AI assistance at the student's request; they need the student's review before submission.

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.

**Why this target:** The selected posts usually state a concrete answer in one paragraph. Four successes allow one difficult phrasing mismatch, while three would make the app unreliable for routine questions.

**How to check:** For each entry in `questions.QUESTIONS`, inspect the top five chunks. Count a success only when a chunk contains the fact required by the question, not merely the same topic.

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** Every retrieved chunk already carries its filename, so no substantive answer should omit attribution. Students must be able to distinguish a sourced report from unsupported advice.

**How to check:** All five generated test answers must name at least one actual retrieved filename. A gate refusal is an abstention, not a factual answer; do not invent a citation for it.

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.

**Why this target:** The corpus concerns campus experiences, so unrelated questions should normally be rejected. Allowing one ambiguous semantic match acknowledges that similarity is not a proof of coverage, but allowing two would be too many unsupported requests reaching the model.

**How to check:** Use the five questions in `OUT_OF_SCOPE`. Count only refusals made before generation; the model's own refusal does not count as a gate success.

## 4. Chunks are understandable in isolation

At least 9 of 10 sampled chunks must identify their topic and contain at least one complete, uncut factual sentence that can be understood without an adjacent chunk.

**Why this target:** These short posts often name a course, residence, or dining hall only in their heading. A high target tests whether splitting preserves that context; allowing one failure exposes an edge case without accepting widespread fragments.

**How to check:** Sort documents by filename and preserve chunk order. For N chunks, inspect indices floor(i × (N − 1) / 9), for i = 0 through 9. Check topic identification and a complete self-contained factual sentence; both must pass.

## 5. Answers contain supported facts

At least 4 of the 5 test answers must contain the expected fact specified in `questions.py`, and every factual claim in each of those successful answers must be supported by the documents it cites.

**Why this target:** A filename alone does not establish correctness. Campus deadlines and eligibility rules include qualifications that a plausible-sounding summary can lose; four fully supported answers is more useful than five fluent answers with invented details.

**How to check:** Check the `expects` phrase case-insensitively, then read the cited documents and verify every factual claim. A phrase match with a wrong qualification fails. Keep the original targets unchanged for Unit 2, recording any necessary clarification beneath them.
