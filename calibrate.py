"""Record Unit 1 retrieval distances without making generation calls."""
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import config
from questions import QUESTIONS, OUT_OF_SCOPE
from store import search


def main():
    records = []
    for in_corpus, questions in [(True, [q['question'] for q in QUESTIONS]), (False, OUT_OF_SCOPE)]:
        for question in questions:
            hits = search(question)
            record = {'question': question, 'in_corpus': in_corpus, 'best_distance': hits[0].distance if hits else None, 'results': [asdict(h) for h in hits]}
            records.append(record)
            print(f"{'IN ' if in_corpus else 'OUT'} {record['best_distance']:.6f} {question}", flush=True)
    output = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'corpus': config.CORPUS, 'embedding_model': config.EMBEDDING_MODEL, 'top_k': config.TOP_K, 'records': records}
    config.RESULTS_DIR.mkdir(exist_ok=True)
    (config.RESULTS_DIR / 'unit1_retrieval.json').write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
