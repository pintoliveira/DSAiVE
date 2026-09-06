# Document Paragraph Chunking & Processing

## Overview

Your thesis document has been extracted into **448 paragraphs**. Use these tools to apply prompts to each paragraph sequentially.

## Quick Start

### 1. **Extract Paragraphs Only** (No API calls)
```bash
python3 paragraph_chunker.py
```

**Output:**
- `paragraphs.json` - All paragraphs with indices
- `paragraphs.csv` - Spreadsheet-friendly format

### 2. **Process with Claude API** (Sequential, one paragraph at a time)
```bash
python3 process_paragraphs.py
```

This will:
1. Extract all paragraphs
2. Show you a sample
3. Ask for confirmation
4. Process each paragraph sequentially with Claude
5. Save results to `results.json`

## Document Statistics

| Metric | Value |
|--------|-------|
| **Total Paragraphs** | 448 |
| **Total Characters** | 101,773 |
| **Avg per Paragraph** | 227 chars |
| **Longest Paragraph** | 1,439 chars |
| **Shortest Paragraph** | 2 chars |

## Customizing Your Prompt

Edit `process_paragraphs.py` and modify the `prompt_template`:

```python
prompt_template = """Analyze the following paragraph:

{paragraph}

Provide:
1. Key concepts
2. Main arguments
3. One-sentence summary"""
```

The `{paragraph}` placeholder will be replaced with each paragraph text.

## Output Format

### paragraphs.json
```json
{
  "total_paragraphs": 448,
  "paragraphs": [
    {
      "index": 0,
      "text": "Techno-economic and environmental..."
    },
    ...
  ]
}
```

### results.json (after processing)
```json
{
  "total_processed": 10,
  "total_paragraphs": 448,
  "results": [
    {
      "index": 0,
      "original_length": 125,
      "result": "Claude's response here..."
    },
    ...
  ]
}
```

## Processing Options

### Change Claude Model
Edit line in `process_paragraphs.py`:
```python
model="claude-opus-4-1"  # Change to claude-sonnet-4, etc.
```

### Process Subset of Paragraphs
Modify the loop in `process_all_paragraphs()`:
```python
for i, para in enumerate(paragraphs[10:50], 1):  # Process only paragraphs 10-50
```

### Batch Processing with Context
Combine multiple paragraphs (e.g., by section):
```python
# In process_paragraphs.py, modify before calling process_all_paragraphs()
grouped = ['\n\n'.join(paragraphs[i:i+5]) for i in range(0, len(paragraphs), 5)]
results = process_all_paragraphs(grouped, prompt_template)
```

## Examples

### Example 1: Summarization
```python
prompt_template = """Summarize this paragraph in 2-3 sentences:

{paragraph}"""
```

### Example 2: Sentiment Analysis
```python
prompt_template = """Analyze the sentiment and tone of this paragraph:

{paragraph}

Classify as: positive, neutral, or negative"""
```

### Example 3: Keyword Extraction
```python
prompt_template = """Extract the 5 most important keywords from:

{paragraph}

Format as comma-separated list"""
```

### Example 4: Translation
```python
prompt_template = """Translate to English (if needed) and preserve technical terminology:

{paragraph}"""
```

## Files Generated

```
DSAiVE/
├── paragraph_chunker.py          # Simple extraction tool
├── process_paragraphs.py         # Main processing script
├── paragraphs.json               # All extracted paragraphs
├── paragraphs.csv                # CSV version
├── results.json                  # Processing results (generated after running)
└── PARAGRAPH_PROCESSING.md       # This file
```

## Tips

1. **Start Small**: Test with `paragraphs[0:5]` first to validate your prompt
2. **Incremental Saves**: `results.json` updates after each paragraph (safe to interrupt)
3. **Rate Limiting**: API calls are sequential (respects rate limits)
4. **Cost**: Monitor API usage - 448 paragraphs × 1-2 API calls each

## Troubleshooting

### "unzip not found"
Install unzip: `apt-get install unzip` or `brew install unzip`

### API Key Issues
Set environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Memory Issues
Process in chunks:
```python
batch_size = 50
for i in range(0, len(paragraphs), batch_size):
    batch = paragraphs[i:i+batch_size]
    results = process_all_paragraphs(batch, prompt_template)
```

## Next Steps

1. ✅ Verify extracted paragraphs: `python3 paragraph_chunker.py`
2. ✅ Customize your prompt in `process_paragraphs.py`
3. ✅ Run: `python3 process_paragraphs.py`
4. ✅ Check results in `results.json`

Questions? Let me know your specific prompt and I can optimize the setup!
