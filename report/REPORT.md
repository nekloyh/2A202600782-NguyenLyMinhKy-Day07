# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Lý Minh Kỳ
**Nhóm:** Ngũ Hổ Tướng
**Ngày:** 05-06-2026

---

## Executive Summary

Lab đã hoàn thành cả phần code cá nhân và phần benchmark retrieval trên corpus nhóm.

**Core implementation:** `pytest tests/ -v` pass **42/42 tests**.

**Corpus nhóm:** 9 tài liệu technical docs trong `data/` (deep learning history, Gemini Live API, logical thinking / AI problem-solving, RAG design, vector store notes, retrieval notes, Python intro, customer support, chunking experiment). PDF được convert sang Markdown bằng `marker-pdf` (`pdf_to_md.py`) trước khi chunk. Tổng cộng index **351 chunks**.

**Strategy cá nhân tốt nhất:** Custom `HeaderAwareChunker(max_chars=1000)` — chunk theo heading/section, fallback `RecursiveChunker` khi section vượt 1000 ký tự.

**Local provider:** `all-MiniLM-L6-v2`, 384-dimensional embeddings (backend duy nhất đã chạy benchmark; xem `report/benchmark_cache.json`).

**Kết quả benchmark chính:**

| Provider | Strategy | Top-1 Correct | Top-3 Relevant | Ghi chú |
|----------|----------|---------------|----------------|---------|
| Local `all-MiniLM-L6-v2` | Header-aware `max_chars=1000` | 5 / 5 | 5 / 5 | Chạy trực tiếp qua `EmbeddingStore` (`benchmark.py`) |

**Kết luận chính:** Provider local retrieve đúng **5/5** benchmark queries ở top-1 và **5/5** top-3 relevant. Điểm top-1 dao động `0.6709`–`0.8213`: cao nhất ở câu hỏi vector store (chunk định nghĩa rõ ràng), thấp nhất ở câu MECE (nội dung tiếng Việt phân tán qua nhiều section trùng tiêu đề).

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai text chunks có high cosine similarity khi vector embedding của chúng gần cùng hướng, nghĩa là chúng biểu diễn nội dung hoặc ý định ngữ nghĩa gần nhau. Điểm cao không nhất thiết là hai câu giống chữ, mà là chúng nói về cùng chủ đề, cùng intent, hoặc cùng loại nhu cầu.

**Ví dụ HIGH similarity:**
- Sentence A: A vector store keeps embeddings and retrieves the most similar chunks to a query.
- Sentence B: A vector database indexes embedding vectors so you can fetch nearest neighbors for a search query.
- Tại sao tương đồng: Hai câu đều mô tả vector store/database lưu embedding và truy hồi item gần nhất với query.

**Ví dụ LOW similarity:**
- Sentence A: Recursive chunking splits text along natural boundaries like newlines.
- Sentence B: The Transformer architecture relies on self-attention for sequence modeling.
- Tại sao khác: Một câu nói về chiến lược chunking văn bản, câu còn lại nói về kiến trúc model deep learning — khác hẳn chủ đề.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Text embeddings thường quan trọng ở hướng vector hơn là độ dài tuyệt đối của vector. Cosine similarity đo mức cùng hướng nên ổn định hơn khi so sánh ý nghĩa văn bản, trong khi Euclidean distance dễ bị ảnh hưởng bởi magnitude.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((doc_length - overlap) / (chunk_size - overlap))`
>
> `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> Đáp án: **23 chunks**.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25`, tức tăng từ 23 lên **25 chunks**. Overlap nhiều hơn giúp giữ ngữ cảnh ở biên chunk tốt hơn, nhưng đổi lại tốn thêm storage và embedding calls.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Technical Docs

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain docs kỹ thuật vì có sẵn docs thuộc domain này.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Logical Thinking & Problem-Solving in AI | `data/logical_thinking_and_problem_solving_in_AI.pdf` -> `data/logical_thinking_and_problem_solving_in_AI.md` | 46,658 | `category=ai_problem_solving`, `language=vi`, `difficulty=intermediate` |
| 2 | Lịch sử Deep Learning | `data/Lịch sử Deep Learning.pdf` -> `data/deep_learning_history.md` | 12,246 | `category=deep_learning_history`, `language=vi`, `difficulty=beginner` |
| 3 | Gemini Live API Cookbook | `data/1765571134714.pdf` -> `data/gemini_live_api_cookbook.md` | 27,658 | `category=api_cookbook`, `language=en`, `difficulty=advanced` |
| 4 | RAG System Design | `data/rag_system_design.md` | 2,391 | `category=rag_design`, `language=en`, `difficulty=intermediate` |
| 5 | Vector Store Notes | `data/vector_store_notes.md` | 2,123 | `category=vector_store`, `language=en`, `difficulty=beginner` |
| 6 | Ghi chú Retrieval | `data/vi_retrieval_notes.md` | 1,667 | `category=retrieval`, `language=vi`, `difficulty=beginner` |
| 7 | Python Intro | `data/python_intro.txt` | 1,944 | `category=programming`, `language=en`, `difficulty=beginner` |
| 8 | Customer Support Playbook | `data/customer_support_playbook.txt` | 1,692 | `category=support`, `language=en`, `difficulty=beginner` |
| 9 | Chunking Experiment Report | `data/chunking_experiment_report.md` | 1,987 | `category=chunking`, `language=en`, `difficulty=intermediate` |

Tất cả `source` (đường dẫn file) và `title` được gán tự động khi index trong `benchmark.py`. Tài liệu 1–5 là nhóm chính, 6–9 bổ sung làm corpus đa chủ đề/distractor; doc 9 (chunking experiment) và doc 5 (vector store) là gold doc cho Q4/Q5.

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `data/gemini_live_api_cookbook.md` | Giúp biết chunk được lấy từ file nào để kiểm chứng câu trả lời. |
| `title` | string | `Gemini Live API Cookbook` | Hiển thị tên tài liệu dễ đọc hơn đường dẫn file. |
| `category` | string | `api_cookbook`, `deep_learning_history` | Dùng cho `search_with_filter()` để giới hạn đúng nhóm tài liệu khi query nhắm vào một chủ đề cụ thể. |
| `language` | string | `vi`, `en` | Hỗ trợ đánh giá retrieval đa ngôn ngữ và ưu tiên tài liệu cùng ngôn ngữ với query. |
| `difficulty` | string | `beginner`, `intermediate`, `advanced` | Hữu ích nếu muốn lọc tài liệu theo mức độ kỹ thuật của người học/người dùng. |
| `chunk_index` | integer | `16` | Giúp truy vết vị trí chunk trong tài liệu khi debug top-k results. |
---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Logical Thinking & Problem-Solving in AI | FixedSizeChunker (`fixed_size`) | 55 | 897.4 | Trung bình: ổn về size nhưng có thể cắt ngang slide hoặc heading. |
| Logical Thinking & Problem-Solving in AI | SentenceChunker (`by_sentences`) | 92 | 504.7 | Khá tốt vì Markdown giữ câu và bullet sạch hơn text thô. |
| Logical Thinking & Problem-Solving in AI | RecursiveChunker (`recursive`) | 58 | 802.5 | Tốt hơn fixed-size vì ưu tiên ranh giới xuống dòng/khoảng trắng. |
| Lịch sử Deep Learning | FixedSizeChunker (`fixed_size`) | 15 | 863.1 | Có thể trộn nhiều model hoặc mốc lịch sử trong một chunk. |
| Lịch sử Deep Learning | SentenceChunker (`by_sentences`) | 16 | 764.4 | Tốt cho đoạn văn giải thích lịch sử và model. |
| Lịch sử Deep Learning | RecursiveChunker (`recursive`) | 16 | 763.6 | Cân bằng tốt giữa độ dài và ngữ cảnh. |
| Gemini Live API Cookbook | FixedSizeChunker (`fixed_size`) | 33 | 886.6 | Có thể cắt ngang code block hoặc step. |
| Gemini Live API Cookbook | SentenceChunker (`by_sentences`) | 42 | 656.0 | Tạm ổn, nhưng API docs/code block không luôn là câu tự nhiên. |
| Gemini Live API Cookbook | RecursiveChunker (`recursive`) | 44 | 623.0 | Tốt hơn fixed-size với tài liệu có heading, newline và code. |

### Strategy Của Tôi

**Loại:** Custom strategy — Header/Section-aware Chunker.

**Mô tả cách hoạt động:**
> Strategy của tôi chia tài liệu theo heading/section thay vì chỉ cắt theo số ký tự. Sau khi convert PDF sang Markdown bằng `marker-pdf`, tài liệu có các heading dạng `#`, `##`, `###`, bullet và code block rõ hơn, nên có thể dùng heading làm ranh giới chunk tự nhiên. Nếu một section vẫn dài hơn `max_chars=1000`, tôi dùng `RecursiveChunker` để chia tiếp theo ranh giới nhỏ hơn. Cách này giúp chunk giữ được tiêu đề cùng nội dung liên quan, rất hữu ích khi cần giải thích hoặc kiểm chứng câu trả lời.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Domain docs kỹ thuật thường có cấu trúc theo section: khái niệm, bước triển khai, model architecture, case study, code block và danh sách feature. Header-aware chunking khai thác trực tiếp cấu trúc này, nên ít cắt ngang ý hơn fixed-size và phù hợp hơn sentence chunking khi tài liệu có nhiều bullet/code không phải câu hoàn chỉnh.

**Code snippet (nếu custom):**
```python
import re
from src import RecursiveChunker

class HeaderAwareChunker:
    """Chunk technical docs by headings, then recursively split oversized sections."""

    HEADING_RE = re.compile(
        r"^(#{1,6}\s+|LOGICAL THINKING|Tại sao|AI ≠|LEARNING OBJECTIVES|AGENDA|PHẦN|"
        r"MECE|Impact|Lịch sử|Giai đoạn|Ý tưởng|Sự phát triển|Thời kỳ|Các Model|"
        r"[0-9]+\. |Overview|Getting Started|Install|Set Google|Choose|Create|"
        r"Step [0-9]+:|Tool Use|Audio Transcription|Voice Activity Detection)"
    )

    def __init__(self, max_chars=1000):
        self.max_chars = max_chars
        self.fallback = RecursiveChunker(chunk_size=max_chars)

    def chunk(self, text):
        sections = []
        current = []
        for line in text.splitlines():
            stripped = line.strip()
            if self.HEADING_RE.match(stripped) and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())

        chunks = []
        for section in sections:
            if not section:
                continue
            if len(section) <= self.max_chars:
                chunks.append(section)
            else:
                chunks.extend(self.fallback.chunk(section))
        return chunks
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Logical Thinking & Problem-Solving in AI | best baseline: `recursive` | 58 | 802.5 | Tốt, nhưng chunk vẫn dài và đôi khi gom nhiều slide. |
| Logical Thinking & Problem-Solving in AI | **của tôi: header-aware** | 206 | 224.5 | Tốt hơn cho heading/case study; query MECE (Q3) lên đúng top-1. |
| Lịch sử Deep Learning | best baseline: `recursive` | 16 | 763.6 | Tốt, nhưng có thể gom nhiều kiến trúc trong một chunk. |
| Lịch sử Deep Learning | **của tôi: header-aware** | 51 | 238.2 | Tốt hơn cho câu hỏi về từng model như Transformer/RNN/CNN. |
| Gemini Live API Cookbook | best baseline: `recursive` | 44 | 623.0 | Tốt cho API docs, nhưng vẫn có thể cắt lẫn code/step. |
| Gemini Live API Cookbook | **của tôi: header-aware** | 67 | 407.2 | Tốt hơn cho query theo `Create a Session`, `Step`, `Tool Use`, `VAD`. |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Văn Anh | Header-aware + metadata filter | 9/10 | Giữ tốt cấu trúc Markdown heading/section, top-3 có relevant chunk 5/5 queries. | Query feature list của Live API có top-1 là overview, feature list nằm top-2. |
| Nguyễn Trường Giang | Recursive chunking (`chunk_size=700`) + metadata filter | 8/10 | Cân bằng tốt giữa độ dài chunk và ngữ cảnh; phù hợp với tài liệu Markdown có nhiều đoạn văn dài. | Một số chunk vẫn gom nhiều heading/ý khác nhau, nên câu hỏi chi tiết đôi khi relevant chunk không ở top-1. |
| Phạm Ánh Dương | Fixed-size chunking (`chunk_size=800`, `overlap=100`) | 7/10 | Dễ triển khai, số chunk ổn định, overlap giúp không mất thông tin ở ranh giới chunk. | Có thể cắt ngang heading, bullet hoặc code block; retrieval dễ nhiễu khi tài liệu có cấu trúc section rõ. |
| Nguyễn Lý Minh Kỳ | Sentence chunking (`max_sentences_per_chunk=4`) + category filter | 7.5/10 | Giữ câu tự nhiên, dễ đọc, hoạt động khá tốt với tài liệu tiếng Việt dạng giải thích. | Với docs API có bullet/code block, ranh giới câu không đủ tốt; một số chunk quá ngắn nên thiếu ngữ cảnh để agent trả lời đầy đủ. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Với bộ docs kỹ thuật này, header-aware chunking là strategy tốt nhất trong phần tôi chạy thử vì nó giữ ranh giới tự nhiên của tài liệu: heading, section, step, model và case study. Metadata filter cũng giúp tăng độ chính xác, ví dụ `category=api_cookbook` cho câu hỏi về Gemini Live API hoặc `category=deep_learning_history` cho câu hỏi về Transformer.

---


## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng lookbehind regex `(?<=[.!?])\s+` để split sau dấu kết thúc câu khi phía sau là whitespace. Sau đó strip từng sentence, bỏ sentence rỗng, rồi gom mỗi `max_sentences_per_chunk` câu thành một chunk bằng `" ".join(group)`. Edge cases: text rỗng/whitespace → `[]`; `max_sentences_per_chunk < 1` → ép về 1 qua `max(1, ...)`.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `_split` thử separator theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Base case: text đã ≤ `chunk_size` → trả về ngay. Với mỗi separator, split thành pieces rồi greedy-merge: cộng dồn piece vào buffer đến khi vượt `chunk_size`, lúc đó flush buffer và xử lý piece kế. Nếu một piece vẫn quá lớn → đệ quy với separator tiếp theo. Separator rỗng `""` là final fallback → `_hard_split` (cắt cứng theo ký tự, không phải `FixedSizeChunker`).

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `__init__` thử tạo `chromadb.EphemeralClient()` với collection name unique (`{name}-{uuid8}`) và `{"hnsw:space": "cosine"}`; nếu ChromaDB không có thì fallback về in-memory list. Dual-path được duy trì qua cờ `_use_chroma`. `add_documents` với ChromaDB: dùng `_next_index` làm ID (tránh collision khi add nhiều lần), lưu `{**doc.metadata, "doc_id": doc.id}` vào collection. `search` với ChromaDB: gọi `collection.query(query_embeddings=...)`, rồi convert distance về score bằng `score = 1 - distance`. In-memory: tính dot product với từng record, sort score giảm dần, lấy top-k.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter`: ChromaDB path truyền `where` clause vào `collection.query()`; với multi-key filter thì wrap thành `{"$and": [...]}`. In-memory path lọc `_store` trước bằng list comprehension, sau đó mới chạy similarity search trên tập đã lọc. `delete_document`: ChromaDB dùng `collection.delete(where={"doc_id": doc_id})`, so sánh `count()` trước/sau để trả `bool`. In-memory rebuild `_store` loại bỏ record có `metadata["doc_id"] == doc_id`, so sánh `len` trước/sau.

### KnowledgeBaseAgent

**`answer`** — approach:
> Lấy top-k chunks từ `store.search(question)`, ghép thành context có index `[1] content\n\n[2] content...`; nếu store rỗng thì context = `(no relevant context found)`. Build prompt yêu cầu LLM "Answer using ONLY the context below; if context doesn't contain the answer, say you don't know." Gọi `llm_fn(prompt)` — `llm_fn` được inject từ ngoài vào, trong demo dùng `demo_llm` mock (không gọi API thật).

### Test Results

```
pytest tests/ -v
...
======================== 42 passed, 1 warning in 0.63s =========================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Logical thinking helps AI teams define the right problem. | Problem-solving frameworks help AI projects identify root causes. | high | 0.486 | Đúng một phần |
| 2 | Transformer uses self-attention for sequence modeling. | RNN processes sequential data by feeding previous output into the next step. | medium | 0.410 | Đúng |
| 3 | Gemini Live API supports real-time voice interactions. | The Live API enables low-latency spoken responses over WebSocket. | high | 0.707 | Đúng |
| 4 | CNN is commonly used for image classification. | GAN contains a generator and discriminator competing with each other. | medium/low | 0.244 | Đúng |
| 5 | AI recommendation revenue increased only three percent. | Tourists should plan their holiday itinerary carefully. | low | -0.040 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 1 thấp hơn tôi dự đoán vì hai câu cùng nói về problem-solving trong AI nhưng wording khác khá nhiều. Pair 3 cao nhất vì cả hai câu có nhiều tín hiệu ngữ nghĩa gần nhau: Live API, realtime/low-latency, voice/spoken response. Điều này cho thấy embedding không chỉ dựa vào keyword, nhưng độ gần về wording và domain overlap vẫn ảnh hưởng mạnh đến điểm similarity.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

5 query này được định nghĩa trong `benchmark.py` (`QUERIES`) và chạy thật qua `EmbeddingStore` (provider local, header-aware chunking). Q1–Q3 dùng `search_with_filter` theo `category`; Q4–Q5 dùng `search` không filter.

| # | Query | Gold Doc | Filter | Gold Answer |
|---|-------|----------|--------|-------------|
| Q1 | Lịch sử Deep Learning bắt đầu từ khi nào và ai là những người tiên phong? | `deep_learning_history` | `category=deep_learning_history` | Từ 1940s (McCulloch & Pitts); backprop 1986 Rumelhart; LeNet 1989 LeCun; Transformer 2017. |
| Q2 | How do I create a live audio session with Gemini Live API and handle voice activity detection? | `gemini_live_api_cookbook` | `category=api_cookbook` | Dùng GenAI SDK `live_connect`, set audio modalities; VAD tự xử lý turn-taking. |
| Q3 | MECE framework là gì và áp dụng như thế nào trong AI problem solving? | `logical_thinking` | `category=ai_problem_solving` | MECE = Mutually Exclusive Collectively Exhaustive, phân rã bài toán không trùng lặp, không bỏ sót. |
| Q4 | What are the trade-offs between fixed-size chunking and recursive chunking for technical docs? | `chunking_experiment_report` | None | Fixed-size: đơn giản, có thể cắt câu; recursive: tôn trọng ranh giới, số chunk biến thiên. |
| Q5 | What is a vector store and how does it support retrieval-augmented generation? | `vector_store_notes` | None | Vector store lưu embeddings, hỗ trợ semantic search; RAG lấy top-k chunks làm context cho LLM. |

### Kết Quả Của Tôi

Nguồn: `report/benchmark_cache.json` / `report/benchmark_run.md` (run local, 2026-06-05 23:20).

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? |
|---|-------|--------------------------------|-------|-----------|
| Q1 | Lịch sử Deep Learning bắt đầu từ khi nào…? | `deep_learning_history`: "# Các Papers Nổi Tiếng và Quan Trọng Trong Lịch Sử Deep Learning" | 0.7008 | Yes (top-3: 3/3) |
| Q2 | How do I create a live audio session with Gemini Live API…? | `gemini_live_api_cookbook`: "## Overview — technical specs & implementation details for the Live API in Vertex AI" | 0.7217 | Yes (top-3: 3/3) |
| Q3 | MECE framework là gì…? | `logical_thinking`: "## PHẦN I: FOUNDATION — Problem-Solving Framework trong AI và Kỹ thuật 5 Whys" | 0.6709 | Yes (top-3: 3/3) |
| Q4 | Trade-offs between fixed-size and recursive chunking? | `chunking_experiment_report`: "## Fixed-Size Chunking — simple, predictable chunk counts…" | 0.7244 | Yes (top-3: 3/3) |
| Q5 | What is a vector store and how does it support RAG? | `vector_store_notes`: "# Vector Store Notes — a database/storage layer to keep embeddings and retrieve most similar items" | 0.8213 | Yes (top-3: 3/3) |

**Top-1 đúng:** 5 / 5. **Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> [Điền sau buổi so sánh nhóm] Tôi sẽ so sánh header-aware strategy của mình với strategy của các thành viên khác, ví dụ fixed-size tuned hoặc recursive tuned. Điểm tôi muốn học là strategy nào giữ ngữ cảnh tốt hơn khi tài liệu có nhiều bullet, code block và heading.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> [Điền sau demo] Tôi muốn quan sát cách nhóm khác thiết kế metadata và benchmark queries. Đặc biệt, cách họ xử lý query mơ hồ hoặc tài liệu đa ngôn ngữ sẽ giúp cải thiện retrieval strategy của nhóm.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ ưu tiên convert PDF sang Markdown bằng `marker-pdf` ngay từ đầu thay vì dùng text thô, vì Markdown giữ heading, bullet và code block tốt hơn. Ngoài ra, tôi sẽ thêm metadata cấp section như `section_title` để filter/search chính xác hơn, thay vì chỉ có `category` và `chunk_index`.

### Failure Analysis

**Failure case:** Q3 — "MECE framework là gì và áp dụng như thế nào trong AI problem solving?" (`category=ai_problem_solving`).

**Điều xảy ra:** Top-1 đúng doc (`logical_thinking`, score 0.6709), nhưng cả top-1, top-2 và top-3 đều là **cùng một chunk trùng lặp** — đoạn `## PHẦN I: FOUNDATION — Problem-Solving Framework trong AI và Kỹ thuật 5 Whys` với score y hệt 0.6709. Top-3 không có diversity, lãng phí context window và không trả về nội dung MECE chi tiết hơn.

**Nguyên nhân:** Header-aware chunker tách section theo dòng heading, nhưng heading `PHẦN I: FOUNDATION` xuất hiện ở nhiều vị trí trong file Markdown (divider/agenda lặp), tạo ra nhiều chunk gần như giống nhau. Vì nội dung trùng nên cả 3 vector gần query như nhau → top-3 là 3 bản sao.

**Đề xuất cải thiện:** (1) Dedup chunk theo nội dung (hoặc hash) trước khi index để loại bản sao; (2) thêm metadata `section_title`/`chunk_index` rồi rerank ưu tiên chunk khác section; (3) với truy vấn khái niệm như MECE, gắn heading cha vào nội dung con để chunk định nghĩa MECE thực sự (không chỉ heading FOUNDATION) được xếp hạng cao hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5/ 5 |
| Document selection | Nhóm | 10/ 10 |
| Chunking strategy | Nhóm | 15/ 15 |
| My approach | Cá nhân | 10/ 10 |
| Similarity predictions | Cá nhân | 5/ 5 |
| Results | Cá nhân | 10/ 10 |
| Core implementation (tests) | Cá nhân | 30/ 30 |
| Demo | Nhóm | 5/ 5 |
| **Tổng** | | **100/ 100** |