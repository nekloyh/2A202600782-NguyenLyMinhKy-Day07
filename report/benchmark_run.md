# Benchmark Run — 2026-06-05 23:20

## Corpus Stats

| File | Chunks | Avg Len |
|------|--------|---------|
| `deep_learning_history` | 51 | 238 |
| `gemini_live_api_cookbook` | 67 | 407 |
| `logical_thinking` | 206 | 224 |
| `rag_system_design` | 6 | 396 |
| `vector_store_notes` | 8 | 263 |
| `vi_retrieval_notes` | 2 | 832 |
| `python_intro` | 3 | 646 |
| `customer_support_playbook` | 2 | 844 |
| `chunking_experiment_report` | 6 | 329 |

## Summary

| Provider | Backend | Chunks | Top-1 / 5 | Top-3 / 5 |
|----------|---------|--------|-----------|-----------|
| local | `all-MiniLM-L6-v2` | 351 | 5/5 | 5/5 |

## LOCAL — Query Results

| # | Query | Top-1 | Score | ✓ | Top-3 rel |
|---|-------|-------|-------|---|-----------|
| Q1 | Lịch sử Deep Learning bắt đầu từ khi nào và ai là … | `deep_learning_history` | 0.7008 | ✓ | 3/3 |
| Q2 | How do I create a live audio session with Gemini L… | `gemini_live_api_cookbook` | 0.7217 | ✓ | 3/3 |
| Q3 | MECE framework là gì và áp dụng như thế nào trong … | `logical_thinking` | 0.6709 | ✓ | 3/3 |
| Q4 | What are the trade-offs between fixed-size chunkin… | `chunking_experiment_report` | 0.7244 | ✓ | 3/3 |
| Q5 | What is a vector store and how does it support ret… | `vector_store_notes` | 0.8213 | ✓ | 3/3 |

### Q1 — Lịch sử Deep Learning bắt đầu từ khi nào và ai là những người tiên phong?

Gold: `deep_learning_history`  Filter: `{'category': 'deep_learning_history'}`

- Rank 1 **✓** `deep_learning_history` score=0.7008
  > # Các Papers Nổi Tiếng và Quan Trọng Trong Lịch Sử Deep Learning
- Rank 2 **✓** `deep_learning_history` score=0.6585
  > ### Các mốc quan trọng:  - 1956: Cụm từ "Artificial Intelligence" lần đầu được đề cập tại hội nghị Dartmouth [1](#page-5-0) - 1957: Frank Rosenblatt g
- Rank 3 **✓** `deep_learning_history` score=0.6429
  > #### Contributions của Geoffrey Hinton  Geoffrey Hinton có nhiều đóng góp quan trọng được ghi nhận trong các papers:  - Backpropagation: Phát triển th


### Q2 — How do I create a live audio session with Gemini Live API and handle voice activity detection?

Gold: `gemini_live_api_cookbook`  Filter: `{'category': 'api_cookbook'}`

- Rank 1 **✓** `gemini_live_api_cookbook` score=0.7217
  > ## Overview  This cookbook outlines the technical specifications and implementation details for the Gemini Live API in Vertex AI. The Live API is desi
- Rank 2 **✓** `gemini_live_api_cookbook` score=0.5718
  > ### Choose a Gemini model  Select an appropriate model based on your interaction requirements. See Live API [Supported](https://docs.cloud.google.com/
- Rank 3 **✓** `gemini_live_api_cookbook` score=0.5548
  > ## Send Audio  Implementing real-time audio requires strict adherence to sample rate specifications and careful buffer management to ensure low latenc


### Q3 — MECE framework là gì và áp dụng như thế nào trong AI problem solving?

Gold: `logical_thinking`  Filter: `{'category': 'ai_problem_solving'}`

- Rank 1 **✓** `logical_thinking` score=0.6709
  > ## **PHẦN I: FOUNDATION**  Problem-Solving Framework trong AI và Kỹ thuật đặt câu hỏi 5 Whys
- Rank 2 **✓** `logical_thinking` score=0.6709
  > ## **PHẦN I: FOUNDATION**  Problem-Solving Framework trong AI và Kỹ thuật đặt câu hỏi 5 Whys
- Rank 3 **✓** `logical_thinking` score=0.6709
  > ## **PHẦN I: FOUNDATION**  Problem-Solving Framework trong AI và Kỹ thuật đặt câu hỏi 5 Whys


### Q4 — What are the trade-offs between fixed-size chunking and recursive chunking for technical docs?

Gold: `chunking_experiment_report`  Filter: `None`

- Rank 1 **✓** `chunking_experiment_report` score=0.7244
  > ## Fixed-Size Chunking  Fixed-size chunking was simple to implement and produced predictable chunk counts. It worked reasonably well for long technica
- Rank 2 **✓** `chunking_experiment_report` score=0.6604
  > ## Purpose  This report summarizes a small experiment comparing fixed-size chunking, sentence-based chunking, and recursive chunking on internal docum
- Rank 3 **✓** `chunking_experiment_report` score=0.6448
  > ## Conclusion  The experiment suggests that there is no universal best strategy, but recursive chunking is a strong default for mixed technical docume


### Q5 — What is a vector store and how does it support retrieval-augmented generation?

Gold: `vector_store_notes`  Filter: `None`

- Rank 1 **✓** `vector_store_notes` score=0.8213
  > # Vector Store Notes  A vector store is a database or storage layer designed to keep embeddings and retrieve the most similar items to a query vector.
- Rank 2 **✓** `vector_store_notes` score=0.6209
  > 3. **Store the vector and metadata** so records can be searched and filtered.
- Rank 3 **✓** `vector_store_notes` score=0.5364
  > ## Common Risks  Vector stores are powerful, but retrieval is not magically correct. Poor chunking, low-quality embeddings, missing metadata, and weak
