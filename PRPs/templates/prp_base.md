# PRP: [Feature Name]

## Feature Goal
[One paragraph describing what this feature accomplishes and why it matters]

## Deliverable
[Concrete, measurable deliverable - what will exist when this is complete]

## Success Definition
[How will we know this feature is successfully implemented]

---

## Context & Research

### Required Knowledge
```yaml
# Documentation references (with specific section anchors)
docs:
  - name: "[Technology/Library Name]"
    url: "https://specific-url.com/path#section-anchor"
    relevance: "[Why this matters for implementation]"
    key_points: "[Critical information from this doc]"

# Code patterns and conventions
patterns:
  - location: "[File/directory path]"
    pattern: "[What to follow/emulate]"
    example: "[Specific code example or reference]"

# Known gotchas and pitfalls
gotchas:
  - issue: "[What can go wrong]"
    solution: "[How to avoid it]"
    reference: "[Where this was learned]"

# External examples (GitHub/StackOverflow/blogs)
examples:
  - url: "https://github.com/org/repo/path/to/file#L123"
    description: "[What this example shows]"
    relevance: "[How to apply it here]"

# Project-specific context
project_context:
  - aspect: "[Architecture/Tech stack/Conventions]"
    details: "[Specific information about this project]"
    implications: "[How this affects implementation]"
```

### Architecture Overview
[High-level architecture diagram or description showing how components interact]

### Technical Stack
```yaml
backend:
  framework: "[e.g., FastAPI, Flask, Django]"
  language: "[e.g., Python 3.11]"
  database: "[e.g., PostgreSQL with Supabase]"
  auth: "[e.g., Azure AD OAuth2]"
  key_libraries:
    - "[Library 1 with version]"
    - "[Library 2 with version]"

frontend:
  framework: "[e.g., React 18 with TypeScript]"
  build_tool: "[e.g., Vite]"
  styling: "[e.g., Tailwind CSS]"
  key_libraries:
    - "[Library 1 with version]"
    - "[Library 2 with version]"

infrastructure:
  hosting: "[Where this will be deployed]"
  database: "[Database service]"
  payment: "[Payment processor]"
  other: "[Other services]"
```

### Dependencies & Prerequisites
- [ ] [Prerequisite 1 - what must exist before starting]
- [ ] [Prerequisite 2 - services/accounts needed]
- [ ] [Prerequisite 3 - environment setup requirements]

---

## Implementation Tasks

### Task Structure
Each task follows this format:
- **Task Name**: [Clear, action-oriented task name]
  - **Dependency**: [What must be completed first, or "None"]
  - **Files**: [Specific files to create/modify]
  - **Acceptance Criteria**: [How to verify this task is complete]
  - **Key Considerations**: [Important details, gotchas, or patterns to follow]

---

### Phase 1: [Phase Name - e.g., "Database & Schema Setup"]

**Task 1.1**: [Specific task name]
- **Dependency**: None
- **Files**:
  - `path/to/file1.ext`
  - `path/to/file2.ext`
- **Acceptance Criteria**:
  - [ ] [Specific measurable criterion 1]
  - [ ] [Specific measurable criterion 2]
- **Key Considerations**:
  - [Important detail about naming, patterns, or gotchas]
  - [Reference to similar code: `existing_file.py:123`]

**Task 1.2**: [Specific task name]
- **Dependency**: Task 1.1
- **Files**:
  - `path/to/file.ext`
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Key Considerations**:
  - [Key detail]

---

### Phase 2: [Phase Name]

**Task 2.1**: [Specific task name]
- **Dependency**: Task 1.2
- **Files**:
  - `path/to/file.ext`
- **Acceptance Criteria**:
  - [ ] [Criterion]
- **Key Considerations**:
  - [Key detail]

---

[Continue with remaining phases and tasks...]

---

## Validation Strategy

### Unit Testing
```yaml
test_coverage:
  - component: "[Component name]"
    test_file: "[Test file path]"
    key_tests:
      - "[Test scenario 1]"
      - "[Test scenario 2]"
```

### Integration Testing
```yaml
integration_tests:
  - flow: "[User flow or API flow]"
    steps:
      - "[Step 1]"
      - "[Step 2]"
    expected_result: "[What should happen]"
```

### Manual Testing Checklist
- [ ] [Manual test 1 - e.g., "User can login via Azure AD"]
- [ ] [Manual test 2 - e.g., "Token balance updates after purchase"]
- [ ] [Manual test 3]

---

## Final Validation Checklist

### Functionality
- [ ] All acceptance criteria met for every task
- [ ] All endpoints respond with correct status codes
- [ ] All user flows work end-to-end
- [ ] Error handling works for all edge cases

### Code Quality
- [ ] Code follows project conventions
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables documented in .env.example
- [ ] All functions have appropriate error handling

### Security
- [ ] Authentication works correctly
- [ ] Authorization checks in place
- [ ] Sensitive data is encrypted/protected
- [ ] Rate limiting implemented where needed

### Documentation
- [ ] README updated with new features
- [ ] API documentation complete
- [ ] Environment variables documented
- [ ] Deployment instructions updated

### Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing checklist complete
- [ ] Edge cases handled

---

## Environment Variables

### Backend (.env)
```bash
# [Category 1 - e.g., Authentication]
VAR_NAME=value_placeholder
VAR_NAME_2=value_placeholder

# [Category 2 - e.g., Database]
VAR_NAME_3=value_placeholder
```

### Frontend (.env)
```bash
# [Category 1]
VITE_VAR_NAME=value_placeholder
```

---

## Known Limitations & Future Improvements

### Current Limitations
- [Limitation 1 - what doesn't work or is simplified]
- [Limitation 2]

### Future Enhancements
- [Enhancement 1 - what could be added later]
- [Enhancement 2]

---

## References & Resources

### Primary Documentation
- [Technology 1]: [URL with section anchor]
- [Technology 2]: [URL with section anchor]

### Implementation Examples
- [Example 1]: [URL] - [What it demonstrates]
- [Example 2]: [URL] - [What it demonstrates]

### Related Issues/PRs
- [Issue/PR description]: [URL]

---

## Success Metrics

**One-Pass Implementation Confidence**: [1-10 rating]
- **Reasoning**: [Why this rating - what gives confidence or what might cause issues]

**Estimated Implementation Time**: [Time estimate]
- **Breakdown**:
  - Phase 1: [Time]
  - Phase 2: [Time]
  - Phase 3: [Time]
  - Testing: [Time]

---

## "No Prior Knowledge" Test

This PRP passes the "No Prior Knowledge" test if someone unfamiliar with this codebase can:
1. ✓ Understand what to build and why
2. ✓ Know exactly which files to create/modify
3. ✓ Follow specific patterns and conventions
4. ✓ Find all necessary documentation
5. ✓ Validate their implementation successfully

**Test Result**: [Pass/Fail with reasoning]
