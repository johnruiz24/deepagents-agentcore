# Testing Guide: Literacy Level Assessment System

**Purpose**: Step-by-step instructions for testing the literacy assessment agent with different backgrounds and levels.

**Date**: 2025-11-03

---

## Prerequisites

### 1. Install Dependencies

```bash
# From project root
cd examples/literacy-assessment
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Ensure your `~/.aws/credentials` file has the `mll-dev` profile:

```ini
[mll-dev]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### 3. Verify Configuration

```bash
python -m examples.literacy_assessment.scripts.validate_config
```

Expected output:
```
✓ AWS credentials configured (profile: mll-dev)
✓ Knowledge Base Level 1: QADZTSAPWX (accessible)
✓ Knowledge Base Level 2: KGGD2PTQ2N (accessible)
✓ Knowledge Base Level 3: 7MGFSODDVI (accessible)
✓ Knowledge Base Level 4: 7MGFSODDVI (accessible)
✓ Configuration complete!
```

---

## Testing Approach

### Understanding Background Calibration

The system now calibrates questions based on **DOMAIN/CONTEXT**, not just difficulty:

| Background | Level 1 | Level 3 | Level 4 |
|------------|---------|---------|---------|
| **IT/Data Science** | Basic AI tools for development | System architecture, agent design | Multi-agent orchestration, platform strategy |
| **Finance** | AI for basic reporting | Strategic forecasting, governance | Enterprise AI strategy, board-level decisions |
| **HR** | AI for job descriptions | Fair hiring processes, ethics | Organizational transformation at scale |
| **Marketing** | AI for content creation | Multi-channel campaigns | Brand AI strategy, market leadership |

**Key Insight**: A Level 3 Finance person gets strategic business questions, NOT technical implementation questions!

---

## Test Scenarios

### Scenario 1: Finance Background - Level 1

**Background**: "I work in finance with 2 years of experience in financial analysis and reporting."

**Expected Questions**:
- AI basics applied to financial reporting
- Simple prompt engineering for budget analysis
- Data privacy for financial data
- Basic AI tool selection for finance tasks

**NOT Expected**:
- Technical implementation details
- Code or API references
- System architecture

**Test Command**:

```python
from examples.literacy_assessment import create_literacy_assessment_agent

agent = create_literacy_assessment_agent()

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 1 assessment for someone who works in finance with 2 years of experience in financial analysis and reporting"
    }]
})

print(result['messages'][-1].content)
```

**What to Verify**:
- [ ] 7 multiple choice + 3 open-ended questions
- [ ] Questions use finance/business scenarios (budget, reports, ROI, compliance)
- [ ] Questions avoid technical jargon (APIs, infrastructure, code)
- [ ] 5+ different modules covered
- [ ] All MC options seem plausible (no obviously wrong answers)

---

### Scenario 2: IT Background - Level 1

**Background**: "I'm a software developer with 3 years of experience building web applications."

**Expected Questions**:
- AI basics applied to development workflows
- Prompt engineering for code generation
- AI tools for debugging/testing
- Data privacy in development contexts

**Expected Technical Depth**:
- Can mention APIs, logs, code, systems
- Should still be foundational concepts
- NOT system architecture or infrastructure

**Test Command**:

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 1 assessment for a software developer with 3 years of experience building web applications"
    }]
})

print(result['messages'][-1].content)
```

**What to Verify**:
- [ ] 7 multiple choice + 3 open-ended questions
- [ ] Questions use technical scenarios (APIs, logs, testing, development)
- [ ] Questions use appropriate technical vocabulary
- [ ] 5+ different modules covered
- [ ] Difficulty appropriate for foundational level (not architecture/design patterns)

---

### Scenario 3: Finance Background - Level 3

**Background**: "I'm a senior financial analyst with 8 years of experience, leading forecasting and strategic planning initiatives."

**Expected Questions**:
- Strategic AI implementation for finance
- Building business cases for AI investment
- Governance frameworks for financial AI
- Change management for finance teams

**NOT Expected**:
- System architecture or technical implementation
- Code, APIs, or infrastructure details
- DevOps or deployment strategies

**Test Command**:

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 3 assessment for a senior financial analyst with 8 years of experience, leading forecasting and strategic planning initiatives"
    }]
})

print(result['messages'][-1].content)
```

**What to Verify**:
- [ ] 7 multiple choice + 3 open-ended questions
- [ ] Questions focus on STRATEGY and BUSINESS VALUE (not technical implementation)
- [ ] Scenarios involve: ROI, risk management, stakeholder buy-in, governance
- [ ] Questions require understanding of trade-offs (cost vs capability, risk vs innovation)
- [ ] 5+ different modules covered
- [ ] All MC options are sophisticated strategies (require careful analysis)

---

### Scenario 4: IT Background - Level 3

**Background**: "I'm a senior software architect with 8 years of experience designing distributed systems and leading technical teams."

**Expected Questions**:
- System architecture for AI agents
- Agent design patterns and orchestration
- Production deployment and monitoring
- Technical governance and tool integration

**Expected Technical Depth**:
- System design, architecture patterns
- Infrastructure, scalability, reliability
- Technical trade-offs and decisions
- BUT still focused on AI/agent-specific topics

**Test Command**:

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 3 assessment for a senior software architect with 8 years of experience designing distributed systems and leading technical teams"
    }]
})

print(result['messages'][-1].content)
```

**What to Verify**:
- [ ] 7 multiple choice + 3 open-ended questions
- [ ] Questions focus on TECHNICAL ARCHITECTURE (system design, infrastructure)
- [ ] Scenarios involve: agent architecture, production deployment, monitoring, scaling
- [ ] Questions require understanding of technical trade-offs
- [ ] 5+ different modules covered
- [ ] All MC options are valid architectural approaches

---

### Scenario 5: Multi-Level Parallel (Finance Background)

**Background**: "I'm a finance professional with 5 years of experience. I want to understand my AI literacy across multiple levels."

**Expected Behavior**:
- Agent generates assessments for Levels 1, 2, and 3 in PARALLEL
- Each assessment uses finance-appropriate scenarios
- Total time < 60% of sequential generation time

**Test Command**:

```python
import time

start = time.time()

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate assessments for Levels 1, 2, and 3 for a finance professional with 5 years of experience"
    }]
})

duration = time.time() - start

print(f"Total time: {duration:.2f}s")
print(result['messages'][-1].content)
```

**What to Verify**:
- [ ] 3 assessments generated (Levels 1, 2, 3)
- [ ] Each has 7 MC + 3 OE questions
- [ ] All use finance-appropriate scenarios
- [ ] Total time ideally < 60s (with parallel execution)
- [ ] Performance metrics included in output

---

## Verification Checklist

For **each** test scenario, verify:

### Question Format
- [ ] Exactly 7 multiple choice questions
- [ ] Exactly 3 open-ended questions
- [ ] Each MC has 4 options (A-D)
- [ ] Correct answer marked for each MC
- [ ] Each OE has 3-5 expected key points

### Domain Calibration
- [ ] Questions match user's background domain
- [ ] Technical depth appropriate for domain (IT vs Finance vs HR, etc.)
- [ ] Scenarios use domain-relevant examples
- [ ] Vocabulary appropriate for domain

### Level Calibration
- [ ] Level 1: Foundational concepts, basic application
- [ ] Level 2: Intermediate complexity, workflow coordination
- [ ] Level 3: Advanced/strategic, system thinking
- [ ] Level 4: Expert/leadership, organizational transformation

### Quality Standards
- [ ] All MC options are plausible (no obviously wrong answers)
- [ ] Questions force trade-off decisions
- [ ] Realistic constraints included
- [ ] 5+ different modules covered

### Output Format
- [ ] Valid JSON structure
- [ ] All required fields present
- [ ] Modules list has 5+ unique entries
- [ ] Generated timestamp included

---

## Common Issues & Troubleshooting

### Issue: Questions are too technical for finance background

**Diagnosis**: Subagent not properly parsing background

**Check**: Look at the questions - are they about APIs, code, infrastructure?

**Fix**: The updated prompts emphasize domain parsing. If still seeing this:
1. Make background more explicit: "I work in FINANCE" (emphasize)
2. Check subagent prompt is using latest version

### Issue: Questions too easy/obvious

**Diagnosis**: Not following quality standards (all options plausible)

**Check**: Can you eliminate 2+ MC options immediately?

**Expected**: All 4 options should seem reasonable, requiring careful analysis

**Fix**: The updated prompts emphasize "all options must seem plausible" - agent should self-correct

### Issue: Not enough module diversity (< 5 modules)

**Diagnosis**: KB queries not targeting diverse content

**Check**: Look at modules_covered list

**Fix**: Ensure KB has content across multiple modules. If KB content is limited, this is a data issue.

### Issue: Generation takes > 60 seconds

**Diagnosis**: KB queries are slow or agent is making too many queries

**Check**: Time individual KB queries using boto3 directly

**Potential causes**:
- KB not fully indexed
- Network latency to AWS
- Too many sequential queries (should be < 10 per level)

---

## Advanced Testing

### Test Calibration Accuracy

Generate assessments for the SAME level but DIFFERENT backgrounds:

```python
# Finance Level 2
result_finance = agent.invoke({
    "messages": [{"role": "user", "content": "Generate Level 2 for finance analyst with 4 years experience"}]
})

# IT Level 2
result_it = agent.invoke({
    "messages": [{"role": "user", "content": "Generate Level 2 for software engineer with 4 years experience"}]
})
```

**Compare**:
- Finance should have: ROI, budgets, forecasting, compliance scenarios
- IT should have: APIs, workflows, automation, technical implementation scenarios
- Both should have SAME difficulty/complexity level

### Test Level Progression

Generate assessments for the SAME background but DIFFERENT levels:

```python
# Level 1 Finance
result_l1 = agent.invoke({
    "messages": [{"role": "user", "content": "Generate Level 1 for finance analyst"}]
})

# Level 3 Finance
result_l3 = agent.invoke({
    "messages": [{"role": "user", "content": "Generate Level 3 for senior finance analyst"}]
})
```

**Compare**:
- Level 1: Basic concepts, simple prompting, tool awareness
- Level 3: Strategic thinking, governance, change management
- Both should use FINANCE scenarios

---

## Quick Test Script

Save this as `quick_test.py`:

```python
from examples.literacy_assessment import create_literacy_assessment_agent
import json

agent = create_literacy_assessment_agent()

# Test: Finance Level 1
print("=" * 70)
print("TEST: Finance Background - Level 1")
print("=" * 70)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 1 assessment for someone who works in finance with 2 years of experience in financial reporting"
    }]
})

# Parse result
assessment_json = result['messages'][-1].content
assessment = json.loads(assessment_json)

print(f"Level: {assessment['level']}")
print(f"Modules covered: {len(assessment.get('modules_covered', []))}")
print(f"MC questions: {len(assessment['multiple_choice_questions'])}")
print(f"OE questions: {len(assessment['open_ended_questions'])}")

print("\nFirst MC Question:")
print(f"Q: {assessment['multiple_choice_questions'][0]['question_text']}")
print(f"Module: {assessment['multiple_choice_questions'][0]['module_source']}")

print("\nFirst OE Question:")
print(f"Q: {assessment['open_ended_questions'][0]['question_text']}")
print(f"Module: {assessment['open_ended_questions'][0]['module_source']}")

print("\nAll Modules Covered:")
for module in assessment.get('modules_covered', []):
    print(f"  - {module}")
```

Run:
```bash
python quick_test.py
```

---

## Next Steps

After verifying the basic functionality:

1. **Test all domain-level combinations** (5 domains × 4 levels = 20 combinations)
2. **Test multi-level parallel execution** for performance
3. **Collect sample assessments** for quality review
4. **Identify any domain/level combinations** that need prompt tuning

For Phase 2 (interactive conversation flow), see `PHASE2_DESIGN.md`.
