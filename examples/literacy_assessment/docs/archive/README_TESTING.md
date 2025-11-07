# Literacy Assessment System - Testing Guide

## Quick Start

### Run Comprehensive Test (All 4 Levels)

```bash
source .venv/bin/activate
python run_comprehensive_test.py
```

This will:
- Test all 4 literacy levels (L1, L2, L3, L4)
- Use Sonnet 4 fallback model (to avoid throttling)
- Generate assessments for different backgrounds (Finance, IT, Data Science, CTO)
- Save results with KB document references
- Create detailed logs

### Output Structure

```
output/
├── assessments/           # Generated assessments
│   ├── level_1_TIMESTAMP.json      # Full assessment with KB sources
│   ├── level_1_TIMESTAMP.md        # Human-readable markdown
│   ├── level_2_TIMESTAMP.json
│   ├── level_2_TIMESTAMP.md
│   ├── level_3_TIMESTAMP.json
│   ├── level_3_TIMESTAMP.md
│   ├── level_4_TIMESTAMP.json
│   └── level_4_TIMESTAMP.md
└── logs/                  # Execution logs
    └── test_run_TIMESTAMP.log      # Detailed execution log
```

## What You'll See in the Results

### JSON Files

Each JSON file includes:
```json
{
  "level": 1,
  "multiple_choice_questions": [...],
  "open_ended_questions": [...],
  "modules_covered": [...],
  "kb_document_sources": [          ← PDF references!
    {
      "filename": "module_1_fundamentals.pdf",
      "s3_uri": "s3://bucket/path/module_1_fundamentals.pdf"
    },
    ...
  ]
}
```

### Markdown Files

Human-readable format with:
- Assessment overview (level, question counts, modules)
- **📄 Knowledge Base Document Sources** - List of PDFs where content was extracted
- All multiple choice questions with answers and explanations
- All open-ended questions with evaluation criteria

### Log Files

Detailed execution log showing:
- Timestamps for each operation
- Model being used
- Generation times
- Parsing results
- KB document extraction
- Any errors with full stack traces

## Folder Structure

```
examples/literacy_assessment/
├── run_comprehensive_test.py       # Main test script (USE THIS!)
├── __init__.py                     # Module exports
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
│
├── src/                            # Core source code
│   ├── agent.py                    # Main agent + 4 subagents
│   ├── config.py                   # Configuration
│   ├── models.py                   # Pydantic models
│   ├── kb_tools.py                 # KB query functions (NOW with document tracking!)
│   └── questions.py                # Question utilities
│
├── docs/                           # Documentation
│   ├── README.md                   # Complete system docs
│   ├── START_HERE.md               # Quick start
│   ├── TESTING_GUIDE.md            # Testing scenarios
│   ├── PHASE2_DESIGN.md            # Future enhancements
│   └── ...
│
├── scripts/                        # Utility scripts
│   ├── validate_config.py          # Config validation
│   └── example_usage.py            # Usage examples
│
├── tests/                          # Tests
│   ├── test_config.py              # Unit tests
│   ├── test_models.py
│   ├── test_question_gen.py
│   └── archived/                   # Old test scripts (historical)
│
├── output/                         # Generated output
│   ├── assessments/                # JSON + Markdown assessments
│   └── logs/                       # Execution logs
│
└── .venv/                          # Python virtual environment
```

## Understanding the Output

### KB Document Sources

The system now tracks which PDFs/documents from the Knowledge Base were used to generate each question. In the markdown files, you'll see:

```markdown
### 📄 Knowledge Base Document Sources

*Questions generated from content in these documents:*

- **module_1_ai_fundamentals.pdf**
  `s3://literacy-kb-bucket/level-1/module_1_ai_fundamentals.pdf`
- **module_3_prompt_engineering.pdf**
  `s3://literacy-kb-bucket/level-1/module_3_prompt_engineering.pdf`
...
```

This shows:
1. **Which PDFs** were retrieved from the Knowledge Base
2. **Full S3 paths** to the source documents
3. **Proof** that questions are generated from actual KB content

### Log File Example

```
[2025-11-03 19:30:45] ================================================================================
[2025-11-03 19:30:45] Testing Level 1
[2025-11-03 19:30:45] ================================================================================
[2025-11-03 19:30:45]
[2025-11-03 19:30:45] Background: a finance analyst with 2 years of experience in financial reporting
[2025-11-03 19:30:45] Using model: eu.anthropic.claude-sonnet-4-20250514-v1:0
[2025-11-03 19:30:45] Creating agent...
[2025-11-03 19:30:46] Agent created ✓
[2025-11-03 19:30:46] Generating assessment...
[2025-11-03 19:33:01] Assessment generated in 135.42s ✓
[2025-11-03 19:33:01] Parsing assessment...
[2025-11-03 19:33:01] Parsed: 7 MC + 3 OE = 10 questions, 7 modules ✓
[2025-11-03 19:33:01] Extracting KB document sources...
[2025-11-03 19:33:01] Found 12 document sources ✓
[2025-11-03 19:33:01] Saved JSON: output/assessments/level_1_20251103_193001.json ✓
[2025-11-03 19:33:01] Saved Markdown: output/assessments/level_1_20251103_193001.md ✓
```

## Models Used

The test uses fallback models to avoid throttling:

- **Primary**: Sonnet 4 (`eu.anthropic.claude-sonnet-4-20250514-v1:0`)
- **Fast**: Claude 3.7 Sonnet (`eu.anthropic.claude-3-7-sonnet-20250219-v1:0`)

These have separate rate limits from Sonnet 4.5/Haiku 4.5.

## Troubleshooting

### Throttling Errors

If you still see throttling:
1. Wait 15-30 minutes between test runs
2. Check AWS Bedrock quotas in AWS Console
3. Request quota increases if needed

### Missing KB Document Sources

If `kb_document_sources` is empty in JSON:
1. Check that KB documents have S3 metadata
2. Verify KB sync is complete
3. Check KB permissions

### Import Errors

Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
```

## What's Been Fixed

✅ **Organized test files** - All old tests moved to `tests/archived/`
✅ **KB document tracking** - All 4 KB query tools now return `document_sources`
✅ **Proper logging** - Detailed timestamped logs in `output/logs/`
✅ **PDF references in output** - Both JSON and Markdown show source documents
✅ **Clean folder structure** - No more messy root directory!

## Next Steps

After running the test successfully:
1. Check `output/assessments/` for the generated assessments
2. Review `output/logs/` for execution details
3. Verify KB document sources are shown
4. Compare questions across different levels and backgrounds
