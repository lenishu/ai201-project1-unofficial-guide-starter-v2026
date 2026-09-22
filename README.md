# The Unofficial Guide

# Unit 1

## What This Does

This command-line app searches 88 fictional campus-life posts supplied by CodePath. It answers questions about housing, dining, courses, and campus procedures using local MiniLM embeddings and a Chroma vector store. A cosine-distance gate rejects unrelated questions before Gemini runs, and Gemini receives only retrieved excerpts with filenames. The posts are course material, not verified policies for a real university.

Run with Python 3.11–3.13: create a virtual environment, install `requirements.txt`, copy `.env.example` to `.env`, and set `GEMINI_API_KEY` locally. Then run `python app.py index` and `python app.py ask "Is the housing lottery random?"`. Use `python app.py ask` for an interactive session. See the unchanged `RUNNING.md` for all commands. Never commit `.env`.

## Chunking Strategy

**Chunk size:** One body paragraph, with a 420-character soft body target for unusually long paragraphs. The repeated title is additional context, so 420 is not a hard total-length limit. **Overlap:** Zero body characters; the document heading repeats in each chunk.

The original 800-character windows produced 88 chunks from 88 documents (average 317, shortest 178, longest 549). In the source documents, the 183 body paragraphs have median length 112 and maximum length 373. A paragraph is therefore a natural unit: dining wait times and opening hours become separate chunks, while a short administrative explanation stays whole. The 420 target accommodates the longest observed paragraph with a small margin. Longer paragraphs split at sentence boundaries, and a single overlong sentence remains whole rather than being truncated. This trades some cross-paragraph context for more focused retrieval; repeating the title preserves which hall or course each paragraph describes.

The provided corpus is already free of navigation and ads. Ingestion normalizes line endings, repeated blank lines, spaces, and tabs while preserving paragraph boundaries and source filenames. It does not claim to clean arbitrary scraped HTML.

Current output: 183 chunks, 167 characters on average (shortest 63, longest 397), produced by chunker.py::split_documents.

## Sample Chunks

### Chunk 1

Source: `admin_add_drop_deadline.txt#0`. Produced by: `chunker.py::split_documents`.

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

### Chunk 2

Source: `course_cs_340_exams.txt#1`. Produced by: `chunker.py::split_documents`.

```text
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

### Chunk 3

Source: `course_phys_130_workload.txt#0`. Produced by: `chunker.py::split_documents`.

```text
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

### Chunk 4

Source: `dining_verrill_street_grill_followup.txt#1`. Produced by: `chunker.py::split_documents`.

```text
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

### Chunk 5

Source: `housing_morrow_house.txt#1`. Produced by: `chunker.py::split_documents`.

```text
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

## Sample Answer

**Question:** How are juniors and seniors ordered in the housing lottery?

**Answer (actual Gemini output):**

```text
Juniors and seniors are ordered by accumulated credit hours first, with a random tie-break used only in the case of a tie (admin_housing_lottery.txt).
```

**Source cited in the answer:** `admin_housing_lottery.txt`.

**Relevance cutoff:** `0.51` cosine distance, with lower meaning more similar. The gate accepts only when the best distance is strictly below the cutoff. **Top-k:** `5`.

| Question | In corpus? | Best distance |
|---|---|---:|
| How are juniors and seniors ordered in the housing lottery? | Yes | 0.224975 |
| How long is the lunch wait at Kestrel Commons between 12:15 and 1:00? | Yes | 0.163408 |
| What happens to dining dollars left at the end of spring? | Yes | 0.234627 |
| Who must a student contact first for a grade appeal, and within how many days? | Yes | 0.204793 |
| How far ahead can group study rooms be booked? | Yes | 0.216248 |
| What is the capital of Mongolia? | No | 0.787250 |
| How do I change the oil in a diesel engine? | No | 0.922791 |
| Who won the 1994 World Cup? | No | 0.847429 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.848693 |
| How do I write a for loop in Rust? | No | 0.859783 |

The in-scope range was 0.163408–0.234627; the out-of-scope range was 0.787250–0.922791. The midpoint between the worst in-scope match and nearest out-of-scope match is approximately 0.511, so the chosen 0.51 cutoff sits inside the gap. A much lower cutoff would start rejecting supported questions; a much higher one would admit unrelated questions. These ten calibration examples do not establish performance on unseen questions.

I retained top-k 5. Inspection of the first three questions found the answer in their best match, although lower-ranked housing and dining matches were sometimes only loosely related. The grounding instruction therefore explicitly requires preserving numbers and qualifications, matching the named place or procedure, citing the exact supporting filename for each claim, and reporting conflicting sources rather than merging them. It also treats excerpts as data rather than instructions. This is a prompt safeguard, not a guarantee that every generated answer is correct.

All five out-of-scope questions returned `I don't have enough information about that.` through the actual pipeline, with **zero generation calls**. The complete retrieved chunks and distances are saved in `results/unit1_retrieval.json`; the real sample answer, assembled prompt, and refusal outcomes are in `results/unit1_answers.json`. Reproduce distances with `python calibrate.py` after indexing, and reproduce the answer with `python app.py ask "How are juniors and seniors ordered in the housing lottery?" --show-prompt`.

## How I Used AI

1. I asked Codex to complete the project in `Desktop/codepath/assignment-1`. It inspected the starter and corpus, proposed paragraph-based chunking with repeated titles, implemented it, and ran regression tests. I supplied the location and Gemini key; I have not manually changed the implementation. The baseline used one fixed window per post; the resulting implementation separates body paragraphs while retaining their heading.
2. When Codex asked for my own chunk-quality and answer-quality criteria, I asked it to suggest them. It proposed measurable targets and added explicit sampling and checking procedures. I have not independently rewritten those suggestions. Criteria 4–5 and this write-up are AI-assisted drafts for my review; the course asks students to author those criteria themselves.

The model cache is kept in the ignored `.cache` folder. Nine focused regression tests pass (`python -m unittest test_project.py -v`). These are implementation checks, not the three-run Unit 2 evaluation.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
