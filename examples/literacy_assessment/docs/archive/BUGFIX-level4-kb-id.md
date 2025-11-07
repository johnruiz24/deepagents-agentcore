# Critical Bug: Level 4 Using Wrong Knowledge Base

**Status**: Identified, Pending Fix
**Severity**: Critical
**Impact**: Level 4 assessments using Level 3 curriculum content
**Discovered**: 2025-11-03

## Problem Description

Level 4 assessments are incorrectly querying the Level 3 Knowledge Base instead of the dedicated Level 4 Knowledge Base. This results in Level 4 questions being generated from Level 3 (Advanced) content rather than Level 4 (Expert) content.

## Root Cause

**File**: `src/config.py`
**Line**: 33

```python
# WRONG - Currently configured
KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "7MGFSODDVI")  # Shares KB with Level 3

# CORRECT - Should be
KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "CHYWO1H6OM")  # Level 4 dedicated KB
```

**Additional Location**: `src/kb_tools.py` line 366 has a comment stating "Level 4 shares the same KB as Level 3", which is incorrect.

## Correct Knowledge Base IDs

| Level | KB ID | Description |
|-------|-------|-------------|
| Level 1 | `QADZTSAPWX` | Foundational |
| Level 2 | `KGGD2PTQ2N` | Intermediate |
| Level 3 | `7MGFSODDVI` | Advanced |
| Level 4 | `CHYWO1H6OM` | Expert (DISTINCT from Level 3) |

## Impact Analysis

### User Impact
- **Severity**: High
- **Affected Users**: Anyone taking Level 4 assessments
- **Consequence**: Level 4 questions generated from Advanced content instead of Expert content
- **Quality Impact**: Assessment difficulty and content not matching Level 4 curriculum expectations

### System Impact
- **Data Integrity**: Level 4 assessments generated so far are invalid
- **Reproducibility**: All Level 4 test runs used wrong content source
- **Metrics**: Level 4 performance data may be misleading (questions were easier than intended)

### Test Results Impact
All previous comprehensive test results showing "Level 4 success" are technically invalid because:
1. Questions came from Level 3 KB (7MGFSODDVI)
2. Module coverage reflects Level 3 modules, not Level 4
3. Document sources point to Level 3 PDFs

## Files Requiring Updates

### 1. Configuration (`src/config.py`)
**Line 33**: Change KB_LEVEL_4_ID default value
```python
# Before
KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "7MGFSODDVI")

# After
KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "CHYWO1H6OM")
```

### 2. KB Tools (`src/kb_tools.py`)
**Line 366**: Update comment
```python
# Before
Note: Level 4 shares the same KB as Level 3 (7MGFSODDVI).

# After
Note: Level 4 has dedicated expert-level KB (CHYWO1H6OM).
```

### 3. Documentation (`docs/SPEC.md`)
**Section**: Technical Constraints
```markdown
# Before
- AWS Bedrock Knowledge Base IDs: QADZTSAPWX (L1), KGGD2PTQ2N (L2), 7MGFSODDVI (L3&4)

# After
- AWS Bedrock Knowledge Base IDs: QADZTSAPWX (L1), KGGD2PTQ2N (L2), 7MGFSODDVI (L3), CHYWO1H6OM (L4)
```

### 4. Architecture Docs (`docs/PLAN.md`)
**Section**: Architecture diagram
Update KB IDs in the Knowledge Base component box

### 5. Tasks (`docs/TASKS.md`)
Add new task for KB ID correction

## Fix Procedure

1. ✅ **Document the bug** (this file)
2. ⏳ **Update config.py** - Change KB_LEVEL_4_ID default
3. ⏳ **Update kb_tools.py** - Fix comment on line 366
4. ⏳ **Update all documentation** - SPEC.md, PLAN.md, TASKS.md
5. ⏳ **Regenerate Level 4 assessments** - Validate using correct KB
6. ⏳ **Compare before/after** - Verify Level 4 questions are now expert-level
7. ⏳ **Update test results** - Document that previous Level 4 results were invalid

## Validation Plan

### Pre-Fix Verification
```bash
# Verify current (wrong) configuration
grep "KB_LEVEL_4_ID" src/config.py
# Expected: KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "7MGFSODDVI")
```

### Post-Fix Verification
```bash
# 1. Verify configuration updated
grep "KB_LEVEL_4_ID" src/config.py
# Expected: KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "CHYWO1H6OM")

# 2. Regenerate Level 4 assessment
python run_comprehensive_test.py

# 3. Check generated assessment uses Level 4 KB
grep -A 5 "kb_document_sources" output/assessments/level_4_*.json | head -20
# Expected: Should see CHYWO1H6OM in S3 URIs, not 7MGFSODDVI

# 4. Verify module coverage reflects Level 4 content
jq '.modules_covered' output/assessments/level_4_*.json
# Expected: Expert-level modules distinct from Level 3
```

## Rollback Plan

If the fix causes issues:
```bash
# Revert config.py to previous value
git checkout HEAD -- src/config.py

# Or manually set:
KB_LEVEL_4_ID="7MGFSODDVI"  # Revert to Level 3 KB
```

## Communication Plan

### Internal Stakeholders
- Notify: Development team, QA team, Data science team
- Impact: Previous Level 4 assessments need regeneration
- Action: Re-run all Level 4 validations

### External Users (if applicable)
- Notify: Users who completed Level 4 assessments
- Impact: Assessment results may need recalibration
- Action: Offer retake with corrected assessment

## Lessons Learned

### Why This Happened
1. **Incorrect Assumption**: Documentation stated "Level 4 shares KB with Level 3"
2. **Insufficient Validation**: No automated check verifying KB IDs match curriculum levels
3. **Missing Test**: No validation that Level 4 content differs from Level 3

### Prevention Measures
1. **Add Validation Test**: Assert KB IDs are unique (except where sharing is intended)
2. **Update Documentation**: Clearly specify each level has dedicated KB
3. **Content Sampling**: Add automated check that Level 4 questions differ from Level 3
4. **KB Configuration Audit**: Regular review of KB mappings

## Related Issues

- None currently identified

## References

- Configuration file: `src/config.py`
- KB query functions: `src/kb_tools.py`
- System specification: `docs/SPEC.md`
- Architecture plan: `docs/PLAN.md`

## Timeline

- **2025-11-03 Evening**: Bug discovered by user review
- **2025-11-03 Evening**: Bug documented, fix procedure defined
- **TBD**: Fix implementation
- **TBD**: Validation and testing
- **TBD**: Regenerate all Level 4 assessments

## Priority Justification

**Critical Priority** because:
1. **Data Quality**: All Level 4 assessments generated so far are invalid
2. **User Trust**: Users taking Level 4 assessment expect expert-level content
3. **Business Impact**: Level 4 is the highest certification level - must be accurate
4. **Simple Fix**: One-line code change with clear validation path
5. **Blocking**: Should fix before generating more Level 4 assessments
