# System Architecture

## Overview

```
User Request
     ↓
Main Orchestrator Agent
     ↓
┌────┴────┬────┬────┐
│         │    │    │
Level 1   2    3    4  (Parallel Execution)
│         │    │    │
KB-1    KB-2  KB-3 KB-4
│         │    │    │
└────┬────┴────┴────┘
     ↓
Combined Assessment JSON
```

## Components

### Main Agent
- Parses user request
- Spawns level-specific subagents
- Combines results
- Writes to filesystem

### Level Subagents (4)
- Query Bedrock Knowledge Base
- Generate 10 questions (7 MC + 3 OE)
- Calibrate to user background
- Return JSON assessment

### Bedrock KBs
- **Level 1**: QADZTSAPWX (Foundational)
- **Level 2**: KGGD2PTQ2N (Intermediate)
- **Level 3**: 7MGFSODDVI (Advanced)
- **Level 4**: 7MGFSODDVI (Expert)

## Data Flow

### Single Level
```
User → Main → Level N Agent → KB N → Results → Main → User
Time: <60s
```

### Multi-Level (Parallel)
```
User → Main → [Level 1, 2, 3] → [KB 1, 2, 3] → Results → Main → User
                  (Parallel)         (Parallel)
Time: ~60% of sequential
```

## Question Format

### Multiple Choice (70%)
```json
{
  "type": "multiple_choice",
  "question": "What is...",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "A",
  "module": "Introduction to AI"
}
```

### Open-Ended (30%)
```json
{
  "type": "open_ended",
  "question": "Explain...",
  "module": "Practical Applications"
}
```

## Deployment

```
AWS Bedrock AgentCore
├── Docker Container (linux/arm64)
│   ├── serve_bedrock.py
│   ├── literacy_agent.py
│   └── deepagents library
├── IAM Role (bedrock:Retrieve)
└── Memory (STM_ONLY)
```

## Performance

| Metric | Target | Typical |
|--------|--------|---------|
| Single level | <60s | ~40-50s |
| Multi-level (3) | <60s | ~50-55s |
| Parallel speedup | 60%+ | ~65-70% |
| Module coverage | 5+ | 6-7 |
