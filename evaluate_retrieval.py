"""Retrospective LoCoMo-Refined retrieval ablation, never an official score.

The engine receives Add source messages, user_id/query/options/top_k only.
Evidence labels are read by this evaluator after retrieval. Exported answer
inputs contain no gold answer, evidence, category or dataset-specific hints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import shutil
import time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from adaptive_evidence.core import Config, MemoryStore, digest
from adaptive_evidence.encoder import BGEEncoder
from adaptive_evidence.remote_encoder import encoder_from_env


ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append(path, row):
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize(items):
    scored = [row for row in items if row["evidence_count"]]
    return {"questions": len(items), "evidence_questions": len(scored),
            "any_evidence_hit": statistics.mean(r["any_hit"] for r in scored) if scored else None,
            "all_evidence_hit": statistics.mean(r["all_hit"] for r in scored) if scored else None,
            "macro_evidence_recall": statistics.mean(r["recall"] for r in scored) if scored else None,
            "mean_chars": statistics.mean(r["chars"] for r in items),
            "mean_results": statistics.mean(r["returned"] for r in items),
            "median_search_ms": statistics.median(r["search_ms"] for r in items)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, help="Private KEY=value configuration file")
    parser.add_argument("--embedding-backend", choices=["dashscope", "bge"], default="dashscope")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "benchmarks/LoCoMo_refined/data/public")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--model", type=Path, default=ROOT / "MemoryBench-Shared/models/embeddings/bge-small-en-v1.5")
    parser.add_argument("--modes", nargs="+", default=["dense", "hybrid", "hybrid_window"])
    parser.add_argument("--context-chars", type=int, default=24000)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample-ids", type=Path, help="Frozen JSON list of qa_id values")
    parser.add_argument("--database", type=Path, help="Reuse an existing compatible public-only index")
    args = parser.parse_args()
    if args.env_file:
        from preflight import load_env
        load_env(args.env_file)
    args.output.mkdir(parents=True, exist_ok=True)
    config = Config(context_chars=args.context_chars)
    if args.limit < 0:
        parser.error("--limit must be non-negative")
    data = args.data_dir
    inputs = {name: sha(data / name) for name in ["conversations.jsonl", "questions.jsonl"]}
    if args.embedding_backend == "bge":
        encoder = BGEEncoder(str(args.model), args.device)
    else:
        import os
        if os.getenv("AE_EMBEDDING_BACKEND", "dashscope") != "dashscope":
            parser.error("DashScope evaluation requires AE_EMBEDDING_BACKEND=dashscope")
        encoder = encoder_from_env()
    protocol = {"kind": "retrospective_retrieval_only", "unseen_holdout": False,
                "data_sha256": inputs, "config": asdict(config), "top_k": args.top_k,
                "modes": args.modes, "limit": args.limit,
                "sample_ids_sha256": sha(args.sample_ids) if args.sample_ids else None,
                "source_sha256": {str(p.relative_to(Path(__file__).parent)): sha(p)
                                   for p in (Path(__file__).parent / "adaptive_evidence").glob("*.py")},
                "evaluation_script_sha256": sha(Path(__file__)),
                "embedding_backend": args.embedding_backend, "encoder_identity": encoder.identity,
                "model": str(args.model.resolve()) if args.embedding_backend == "bge" else "text-embedding-v4",
                "device": args.device if args.embedding_backend == "bge" else "provider",
                "source_policy": "raw message text, speaker, date string; supplied image captions/query are marked as such",
                "evidence_metric": "full source message span present, not merely a matching chunk ID",
                "answer_model": None, "judge_model": None, "official_score": False}
    manifest_path = args.output / "manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8")) != protocol:
        raise ValueError("Output belongs to a different frozen protocol; use a new directory")
    manifest_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    snapshot = args.output / "source_snapshot"
    snapshot.mkdir(exist_ok=True)
    for source in (Path(__file__).parent / "adaptive_evidence").glob("*.py"):
        target = snapshot / "adaptive_evidence" / source.name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, target)
    shutil.copyfile(__file__, snapshot / Path(__file__).name)
    result_path = args.output / "retrieval_metrics.jsonl"
    done = {(r["mode"], r["qa_id"]) for r in rows(result_path)} if result_path.exists() else set()
    store = MemoryStore(args.database or args.output / "public_memory.sqlite3", encoder, config)
    question_rows = rows(data / "questions.jsonl")
    if args.sample_ids:
        sample_ids = json.loads(args.sample_ids.read_text(encoding="utf-8"))
        if not isinstance(sample_ids, list) or len(sample_ids) != len(set(sample_ids)):
            raise ValueError("Sample IDs must be a unique list")
        selected_ids = set(sample_ids)
        question_rows = [q for q in question_rows if q["qa_id"] in selected_ids]
        if len(question_rows) != len(selected_ids):
            raise ValueError("Unknown sample IDs")
    if args.limit:
        question_rows = question_rows[:args.limit]
    wanted = {r["sample_id"] for r in question_rows}
    question_groups = defaultdict(list)
    for row in question_rows:
        question_groups[row["sample_id"]].append(row)
    started = time.monotonic()
    for conversation in rows(data / "conversations.jsonl"):
        name = conversation["sample_id"]
        if name not in wanted:
            continue
        user = "public-diagnostic:" + name
        source_map, source_lengths = {}, {}
        # All memory ingestion precedes every query for this scope.
        for session in conversation["sessions"]:
            request = f"{name}:session:{session['session_index']}"
            messages = []
            for position, message in enumerate(session["messages"]):
                content = f"[{session['date_time']}] {message['speaker']}: {message['text']}"
                if message.get("blip_caption"):
                    content += "\n[Provided image caption] " + message["blip_caption"]
                if message.get("query"):
                    content += "\n[Provided image query] " + message["query"]
                source = digest([user, request, position])
                source_map[source] = message["dia_id"]
                source_lengths[source] = len(content)
                messages.append({"role": message["role"], "content": content})
            store.add(user_id=user, request_id=request, session_id=str(session["session_index"]), messages=messages)
        index = store.index(user)
        chunk_map = {r["id"]: r for r in index.rows}
        print(f"indexed {name}: {len(index.rows)} chunks; elapsed={time.monotonic()-started:.1f}s", flush=True)
        for question in question_groups[name]:
            for mode in args.modes:
                key = (mode, question["qa_id"])
                if key in done:
                    continue
                before = time.monotonic()
                results = store.search(user_id=user, query=question["question"], top_k=args.top_k, mode=mode)
                elapsed = (time.monotonic() - before) * 1000
                found_spans = defaultdict(list)
                for hit in results:
                    chunk = chunk_map[hit["id"]]
                    found_spans[chunk["source_id"]].append((chunk["start"], chunk["end"]))
                found = set()
                for source, spans in found_spans.items():
                    end = 0
                    for left, right in sorted(spans):
                        if left > end:
                            break
                        end = max(end, right)
                    if end >= source_lengths[source]:
                        found.add(source_map[source])
                gold = set(question["evidence"])
                metric = {"mode": mode, "qa_id": question["qa_id"], "sample_id": name,
                          "category": question["category"], "evidence_count": len(gold),
                          "any_hit": bool(found & gold), "all_hit": bool(gold) and gold <= found,
                          "recall": len(found & gold) / len(gold) if gold else None,
                          "returned": len(results), "chars": sum(len(r["content"]) for r in results),
                          "search_ms": elapsed}
                # Candidate input files deliberately contain no label/evidence fields.
                append(args.output / f"answer_inputs_{mode}.jsonl",
                       {"id": question["qa_id"], "question": question["question"],
                        "speaker_1_name": conversation["speaker_a"],
                        "speaker_2_name": conversation["speaker_b"],
                        "retrieved_context": "\n\n".join(r["content"] for r in results)})
                append(result_path, metric)
                done.add(key)
            if len(done) % 150 == 0:
                print(f"completed={len(done)}/{len(question_rows)*len(args.modes)}", flush=True)
    metrics = rows(result_path)
    groups = defaultdict(list)
    for row in metrics:
        groups[row["mode"]].append(row)
    summary = {"protocol": protocol, "by_mode": {name: summarize(items) for name, items in groups.items()},
               "by_mode_category": {mode: {category: summarize([r for r in items if r['category'] == category])
                                            for category in sorted({r['category'] for r in items})}
                                    for mode, items in groups.items()},
               "elapsed_seconds_this_invocation": time.monotonic()-started}
    if hasattr(encoder, "usage"):
        summary["embedding_usage_this_process"] = encoder.usage()
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary["by_mode"], indent=2), flush=True)
    if hasattr(encoder, "close"):
        encoder.close()


if __name__ == "__main__":
    main()
