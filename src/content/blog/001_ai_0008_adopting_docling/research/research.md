# Research: Adopting Docling (for document ingestion, with SmolDocling & LangFlow)

Source material gathered via live browsing (GitHub, official Docling docs, Hugging Face, LangFlow docs) on 2026-08-10. All facts below are cited with the exact URL they came from — use this as raw material, not final article prose.

---

## 1. What is Docling?

- **Repo**: https://github.com/docling-project/docling
- Tagline: *"Docling simplifies document processing by parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the generative AI ecosystem."*
- **Origin**: "The project was started by the AI for knowledge team at **IBM Research Zurich**." Now hosted as a project under the **LF AI & Data Foundation** (Linux Foundation).
- **License**: MIT (codebase). Individual models (e.g. SmolDocling, layout models) have their own licenses.
- **Stats (as of Aug 10, 2026)**: 64.5k GitHub stars, 4.6k forks, 224 watchers, 290 contributors, 202 releases, used by 3.5K+ repos on GitHub, latest release **v2.119.0**.
- **Technical report**: Docling Technical Report, arXiv:2408.09869 (DOI 10.48550/arXiv.2408.09869), cited as:
  ```
  @techreport{Docling,
    author = {Deep Search Team},
    month = {8},
    title = {Docling Technical Report},
    url = {https://arxiv.org/abs/2408.09869},
    eprint = {2408.09869},
    doi = {10.48550/arXiv.2408.09869},
    version = {1.0.0},
    year = {2024}
  }
  ```
- Python 3.10+ required (Python 3.9 support dropped in docling v2.70.0). Works on macOS, Linux, Windows, x86_64 and arm64.

## 2. Supported formats

**Input formats** (from README feature list): PDF, DOCX, PPTX, XLSX, HTML, EPUB, WAV, MP3, WebVTT, Box Notes, email formats (EML, MSG), images (PNG, TIFF, JPEG, ...), LaTeX, DocLang, plain text (.txt, .text), Markdown supersets (.qmd, .Rmd), and more.

Recent additions ("What's new" as of this version):
- 🎬 Video files (MP4, AVI, MOV, MKV, WebM) — parsed with an ASR transcript + representative keyframes
- 📄 ODF (OpenDocument Format): .odt, .ods, .odp
- 💼 XBRL (eXtensible Business Reporting Language) financial reports
- 📧 Email files (.eml, .msg)
- 📚 EPUB e-books
- 📊 Chart understanding (bar chart, pie chart, line plot) — converts charts into tables or code with detail extraction

**Coming soon**: metadata extraction (title, authors, references, language), complex chemistry/molecular structure understanding.

**Output/export formats**: Markdown, HTML, WebVTT, DocLang, **DocTags**, and lossless JSON (the full `DoclingDocument` serialization).

**Application-specific XML schema support**: DocLang, USPTO patents, JATS articles, XBRL financial reports.

Source: https://github.com/docling-project/docling (README)

## 3. Architecture / pipeline

Source: https://docling-project.github.io/docling/concepts/architecture/

- For each document format, the **`DocumentConverter`** knows which format-specific **backend** to use for parsing and which **pipeline** to use for orchestrating execution, along with relevant options.
- This is fully parametrizable — e.g. for PDF, you can swap in different backends and pipeline options.
- The conversion result contains the **`DoclingDocument`** — Docling's fundamental, unified document representation, independent of the source format.
- From a `DoclingDocument` you can: call export methods directly (markdown, dict, etc.), pass it through a **serializer**, or pass it through a **chunker**.
- Base classes are subclassable for specialized/custom implementations (backends, pipelines, chunkers, serializers are all pluggable).

**Feature list relevant to the PDF/parsing pipeline** (from README):
- 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, images
- 🧬 Unified, expressive `DoclingDocument` representation format
- 🔍 Extensive OCR support for scanned PDFs and images
- 👓 Support for several Visual Language Models (VLMs), such as **GraniteDocling**, as an alternative pipeline to the classic model-cascade pipeline
- 🎙️ Audio support with Automatic Speech Recognition (ASR) models
- 🔌 Connect to any agent via an **MCP server**
- 🌐 Run Docling as a service via the **API server** (`docling-serve`)
- 💻 CLI

Two ways to run PDF conversion in practice:
1. **Standard pipeline** — classic cascade of specialized models (layout detection, table structure recognition/TableFormer lineage, OCR engine, reading-order model) feeding into the unified `DoclingDocument`.
2. **VLM pipeline** — a single vision-language model (e.g. `granite_docling`) does full-page or region-guided document conversion directly, e.g.:
   ```
   docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
   ```

## 4. SmolDocling → succeeded by Granite-Docling

Source: https://huggingface.co/docling-project/SmolDocling-256M-preview and https://huggingface.co/ibm-granite/granite-docling-258M

**Important**: the HF page for SmolDocling now displays a banner: *"📢 New Release: We've released granite-docling-258M, the successor to SmolDocling. It will now receive updates and support, check it out!"* — for the article, it's worth clarifying this lineage (SmolDocling was the original ultra-compact VLM; Granite-Docling-258M is the actively maintained successor).

### SmolDocling-256M-preview
- Paper: *"SmolDocling: An ultra-compact vision-language model for end-to-end multi-modal document conversion"*, arXiv:2503.11576 (Mar 14, 2025).
- Developed by: **Docling Team, IBM Research**.
- Model type: multimodal image-text-to-text.
- Architecture: based on **Idefics3**, finetuned from **SmolVLM-256M-Instruct** (base LLM: HuggingFaceTB/SmolLM2-135M).
- Size: **0.3B params** (256M), tensor type BF16.
- License: **Apache 2.0**.
- Downloads last month (at time of research): 30,134.
- Introduces **DocTags** — an efficient, minimal tag-based representation for documents, fully compatible with `DoclingDocument`, explicitly designed to be easier for image-to-sequence models than directly emitting HTML/Markdown (which "loses details, doesn't clearly show layout, and increases token count").
- Feature list: DocTags tokenization, OCR, layout + bounding-box localization, code recognition (with indentation), formula recognition, chart recognition/interpretation, table recognition (row/col headers), figure classification, caption-to-image correspondence, list grouping, full-page conversion, OCR with bounding boxes, general (scientific + non-scientific) document processing, seamless Docling import/export.
- Performance claim: **~0.35 sec/page on an A100 GPU** using vLLM.
- Inference options shown on model card: 🤗 Transformers, vLLM (OpenAI-compatible server), SGLang, ONNX, MLX (Apple Silicon local inference), llama.cpp/Ollama/LM Studio/Jan via GGUF quantizations.
- Supported natural-language instructions (DocTags prompting), e.g.:
  - `Convert this page to docling.` → full-page DocTags
  - `Convert chart to table.` → `<chart>`
  - `Convert formula to LaTeX.` → `<formula>`
  - `Convert code to text.` → `<code>`
  - `Convert table to OTSL.` → `<otsl>` (OTSL = Optimized Table Structure Language, from Lysak et al., 2023, arXiv:2305.03393 "Optimized Table Tokenization for Table Structure Recognition")
  - Location/region-targeted OCR via `<loc_x1><loc_y1><loc_x2><loc_y2>` bbox tags
- Trained on datasets: HuggingFaceM4/DoclingMatix, docling-project/SynthCodeNet, docling-project/SynthChartNet, docling-project/SynthFormulaNet.
- 26+ community Spaces built on it (OCR apps, demos, leaderboards).

### Granite-Docling-258M (the current recommended model)
- Developed by: **IBM Research**. Released **Sept 17, 2025**. License: **Apache 2.0**.
- Architecture: builds on Idefics3, but **replaces the vision encoder with `siglip2-base-patch16-512`** and **replaces the LLM with a Granite 165M model** (vs SmolDocling's SmolLM2-135M-based LLM). Trained with the **nanoVLM** framework. Incorporated DocTags directly into SFT data (vs SmolDocling, which had this added post-hoc) — this improved training stability and convergence, explicitly fixing "issues previously observed with SmolDocling" (e.g. infinite generation loops).
- Positioned explicitly as **complementing, not replacing, the Docling library**: "consolidating the functions of multiple single-purpose models into a single, compact VLM." Not intended for general image understanding (use Granite Vision models for that).
- New/improved features vs SmolDocling: enhanced equation recognition, flexible inference modes (full-page / bbox-guided region / element-QA), improved stability (fewer infinite loops), better inline-equation recognition, document element QA (e.g. "does this doc have a table of contents, and in what order"), experimental Japanese/Arabic/Chinese support.
- Easiest usage: install `docling`, then run
  ```
  docling --to html --to md --pipeline vlm --vlm-model granite_docling <source>
  ```
  It auto-downloads the model. Also usable via bare transformers/vLLM/ONNX/mlx-vlm.

**Head-to-head benchmark numbers (Granite-Docling-258M model card), SmolDocling-256M-preview vs granite-docling-258m:**

| Task | Metric | SmolDocling-256M | Granite-Docling-258M |
|---|---|---|---|
| Layout | MAP↑ / F1↑ / Precision↑ / Recall↑ | 0.23 / 0.85 / 0.90 / 0.84 | 0.27 / 0.86 / 0.92 / 0.88 |
| Full Page OCR | Edit-distance↓ / F1↑ / Precision↑ / Recall↑ / BLEU↑ / Meteor↑ | 0.48 / 0.80 / 0.89 / 0.79 / 0.58 / 0.67 | 0.45 / 0.84 / 0.91 / 0.83 / 0.65 / 0.72 |
| Code Recognition | Edit-distance↓ / F1↑ / Precision↑ / Recall↑ / BLEU↑ / Meteor↑ | 0.114 / 0.915 / 0.94 / 0.909 / 0.875 / 0.889 | 0.013 / 0.988 / 0.99 / 0.988 / 0.983 / 0.986 |
| Equation Recognition | Edit-distance↓ / F1↑ / Precision↑ / Recall↑ / BLEU↑ / Meteor↑ | 0.119 / 0.947 / 0.959 / 0.941 / 0.824 / 0.878 | 0.073 / 0.968 / 0.968 / 0.969 / 0.893 / 0.927 |
| Table Recognition (FinTabNet 150dpi) | TEDS structure↑ / TEDS w/content↑ | 0.82 / 0.76 | 0.97 / 0.96 |
| MMStar / OCRBench | ↑ / ↑ | 0.17 / 338 | 0.30 / 500 |

This is a clean, concrete, citable improvement story worth using in the article (esp. Code Recognition edit-distance improving ~9x, and Table Recognition TEDS jumping from 0.82→0.97).

## 5. Practical usage — Python quickstart

Source: https://github.com/docling-project/docling and https://docling-project.github.io/docling/usage/

Install:
```bash
pip install docling
```

CLI:
```bash
docling https://arxiv.org/pdf/2206.01062
# generates a .md file with structured document content
```

CLI with a VLM pipeline (GraniteDocling or other VLMs, incl. MLX acceleration):
```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

Recommended Python usage:
```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())
```

The docs note this pattern generalizes: "converting your source file to a Docling document" then "using that Docling document for your workflow" (export to markdown/HTML/JSON, chunk it, feed it to a RAG pipeline, etc.) — same 2-step mental model regardless of format.

## 6. Chunking for RAG

Source: https://docling-project.github.io/docling/concepts/chunking/

Two chunking philosophies noted explicitly in the docs:
1. Export `DoclingDocument` → Markdown (or similar), then do naive/user-defined chunking as a post-processing step.
2. Use **native Docling chunkers** operating directly on the structured `DoclingDocument` — this is the structure-aware approach and what the docs focus on.

A **chunker** is a Docling abstraction: given a `DoclingDocument`, it returns a stream of chunks, each capturing part of the document as a string + metadata. `BaseChunker` interface requires:
- `chunk(self, dl_doc, **kwargs) -> Iterator[BaseChunk]`
- `contextualize(self, chunk) -> str` — metadata-enriched serialization, meant to feed an embedding or generation model.

Docling's LlamaIndex integration is built directly on the `BaseChunker` interface, so any custom chunker plugs in the same way.

**Chunker implementations:**

- **`HierarchicalChunker`**: uses the document structure info from `DoclingDocument` to create **one chunk per detected document element** (by default merging only list items — configurable via `merge_list_items`). Automatically attaches relevant metadata including headers and captions to each chunk. This is the foundational structure-aware chunker.

- **`HybridChunker`** (`docling.chunking.HybridChunker` or `docling_core.transforms.chunker.hybrid_chunker.HybridChunker`): applies **tokenization-aware refinements on top of hierarchical chunking**. Concretely:
  1. Starts from `HierarchicalChunker` output.
  2. Pass 1 — splits chunks only when oversized w.r.t. the token limit (given a user-provided tokenizer, e.g. HuggingFace or OpenAI/tiktoken).
  3. Pass 2 — merges undersized successive chunks that share the same headings, to avoid fragment-heavy over-chunking.
  - Table-specific options: `repeat_table_header` (default `True` — repeats table header at the start of every chunk when a table spans multiple chunks, preserving context) and `omit_header_on_overflow` (default `False` — drops the header for a specific row if including it would overflow the token limit, but the row alone fits; maximizes token efficiency on very wide tables).
  - Install extras: `pip install 'docling-core[chunking]'` for HF tokenizers, or `'docling-core[chunking-openai]'` for tiktoken.

- **`LineBasedTokenChunker`** (`docling.chunking.LineBasedTokenChunker`): a tokenization-aware chunker that **preserves line boundaries** — useful for structured content like tables, code, logs, lists. Only splits a line if that single line alone exceeds the token limit. Supports a repeated prefix per chunk (e.g., table headers) and an `omit_prefix_on_overflow` param analogous to the HybridChunker's table option.

**Why this matters for RAG** (implicit but clear from the design): naive text-splitting (e.g. fixed character windows) breaks tables mid-row, separates headings from their content, and loses document hierarchy — all of which degrades retrieval quality and LLM context comprehension. Docling's chunkers operate on the *parsed structure* (not raw text), so chunks stay semantically coherent (whole table rows with repeated headers, whole list items, heading-attached sections) while still respecting an embedding model's token budget.

## 7. LangFlow integration (core to this article)

Source: https://docling-project.github.io/docling/integrations/langflow/ → https://docs.langflow.org/bundles-docling

- Docling is one of LangFlow's **featured "Agentic / AI dev frameworks" bundle integrations**, alongside LangChain, LlamaIndex, Haystack, Crew AI, Bee Agent Framework, Hector, Semantica, txtai.
- LangFlow integrates Docling via a **bundle of components for parsing and chunking documents** — this ships as a separate installable bundle (`lfx-docling`) when using `lfx` directly, or is bundled automatically if you `uv pip install langflow`.
- Optional extras (install as needed):
  ```
  uv pip install "lfx-docling[local]"          # local model component
  uv pip install "langflow[docling]"           # if installed as full langflow package
  uv pip install "lfx-docling[chunking]"       # HybridChunker/HierarchicalChunker support
  uv pip install "lfx-docling[image-description]"  # vision-model image captions
  ```
- Windows-specific prerequisite: must enable Windows Developer Mode for Langflow Desktop to use Docling components; also may need `LANGFLOW_DOCLING=True` in `.env`.
- Docker/Linux: may need extra system packages for document processing (their docs link out to a troubleshooting page).

**The four Docling components exposed inside LangFlow's visual canvas:**

1. **Docling (local model)** — ingests documents and processes them by running a **local Docling model**. Outputs `DoclingDocument` data attached to the file objects.
   - Parameters: `files` (File), `pipeline` (String: `standard` or `vlm`), `ocr_engine` (String: `easyocr`, `tesserocr`, `rapidocr`, `ocrmac`).

2. **Docling Serve** — same job, but delegates processing to a remote **`docling-serve`** API instance instead of running a model in-process. Good for offloading heavy inference or centralizing a shared Docling service.
   - Parameters: `files`, `api_url`, `max_concurrency` (Integer), `max_poll_timeout` (Float), `api_headers` (Dict), `docling_serve_opts` (Dict).

3. **Chunk DoclingDocument** — splits `DoclingDocument` objects into chunks (requires the chunking extras).
   - Parameters: `data_inputs` (JSON/Table), `chunker` (String: `HybridChunker` or `HierarchicalChunker`), `provider` (String: Hugging Face or OpenAI tokenizer), `hf_model_name`, `openai_model_name`, `max_tokens` (Integer), `doc_key` (String).

4. **Export DoclingDocument** — exports `DoclingDocument` to Markdown, HTML, Plaintext, or DocTags.
   - Parameters: `data_inputs`, `export_format` (Markdown/HTML/Plaintext/DocTags), `image_mode` (`placeholder`/`embedded`), `md_image_placeholder`, `md_page_break_placeholder`, `doc_key`.

**Reference RAG flow described in the LangFlow docs (exact pattern for the article's demo):**
1. `Docling` component ingests the file → `Export DoclingDocument` converts it (e.g. to Markdown, with images as placeholders) → feeds into a **Split Text** component.
2. **Split Text**'s `Chunks` output → **Chroma DB** vector store component.
3. An **embedding model** component → Chroma DB's `Embedding` port; a **Chat Output** component can be wired up to inspect the extracted Table output.
4. Configure the embedding model (credentials etc.), attach a file to the `Docling` component, click **Playground** to run — the chunked document gets embedded and loaded into the vector database.

There's also an official video tutorial referenced: *"Docling + Langflow: Document Processing for AI Workflows"* (linked from the LangFlow docs page).

## 8. Ecosystem / other integrations & notable framework support

Source: https://docling-project.github.io/docling/integrations/

Full "Agentic / AI dev frameworks" integration list: Bee Agent Framework, Crew AI, Haystack, Hector, **LangChain**, **Langflow**, **LlamaIndex**, Semantica, txtai. Plus a "Featured" and "More integrations" catalog beyond this (not fully enumerated in this pass, but the category structure alone signals broad ecosystem reach — vector DBs, agent frameworks, and enterprise platforms all have first-party or community Docling connectors).

README also calls out: 🔒 local execution for sensitive/air-gapped environments, 🔌 MCP server connectivity ("connect to any agent"), 🌐 `docling-serve` API server for running Docling as a hosted service — all relevant if the article wants to contrast "local/offline Docling" vs "Docling Serve as a microservice" deployment models (this maps directly onto the two LangFlow ingestion components above).

## Reference URLs (for article citations)

- https://github.com/docling-project/docling — main repo/README
- https://docling-project.github.io/docling/concepts/architecture/ — architecture concept page
- https://docling-project.github.io/docling/concepts/chunking/ — chunking concept page (HybridChunker, HierarchicalChunker, LineBasedTokenChunker)
- https://docling-project.github.io/docling/usage/ — basic usage (Python + CLI)
- https://docling-project.github.io/docling/integrations/ — integrations index
- https://docling-project.github.io/docling/integrations/langflow/ — Docling's own Langflow integration pointer page
- https://docs.langflow.org/bundles-docling — LangFlow's official Docling bundle docs (components, parameters, reference flow)
- https://huggingface.co/docling-project/SmolDocling-256M-preview — SmolDocling model card
- https://arxiv.org/abs/2503.11576 — SmolDocling paper
- https://huggingface.co/ibm-granite/granite-docling-258M — Granite-Docling (SmolDocling's successor) model card, incl. head-to-head benchmarks
- https://arxiv.org/abs/2408.09869 — Docling Technical Report
- https://arxiv.org/abs/2305.03393 — Lysak et al. 2023, "Optimized Table Tokenization for Table Structure Recognition" (OTSL)
