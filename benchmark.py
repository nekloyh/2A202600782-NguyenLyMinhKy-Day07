#!/usr/bin/env python3
"""Run local + gemini providers on new data corpus. Save to report/."""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(override=False)

import re as _re

from src.chunking import RecursiveChunker
from src.embeddings import GeminiEmbedder, LocalEmbedder
from src.models import Document
from src.store import EmbeddingStore

# ─── Corpus ──────────────────────────────────────────────────────────────────

CORPUS = [
    {
        "path": "data/deep_learning_history.md",
        "id": "deep_learning_history",
        "title": "Lịch sử Deep Learning",
        "meta": {"category": "deep_learning_history", "language": "vi", "difficulty": "beginner"},
    },
    {
        "path": "data/gemini_live_api_cookbook.md",
        "id": "gemini_live_api_cookbook",
        "title": "Gemini Live API Cookbook",
        "meta": {"category": "api_cookbook", "language": "en", "difficulty": "advanced"},
    },
    {
        "path": "data/logical_thinking_and_problem_solving_in_AI.md",
        "id": "logical_thinking",
        "title": "Logical Thinking & Problem-Solving in AI",
        "meta": {"category": "ai_problem_solving", "language": "vi", "difficulty": "intermediate"},
    },
    {
        "path": "data/rag_system_design.md",
        "id": "rag_system_design",
        "title": "RAG System Design",
        "meta": {"category": "rag_design", "language": "en", "difficulty": "intermediate"},
    },
    {
        "path": "data/vector_store_notes.md",
        "id": "vector_store_notes",
        "title": "Vector Store Notes",
        "meta": {"category": "vector_store", "language": "en", "difficulty": "beginner"},
    },
    {
        "path": "data/vi_retrieval_notes.md",
        "id": "vi_retrieval_notes",
        "title": "Ghi chú Retrieval",
        "meta": {"category": "retrieval", "language": "vi", "difficulty": "beginner"},
    },
    {
        "path": "data/python_intro.txt",
        "id": "python_intro",
        "title": "Python Intro",
        "meta": {"category": "programming", "language": "en", "difficulty": "beginner"},
    },
    {
        "path": "data/customer_support_playbook.txt",
        "id": "customer_support_playbook",
        "title": "Customer Support Playbook",
        "meta": {"category": "support", "language": "en", "difficulty": "beginner"},
    },
    {
        "path": "data/chunking_experiment_report.md",
        "id": "chunking_experiment_report",
        "title": "Chunking Experiment Report",
        "meta": {"category": "chunking", "language": "en", "difficulty": "intermediate"},
    },
]

# ─── Benchmark queries ────────────────────────────────────────────────────────

QUERIES = [
    {
        "id": "Q1",
        "query": "Lịch sử Deep Learning bắt đầu từ khi nào và ai là những người tiên phong?",
        "gold_doc": "deep_learning_history",
        "gold_answer": "Từ 1940s (McCulloch & Pitts); backprop 1986 Rumelhart; LeNet 1989 LeCun; Transformer 2017.",
        "filter": {"category": "deep_learning_history"},
    },
    {
        "id": "Q2",
        "query": "How do I create a live audio session with Gemini Live API and handle voice activity detection?",
        "gold_doc": "gemini_live_api_cookbook",
        "gold_answer": "Use GenAI SDK live_connect, set audio modalities, VAD handles turn-taking automatically.",
        "filter": {"category": "api_cookbook"},
    },
    {
        "id": "Q3",
        "query": "MECE framework là gì và áp dụng như thế nào trong AI problem solving?",
        "gold_doc": "logical_thinking",
        "gold_answer": "MECE = Mutually Exclusive Collectively Exhaustive, phân rã bài toán không trùng lặp không bỏ sót.",
        "filter": {"category": "ai_problem_solving"},
    },
    {
        "id": "Q4",
        "query": "What are the trade-offs between fixed-size chunking and recursive chunking for technical docs?",
        "gold_doc": "chunking_experiment_report",
        "gold_answer": "Fixed-size: simple, may cut sentences; recursive: respects boundaries, variable chunk count.",
        "filter": None,
    },
    {
        "id": "Q5",
        "query": "What is a vector store and how does it support retrieval-augmented generation?",
        "gold_doc": "vector_store_notes",
        "gold_answer": "Vector store stores embeddings, supports semantic search; RAG retrieves top-k chunks as LLM context.",
        "filter": None,
    },
]

# ─── Header-aware chunker (from REPORT strategy) ─────────────────────────────

class HeaderAwareChunker:
    HEADING_RE = re.compile(
        r"^(#{1,6}\s+|LOGICAL THINKING|Tại sao|AI ≠|LEARNING OBJECTIVES|AGENDA|PHẦN|"
        r"MECE|Impact|Lịch sử|Giai đoạn|Ý tưởng|Sự phát triển|Thời kỳ|Các Model|"
        r"[0-9]+\. |Overview|Getting Started|Install|Set Google|Choose|Create|"
        r"Step [0-9]+:|Tool Use|Audio Transcription|Voice Activity Detection)"
    )

    def __init__(self, max_chars: int = 1000):
        self.max_chars = max_chars
        self.fallback = RecursiveChunker(chunk_size=max_chars)

    def chunk(self, text: str) -> list[str]:
        sections: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            if self.HEADING_RE.match(line.strip()) and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())

        chunks: list[str] = []
        for section in sections:
            if not section:
                continue
            if len(section) <= self.max_chars:
                chunks.append(section)
            else:
                chunks.extend(self.fallback.chunk(section))
        return chunks


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_corpus(chunker: HeaderAwareChunker) -> tuple[list[Document], list[dict]]:
    base = Path(__file__).parent
    docs: list[Document] = []
    stats: list[dict] = []
    for entry in CORPUS:
        path = base / entry["path"]
        if not path.exists():
            print(f"  SKIP {entry['path']} (not found)")
            continue
        content = path.read_text(encoding="utf-8")
        chunks = chunker.chunk(content)
        for i, chunk in enumerate(chunks):
            meta = {
                **entry["meta"],
                "source": entry["path"],
                "title": entry["title"],
                "chunk_index": i,
            }
            # doc.id = file-level id so store sets metadata["doc_id"] correctly
            docs.append(Document(id=entry["id"], content=chunk, metadata=meta))
        avg = int(sum(len(c) for c in chunks) / max(len(chunks), 1))
        stats.append({"file": entry["id"], "chunks": len(chunks), "avg_len": avg})
        print(f"  {entry['id']}: {len(chunks)} chunks, avg {avg} chars")
    return docs, stats


def run_benchmark(provider: str, embedder, docs: list[Document], stats: list[dict]) -> dict:
    print(f"\n{'='*60}\n  PROVIDER: {provider}\n{'='*60}")
    store = EmbeddingStore(collection_name=f"bench_{provider}", embedding_fn=embedder)

    print(f"  Indexing {len(docs)} chunks...")
    if provider == "gemini":
        BATCH = 20
        for i in range(0, len(docs), BATCH):
            batch = docs[i : i + BATCH]
            for attempt in range(6):
                try:
                    store.add_documents(batch)
                    break
                except Exception as exc:
                    msg = str(exc)
                    # parse retryDelay from error, default 65s
                    m = _re.search(r"retry.*?(\d+)\.?\d*\s*s", msg, _re.IGNORECASE)
                    wait = int(m.group(1)) + 5 if m else 65
                    print(f"\n    429 — wait {wait}s (attempt {attempt+1}/6)...")
                    time.sleep(wait)
            done = min(i + BATCH, len(docs))
            print(f"    {done}/{len(docs)} indexed", end="\r")
            if done < len(docs):
                time.sleep(3)
        print()
    else:
        store.add_documents(docs)

    total = store.get_collection_size()
    print(f"  Store size: {total}")

    results = []
    for q in QUERIES:
        print(f"\n  [{q['id']}] {q['query'][:65]}...")
        if q["filter"]:
            top3 = store.search_with_filter(q["query"], top_k=3, metadata_filter=q["filter"])
        else:
            top3 = store.search(q["query"], top_k=3)

        top1_doc = top3[0]["metadata"].get("doc_id", "") if top3 else ""
        top1_correct = top1_doc == q["gold_doc"]
        top3_data = [
            {
                "rank": i + 1,
                "doc_id": r["metadata"].get("doc_id", ""),
                "score": round(r["score"], 4),
                "preview": r["content"][:150].replace("\n", " "),
                "relevant": r["metadata"].get("doc_id", "") == q["gold_doc"],
            }
            for i, r in enumerate(top3)
        ]
        top3_rel = sum(1 for r in top3_data if r["relevant"])
        mark = "✓" if top1_correct else "✗"
        print(f"    {mark} top1={top1_doc} score={top3[0]['score']:.4f}" if top3 else "    (empty)")
        results.append({
            "query_id": q["id"],
            "query": q["query"],
            "gold_doc": q["gold_doc"],
            "filter": q["filter"],
            "top1_doc": top1_doc,
            "top1_score": round(top3[0]["score"], 4) if top3 else 0.0,
            "top1_correct": top1_correct,
            "top3_relevant": top3_rel,
            "top3": top3_data,
        })

    return {
        "provider": provider,
        "backend": getattr(embedder, "_backend_name", provider),
        "total_chunks": total,
        "corpus_stats": stats,
        "query_results": results,
        "top1_correct": sum(1 for r in results if r["top1_correct"]),
        "top3_relevant": sum(1 for r in results if r["top3_relevant"] > 0),
    }


def save_cache(runs: list[dict]) -> None:
    out = Path("report/benchmark_cache.json")
    out.write_text(
        json.dumps({"generated_at": datetime.now().isoformat(), "runs": runs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nCache -> {out}")


def save_md(runs: list[dict]) -> None:
    lines = [
        f"# Benchmark Run — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Corpus Stats",
        "",
        "| File | Chunks | Avg Len |",
        "|------|--------|---------|",
    ]
    for s in runs[0]["corpus_stats"]:
        lines.append(f"| `{s['file']}` | {s['chunks']} | {s['avg_len']} |")

    lines += ["", "## Summary", "", "| Provider | Backend | Chunks | Top-1 / 5 | Top-3 / 5 |",
              "|----------|---------|--------|-----------|-----------|"]
    for r in runs:
        lines.append(f"| {r['provider']} | `{r['backend']}` | {r['total_chunks']} | {r['top1_correct']}/5 | {r['top3_relevant']}/5 |")

    for r in runs:
        lines += ["", f"## {r['provider'].upper()} — Query Results", "",
                  "| # | Query | Top-1 | Score | ✓ | Top-3 rel |",
                  "|---|-------|-------|-------|---|-----------|"]
        for q in r["query_results"]:
            mark = "✓" if q["top1_correct"] else "✗"
            lines.append(f"| {q['query_id']} | {q['query'][:50]}… | `{q['top1_doc']}` | {q['top1_score']:.4f} | {mark} | {q['top3_relevant']}/3 |")

        for q in r["query_results"]:
            lines += ["", f"### {q['query_id']} — {q['query']}", "",
                      f"Gold: `{q['gold_doc']}`  Filter: `{q['filter']}`", ""]
            for t in q["top3"]:
                mark = "**✓**" if t["relevant"] else "✗"
                lines.append(f"- Rank {t['rank']} {mark} `{t['doc_id']}` score={t['score']:.4f}")
                lines.append(f"  > {t['preview']}")
            lines.append("")

    out = Path("report/benchmark_run.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"MD   -> {out}")


def main() -> None:
    print("=== Loading corpus (HeaderAwareChunker max_chars=1000) ===")
    chunker = HeaderAwareChunker(max_chars=1000)
    docs, stats = load_corpus(chunker)
    print(f"Total: {len(docs)} chunks from {len(stats)} files\n")

    runs: list[dict] = []

    # LOCAL
    try:
        print("── LOCAL (all-MiniLM-L6-v2) ──")
        runs.append(run_benchmark("local", LocalEmbedder(), docs, stats))
    except Exception as e:
        print(f"LOCAL FAILED: {e}")

    # GEMINI
    try:
        print("\n── GEMINI (gemini-embedding-002) ──")
        runs.append(run_benchmark("gemini", GeminiEmbedder(), docs, stats))
    except Exception as e:
        print(f"GEMINI FAILED: {e}")

    if runs:
        save_cache(runs)
        save_md(runs)
        print("\n── RESULTS ──")
        for r in runs:
            print(f"  {r['provider']:8s}  top1={r['top1_correct']}/5  top3={r['top3_relevant']}/5")
    else:
        print("No results.")


if __name__ == "__main__":
    main()
