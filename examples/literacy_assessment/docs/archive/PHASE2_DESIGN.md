# Phase 2 Design: Interactive Conversation Flow

**Feature**: Interactive AI Literacy Assessment with Conversational Discovery

**Status**: Design Document (Not Yet Implemented)

**Date**: 2025-11-03

---

## Overview

**Current State (Phase 1)**:
- User explicitly provides: level + background in one request
- System generates 10 questions immediately
- Direct, single-shot assessment

**Phase 2 Enhancement**:
- Agent initiates conversation with user
- Asks 2-3 background questions first
- Adapts assessment difficulty based on responses
- More engaging, personalized experience

---

## User Flow

### Step 1: Initial Greeting

**Agent** opens with welcoming message:

```
Hello! I'm your AI Literacy Assessment Assistant.

I'll help you discover your AI knowledge level through a friendly conversation.
Think of me as your personal AI learning companion.

How I Can Help You:
• Understand your current AI knowledge
• Explore areas where you'd like to grow
• Find the right learning resources for your goals

Let's get started! I'd love to learn about your role and experience with AI.
```

### Step 2: Background Discovery (2-3 Questions)

**Question 1: Role & Domain**

```
Agent: What is your current role? (e.g., Finance Analyst, Software Developer, HR Manager, Marketing Specialist)
```

**User response examples**:
- "I'm a financial analyst"
- "Software developer"
- "I work in HR"

**Question 2: AI Experience**

```
Agent: How often do you currently use AI tools in your work?

A) Never or rarely - I'm new to AI
B) Occasionally - I've tried a few AI tools
C) Regularly - I use AI tools weekly
D) Daily - AI is part of my regular workflow
```

**Question 3: Learning Goals**

```
Agent: What's your main goal with AI? For example:

A) Understand AI capabilities and how to use basic tools
B) Automate repetitive tasks in my daily work
C) Build AI solutions for my team or organization
D) Lead AI transformation initiatives
E) Something else (please specify)
```

### Step 3: Initial Level Calibration

Based on responses, agent determines starting level:

| Goal | AI Usage | Starting Level |
|------|----------|----------------|
| Understand AI | Never/Rarely | Level 1 |
| Automate tasks | Occasionally | Level 1-2 |
| Build solutions | Regularly | Level 2-3 |
| Lead transformation | Daily | Level 3-4 |

### Step 4: Adaptive Assessment (5-7 Questions)

Agent generates questions ONE AT A TIME, adapting based on responses:

**Adaptation Rules**:
- **User answers 2+ questions correctly** → Jump up one level
- **User struggles with 2+ questions** → Adjust down one level
- **Mixed performance** → Stay at current level, vary question types

**Questioning Pattern**:

```
Agent: Great! Based on your role as a [ROLE] and your goal to [GOAL],
let me ask you a few questions to understand your AI knowledge better.

Question 1:
[Context from their domain]
[Multiple choice or open-ended question]

[Wait for response]

[Brief acknowledgment, NO detailed feedback yet]

Question 2:
...
```

### Step 5: Results & Recommendations

After 5-7 questions, agent presents results:

```
🎯 Your AI Literacy Level: [Level Name]

You're at: [Level Title] - [Description]

### ✨ Your Strengths
• [Strength 1]: You demonstrated solid understanding of [specific area]
• [Strength 2]: Your answers about [topic] show practical experience

### 📈 Growth Opportunities
• [Growth Area 1]: Developing skills in [area] will help you [benefit]
• [Growth Area 2]: Learning [technique] will enable you to [capability]

### 🎓 Your Personalized Learning Path

Start This Week (Quick Wins):
1. [Course Name] - [Why it's relevant to their role and goal]
2. [Course Name] - [Key takeaway]

Next Month (Skill Building):
3. [Course Name] - Take your [skill] to the next level
4. [Course Name] - Master [advanced technique]

### 💡 Practical Challenge
Tomorrow, try this: [Specific exercise for their level and domain]

### 🚀 Your AI Journey
[Personalized encouragement based on goals and role]
```

---

## Architecture

### Main Conversation Orchestrator

New agent: `interactive_literacy_agent`

```python
interactive_orchestrator = {
    "name": "interactive-literacy-orchestrator",
    "description": "Conducts interactive conversation to assess AI literacy",
    "system_prompt": """You are an AI Literacy Mentor conducting a friendly assessment conversation.

**Conversation Flow**:

1. GREETING PHASE:
   - Welcome user warmly
   - Explain the process (2-3 background questions, then 5-7 assessment questions)
   - Ask for their role

2. BACKGROUND DISCOVERY PHASE (2-3 questions):
   - Question 1: Role & domain (Finance, IT, HR, Marketing, Operations)
   - Question 2: AI tool usage frequency (Never, Occasionally, Regularly, Daily)
   - Question 3: Learning goal (Understand, Automate, Build, Lead)

3. CALIBRATION:
   Based on responses, determine starting level:
   - "Understand AI" + "Never" → Level 1
   - "Automate tasks" + "Occasionally" → Level 2
   - "Build solutions" + "Regularly" → Level 3
   - "Lead transformation" + "Daily" → Level 4

4. ADAPTIVE ASSESSMENT PHASE (5-7 questions):
   - Call appropriate level-specific subagent for first question
   - Track performance:
     * 2+ correct → jump up one level
     * 2+ struggling → adjust down one level
     * Mixed → stay current, vary format
   - Present questions ONE AT A TIME
   - Acknowledge briefly (NO detailed feedback during assessment)

5. RESULTS PHASE:
   - Determine final level based on overall performance
   - Present strengths, growth areas, learning path
   - Provide personalized encouragement

**Critical Rules**:
- ONE question at a time (wait for response before next)
- During assessment: brief acknowledgments only ("Got it", "Thanks")
- Save detailed feedback for final results
- Adapt difficulty based on performance patterns
- Use user's domain for all question scenarios
""",
    "tools": [],  # Calls level subagents dynamically
    "subagents": [
        level_1_subagent,
        level_2_subagent,
        level_3_subagent,
        level_4_subagent,
    ]
}
```

### State Management

Track conversation state:

```python
class ConversationState(BaseModel):
    """State for interactive conversation."""

    # Background info
    user_role: Optional[str] = None
    user_domain: str = "general"  # Finance, IT, HR, Marketing, Operations
    ai_usage_frequency: Optional[str] = None  # Never, Occasionally, Regularly, Daily
    learning_goal: Optional[str] = None  # Understand, Automate, Build, Lead

    # Assessment state
    current_phase: str = "greeting"  # greeting, background, assessment, results
    current_level: int = 1  # Current assessment level
    questions_asked: int = 0
    questions_correct: int = 0
    questions_struggled: int = 0

    # Performance tracking
    level_history: List[int] = Field(default_factory=list)  # Track level changes
    responses: List[dict] = Field(default_factory=list)  # User responses

    def should_level_up(self) -> bool:
        """Check if user should move up a level."""
        recent_correct = sum(1 for r in self.responses[-3:] if r.get("correct"))
        return recent_correct >= 2

    def should_level_down(self) -> bool:
        """Check if user should move down a level."""
        recent_struggling = sum(1 for r in self.responses[-3:] if not r.get("correct"))
        return recent_struggling >= 2

    def determine_final_level(self) -> int:
        """Determine final literacy level based on performance."""
        if self.questions_correct / self.questions_asked >= 0.8:
            return min(4, self.current_level + 1)
        elif self.questions_correct / self.questions_asked >= 0.6:
            return self.current_level
        else:
            return max(1, self.current_level - 1)
```

### Question Selection Strategy

```python
def select_next_question(
    state: ConversationState,
    level: int,
    domain: str
) -> dict:
    """
    Select next question based on current state.

    Strategy:
    - Questions 1-2: Start at calibrated level
    - Questions 3-4: Adjust based on performance
    - Questions 5-7: Fine-tune and confirm level

    Mix:
    - 70% multiple choice (easier to evaluate in conversation)
    - 30% open-ended (for depth understanding)
    """

    # Determine question type
    if state.questions_asked < 5:
        # First 5: mostly MC for quick calibration
        question_type = "multiple_choice" if state.questions_asked % 3 != 2 else "open_ended"
    else:
        # Last 2: confirm with open-ended
        question_type = "open_ended"

    # Call appropriate level subagent
    subagent_map = {
        1: "level-1-assessment-agent",
        2: "level-2-assessment-agent",
        3: "level-3-assessment-agent",
        4: "level-4-assessment-agent",
    }

    # Generate ONE question using subagent
    # (Modify subagent to support single-question mode)
    return generate_single_question(
        level=level,
        domain=domain,
        question_type=question_type,
        subagent=subagent_map[level]
    )
```

---

## Implementation Tasks

### T800 Series: Phase 2 Foundation

- [ ] T800 [P2] [Phase2] Create `ConversationState` Pydantic model
  - File: `examples/literacy-assessment/conversation_state.py`
  - Track user background, current phase, performance history

- [ ] T801 [P2] [Phase2] Implement `interactive_literacy_agent.py`
  - Main conversation orchestrator
  - 5-phase flow (greeting, background, calibration, assessment, results)

- [ ] T802 [P2] [Phase2] Add single-question generation mode to level subagents
  - Modify subagent prompts to support generating ONE question at a time
  - Add `question_type` parameter (multiple_choice or open_ended)

### T810 Series: Adaptive Logic

- [ ] T810 [P2] [Phase2] Implement `select_next_question()` function
  - Dynamic question selection based on performance
  - Level adjustment logic (jump up/down based on responses)

- [ ] T811 [P2] [Phase2] Implement response evaluation
  - Real-time evaluation of user responses
  - Track correct/struggled patterns
  - Trigger level adjustments

- [ ] T812 [P2] [Phase2] Implement `determine_final_level()` logic
  - Calculate final literacy level from conversation
  - Consider overall performance + level history

### T820 Series: Results Presentation

- [ ] T820 [P2] [Phase2] Create results formatter
  - Parse conversation history
  - Identify strengths and growth areas
  - Generate personalized learning path recommendations

- [ ] T821 [P2] [Phase2] Add course recommendation engine
  - Map level + domain → relevant courses
  - Prioritize based on learning goals
  - Format with clear next steps

### T830 Series: Testing & Polish

- [ ] T830 [P2] [Phase2] Test full conversation flow
  - Greeting → Background → Assessment → Results
  - Verify level adaptation works correctly
  - Test all domain × level combinations

- [ ] T831 [P2] [Phase2] Test adaptive difficulty
  - Verify level-up triggers (2+ correct)
  - Verify level-down triggers (2+ struggling)
  - Test mixed performance scenarios

- [ ] T832 [P2] [Phase2] Create interactive CLI
  - Command-line interface for testing conversations
  - Real-time question-response loop
  - Display results at end

---

## Example Conversation

```
Agent: Hello! I'm your AI Literacy Assessment Assistant. I'll help you discover
your AI knowledge level through a friendly conversation. Let's get started!

What is your current role?

User: I'm a financial analyst

Agent: Great! How often do you currently use AI tools in your work?
A) Never or rarely
B) Occasionally
C) Regularly
D) Daily

User: B

Agent: Thanks! What's your main goal with AI?
A) Understand AI capabilities
B) Automate repetitive tasks
C) Build AI solutions
D) Lead AI transformation

User: B

Agent: Perfect! Based on your role as a financial analyst wanting to automate
tasks, let me ask you a few questions to understand your AI knowledge better.

Question 1 (of 5-7):
You want to use AI to automate monthly budget variance reports. Which approach
would be most effective?

A) Have AI generate complete reports independently
B) Use AI to draft reports for your review and refinement
C) Use AI only for data aggregation, write reports manually
D) Keep current manual process but use AI for formatting

User: B

Agent: Got it, thanks.

Question 2 (of 5-7):
[Next question based on correct response - might level up]

...

[After 5-7 questions]

Agent:
🎯 Your AI Literacy Level: AI Practitioner (Level 2)

You're at: AI Practitioner - You have solid foundational knowledge and are
ready to apply AI tools effectively in your work.

### ✨ Your Strengths
• Strong understanding of AI-human collaboration workflows
• Practical grasp of when to use AI vs manual approaches
• Good intuition about data privacy in financial contexts

### 📈 Growth Opportunities
• Advanced prompting techniques for complex financial analysis
• Workflow automation across multiple tools
• Building custom AI workflows for recurring tasks

### 🎓 Your Personalized Learning Path

Start This Week:
1. Advanced Prompt Engineering (30 min) - Learn chain-of-thought prompting
   for complex financial calculations
2. AI for Financial Reporting (45 min) - Automate variance analysis and
   report generation

Next Month:
3. Multi-Tool AI Workflows - Coordinate multiple AI tools for end-to-end
   automation
4. AI Governance in Finance - Ensure compliance and auditability

### 💡 Practical Challenge
Tomorrow, try this: Take one budget report you create regularly and write a
detailed prompt for AI to generate the first draft. Focus on giving specific
instructions about format, key metrics, and analysis depth.

### 🚀 Your AI Journey
You're well-positioned to become an AI power user in finance! Your understanding
of human-AI collaboration will serve you well as you build more sophisticated
workflows. Start with small automations and gradually expand your AI toolkit.
```

---

## Benefits of Phase 2

### User Experience
- **More engaging**: Feels like coaching, not testing
- **Less intimidating**: Questions come one at a time
- **Personalized**: Adapts to user's actual knowledge
- **Actionable**: Specific next steps based on goals

### Assessment Quality
- **More accurate**: Adapts difficulty in real-time
- **Better calibration**: Starts at right level based on goals
- **Comprehensive**: Covers multiple levels if needed
- **Fair**: Doesn't penalize for one bad answer

### Business Value
- **Higher completion rates**: More engaging flow
- **Better recommendations**: Based on goals + performance
- **Scalable**: Same flow works for all domains
- **Data-rich**: Track performance patterns over time

---

## Migration Path

### Phase 1 → Phase 2

Keep Phase 1 implementation as "Quick Assessment" mode:

```python
# Quick mode (Phase 1 - current)
quick_agent = create_literacy_assessment_agent()

# Interactive mode (Phase 2 - new)
interactive_agent = create_interactive_literacy_agent()
```

Both share same subagents, just different orchestration.

### Implementation Order

1. **Week 1**: T800-T802 (Foundation - conversation state, orchestrator)
2. **Week 2**: T810-T812 (Adaptive logic - question selection, evaluation)
3. **Week 3**: T820-T821 (Results - formatting, recommendations)
4. **Week 4**: T830-T832 (Testing, polish, CLI)

**Estimated Time**: 3-4 weeks for full Phase 2 implementation

---

## Open Questions

1. **Question bank size**: Should we pre-generate questions or generate on-demand?
   - **Recommendation**: Generate on-demand (more flexible, always fresh)

2. **Conversation length**: Fixed 5-7 questions or adaptive?
   - **Recommendation**: Adaptive (end early if level is clear after 5)

3. **Multi-language support**: Should we support multiple languages?
   - **Recommendation**: Start English-only, add translations later

4. **Conversation history**: Should we persist conversations for review?
   - **Recommendation**: Yes, store in FilesystemMiddleware for analysis

---

## Success Metrics (Phase 2)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completion rate | >85% | % users who finish conversation |
| Avg conversation time | 10-15 min | Time from greeting to results |
| Level accuracy | >90% | Manual review of 100 assessments |
| User satisfaction | >4/5 | Post-assessment survey |
| Adaptation rate | 30-50% | % assessments where level changed mid-conversation |

---

## Next Steps

1. **Review this design** with stakeholders
2. **Validate conversation flow** with sample users
3. **Start implementation** with T800 (conversation state)
4. **Test incrementally** as each component is built

For current testing (Phase 1), see `TESTING_GUIDE.md`.
