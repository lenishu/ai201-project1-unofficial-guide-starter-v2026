"""Questions fixed before retrieval calibration; expected facts come from corpus reading."""
QUESTIONS = [
    {"question": "How are juniors and seniors ordered in the housing lottery?", "expects": "credit hours"},
    {"question": "How long is the lunch wait at Kestrel Commons between 12:15 and 1:00?", "expects": "20 to 25"},
    {"question": "What happens to dining dollars left at the end of spring?", "expects": "May"},
    {"question": "Who must a student contact first for a grade appeal, and within how many days?", "expects": "fifteen"},
    {"question": "How far ahead can group study rooms be booked?", "expects": "two weeks"},
]
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]

def answered() -> list[dict]:
    return [q for q in QUESTIONS if q.get("question", "").strip()]
