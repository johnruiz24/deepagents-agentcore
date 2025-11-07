# 🚀 Start Here: Literacy Assessment System

**Status**: ✅ MVP Complete with Background-Aware Question Generation

**Last Updated**: 2025-11-03

---

## What's Been Implemented

### ✅ Phase 1: Complete (Ready to Test!)

**Background-Aware Question Generation** - The KEY feature you requested!

The system now calibrates questions based on **DOMAIN/CONTEXT**:

| Your Background | Level 1 Questions About | Level 3 Questions About |
|----------------|------------------------|------------------------|
| **Finance** | Basic AI for reports, budgeting | Strategic forecasting, governance, ROI |
| **IT/Data Science** | AI tools for development, APIs | System architecture, agent design |
| **HR** | AI for job descriptions, hiring | Fair hiring systems, org transformation |
| **Marketing** | AI for content creation | Multi-channel campaigns, brand strategy |

**Example**:
- **Level 3 for Finance**: Strategic business questions (NOT technical implementation!)
- **Level 3 for IT**: Technical architecture questions (system design, infrastructure)

---

## How to Test RIGHT NOW

### Quick Test (5 minutes)

```python
from examples.literacy_assessment import create_literacy_assessment_agent

agent = create_literacy_assessment_agent()

# Test: Finance background, Level 1
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 1 assessment for someone who works in finance with 2 years of experience in financial reporting"
    }]
})

print(result['messages'][-1].content)
```

**What to expect**:
- 7 multiple choice + 3 open-ended questions
- Questions about: budget analysis, financial reports, ROI, compliance
- NO technical jargon (APIs, code, infrastructure)
- All scenarios use finance context

### Test Different Backgrounds

**IT Background**:
```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 1 assessment for a software developer with 3 years of experience"
    }]
})
```

Expected: Technical scenarios (APIs, code, development workflows)

**Finance Background - Advanced**:
```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 3 assessment for a senior financial analyst with 8 years of experience leading strategic planning"
    }]
})
```

Expected: Strategic business questions (ROI, governance, change management) - NOT technical implementation!

---

## Complete Testing Guide

See **`TESTING_GUIDE.md`** for:
- Prerequisites and setup
- 5 detailed test scenarios
- Verification checklists
- Troubleshooting
- Quick test scripts

**Key test scenarios**:
1. Finance Level 1 vs IT Level 1 (compare domain contexts)
2. Finance Level 1 vs Finance Level 3 (compare complexity within domain)
3. Multi-level parallel generation (performance test)

---

## What Makes This Work

### Background Calibration Logic

Each of the 4 level-specific subagents now:

1. **Parses user background** to identify domain:
   - IT/Data Science
   - Finance/Business
   - HR/People
   - Marketing/Creative
   - Operations/General

2. **Applies domain-specific scenarios**:
   - Finance: Reports, budgets, forecasting, compliance
   - IT: APIs, systems, development, infrastructure
   - HR: Hiring, training, performance, fairness
   - Marketing: Campaigns, content, personalization, brand

3. **Maintains level-appropriate complexity**:
   - Level 1: Foundational concepts
   - Level 2: Workflow automation
   - Level 3: Strategic/architectural thinking
   - Level 4: Enterprise/leadership

### Updated Files

All 4 subagent prompts enhanced in:
- `examples/literacy-assessment/literacy_agent.py`

**Lines updated**:
- Level 1: Lines 33-135 (background-aware foundational)
- Level 2: Lines 139-247 (background-aware intermediate)
- Level 3: Lines 250-363 (background-aware advanced)
- Level 4: Lines 366-478 (background-aware expert)

---

## Next Steps

### Immediate (Today)

1. **Run validation**:
   ```bash
   python -m examples.literacy_assessment.scripts.validate_config
   ```

2. **Test finance background**:
   ```bash
   python quick_test.py  # See TESTING_GUIDE.md for script
   ```

3. **Test IT background** for comparison

4. **Review questions**: Are they domain-appropriate?

### This Week

1. Test all 5 domains × 4 levels = 20 combinations
2. Collect sample assessments for quality review
3. Identify any prompt tuning needed
4. Document findings

### Phase 2 (Future - Interactive Flow)

See **`PHASE2_DESIGN.md`** for the interactive conversation flow design:

**Phase 2 Vision**:
- Agent asks user background questions first
- Generates questions one at a time
- Adapts difficulty based on responses
- Presents personalized results with learning paths

**Implementation**: 3-4 weeks (detailed task breakdown in design doc)

---

## Key Differences: Phase 1 vs Phase 2

### Phase 1 (Current - ✅ Complete)

**User interaction**:
```
User: "Generate Level 2 for finance analyst with 3 years experience"
Agent: [Returns complete 10-question assessment immediately]
```

**Pros**: Fast, direct, batch generation possible

**Use case**: When you already know the level to test

### Phase 2 (Future - Design Complete)

**User interaction**:
```
Agent: "What's your role?"
User: "Finance analyst"
Agent: "How often use AI?"
User: "Occasionally"
Agent: "Main goal?"
User: "Automate tasks"
Agent: "Great! Question 1..."
[Asks 5-7 questions adaptively]
Agent: "Your Level: AI Practitioner (Level 2). Here's your learning path..."
```

**Pros**: More engaging, adaptive, personalized

**Use case**: When user doesn't know their level, wants guided experience

---

## File Structure

```
examples/literacy-assessment/
├── docs/                      ← Documentation
│   ├── START_HERE.md          ← You are here - Quick start guide
│   ├── TESTING_GUIDE.md       ← Detailed testing instructions
│   ├── PHASE2_DESIGN.md       ← Future interactive flow design
│   └── README.md              ← Complete documentation
├── src/                       ← Core source code
│   ├── agent.py               ← ✅ Main agent with background-aware prompts
│   ├── config.py              ← AWS Bedrock configuration
│   ├── models.py              ← Pydantic data models
│   ├── kb_tools.py            ← Knowledge Base query functions
│   └── questions.py           ← Question validation utilities
├── scripts/                   ← Utility scripts
│   ├── validate_config.py     ← Config validation
│   └── example_usage.py       ← Usage examples
├── tests/                     ← Unit tests
├── __init__.py                ← Module exports
└── requirements.txt           ← Python dependencies
```

---

## Questions & Answers

### Q: How does it know I'm from Finance vs IT?

**A**: The subagent prompt explicitly instructs: "Parse the user background to identify their domain (IT, Finance, HR, Marketing, Operations, etc.)"

The LLM looks for keywords like:
- "finance", "financial analyst", "budget" → Finance domain
- "software", "developer", "engineer" → IT domain
- "HR", "recruitment", "hiring" → HR domain
- etc.

### Q: What if I want Level 3 technical questions for Finance?

**A**: You don't! That's the insight.

Level 3 for Finance = Strategic business thinking (governance, ROI, change management)

Level 3 for IT = Strategic technical thinking (architecture, infrastructure, design patterns)

Both are "advanced" but in their respective domains.

### Q: Can I still get technical questions if I'm from Finance?

**A**: If you work in Finance but have technical responsibilities, be explicit:

```python
"Generate Level 3 for someone who works in Finance Technology, responsible for
implementing financial systems and APIs"
```

The agent will blend finance + technical contexts.

### Q: How do I test the interactive conversation flow (Phase 2)?

**A**: It's not implemented yet! See `PHASE2_DESIGN.md` for the design.

Current implementation (Phase 1) is direct/batch generation.

---

## Support

**For testing issues**: See `TESTING_GUIDE.md` → Troubleshooting section

**For Phase 2 questions**: See `PHASE2_DESIGN.md`

**For general usage**: See `README.md`

---

## Quick Reference

### Test Finance Level 1

```python
from examples.literacy_assessment import create_literacy_assessment_agent

agent = create_literacy_assessment_agent()

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate Level 1 for finance analyst with 2 years experience"
    }]
})

print(result['messages'][-1].content)
```

### Test IT Level 3

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate Level 3 for senior software architect with 8 years experience"
    }]
})

print(result['messages'][-1].content)
```

### Test Multi-Level Parallel

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate Levels 1, 2, and 3 for finance professional with 5 years experience"
    }]
})

print(result['messages'][-1].content)
```

---

**Ready to test? Start with `TESTING_GUIDE.md`!** 🚀
