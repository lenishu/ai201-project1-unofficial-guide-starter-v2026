# Unit 1 development notes

## Setup and corpus selection

Selected `campus_life`: 88 short student posts about a fictional university. Read the add/drop, dining dollars, grade appeals, declaring a major, housing lottery, Kestrel Commons, and group-study-room documents. Short administrative posts hold their answer in a single paragraph; longer dining and housing posts contain several distinct topics.

The original chunker produces 88 chunks from these 88 documents. The special-activity command for `advice_threads` reports 26 chunks before modifications.

Python 3.11.15 is used in `.venv`. All seven pinned top-level packages import. The environment check passed all ten checks, including actual 384-dimensional MiniLM embeddings, a Chroma cosine-search round trip, and a real Gemini response. The embedding archive was extracted into the ignored project cache because normal extraction encountered Windows directory permissions. `store.py` now uses this project-local model cache.

AI assistance: Codex performed setup and implementation at the student's request. Personal acceptance criteria were requested from the student; the student asked for AI suggestions. The README must disclose this rather than claim unaided authorship.
