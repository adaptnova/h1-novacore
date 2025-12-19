# Team Communication - Message Format Guide

**Project:** Easter
**Version:** 1.0
**Date:** November 23, 2025
**Distribution:** All Team Members

---

## 📋 OVERVIEW

This guide defines the communication standards for the Easter project, following the Phoenix communication conventions. All team communications must follow these formats to ensure clarity, consistency, and traceability.

---

## 🏷️ NAMING CONVENTION

### **File Names:**
```
YYMMDD_HHMM_team_recipient_topic.md
```

**Components:**
- **YYMMDD**: Year, Month, Day (e.g., 251123 = November 23, 2025)
- **HHMM**: Time in 24-hour format (e.g., 0530 = 5:30 AM, 1400 = 2:00 PM)
- **team**: Team identifier (dataops, novaops, easter, nexus)
- **recipient**: Intended recipient (individual, team, or all)
- **topic**: Brief description (init, update, review, escalation)

### **Examples:**

**Good Names:**
```
251123_0530_dataops_init_easter.md
251123_1400_novaops_dataops_progress.md
251123_1600_easter_team_architecture_review.md
251123_1800_dataops_escalation_service_issue.md
251124_0900_team_all_weekly_standup.md
```

**Bad Names:**
```
todays_memo.md
dataops_update.doc
meeting_notes.txt
status123.md
```

---

## 📝 MESSAGE TEMPLATE

### **Standard Header (Required):**

```markdown
# TEAM COMMUNICATION MEMO
**Date:** [Full Date] [Time] MST
**From:** [Team Name]
**To:** [Recipient Team/Individual]
**Subject:** [Brief, descriptive subject]
**Priority:** [High|Medium|Low]
**Distribution:** [Who receives this]
**Reply-To:** [For threaded discussions, optional]
**References:** [Related document IDs, optional]
```

### **Content Structure:**

```markdown
## 🎯 EXECUTIVE SUMMARY
[2-3 sentences: what, why, key message]

## 💡 DETAILS
[Technical or operational details]

## 📋 ACTION ITEMS
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## ⏰ TIMELINE
[Key dates and deadlines]

## 🚀 NEXT STEMS
[What happens next]

## ❓ QUESTIONS
[Any open questions for the recipient]

## 📞 CONTACT
[How to reach sender, response time expectations]

---
```

---

## 🎨 FORMATTING GUIDELINES

### **Emojis (Use Consistently):**

**Status:**
- ✅ Complete/Done
- ⚠️ Warning/Issue
- ❌ Failed/Error
- 🔄 In Progress
- 📅 Scheduled

**Sections:**
- 🎯 Summary/Goals
- 💡 Details/Information
- 📋 Lists/Checkboxes
- ⏰ Time/Deadlines
- 🚀 Actions/Next Steps
- ❓ Questions/Open Items
- 📞 Contact/Coordination

**Priorities:**
- 🔥 Critical
- ⚡ High
- 📌 Medium
- 💤 Low

### **Code Blocks:**

```bash
# Commands
sudo systemctl status service

# Configuration
{
  "key": "value",
  "array": [1, 2, 3]
}
```

### **Tables:**

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

### **Lists:**

**Unordered:**
```markdown
- Item 1
  - Sub-item 1.1
  - Sub-item 1.2
- Item 2
```

**Ordered:**
```markdown
1. First step
2. Second step
3. Third step
```

---

## 📊 MESSAGE TYPES

### **1. INIT (Introduction)**

**Purpose:** Introduce a team, project, or major initiative

**Template Sections:**
- Executive Summary
- Who We Are (team roles)
- What We're Building (overview)
- Architecture/Design
- Timeline
- Collaboration Model
- Next Steps
- Contact Information

**Example:**
```
251123_0530_dataops_init_easter.md
```

---

### **2. UPDATE (Status Update)**

**Purpose:** Regular progress updates

**Template Sections:**
- Executive Summary
- Progress Since Last Update
- Key Achievements
- Current Status
- Upcoming Milestones
- Risks/Issues
- Action Items

**Example:**
```
251124_0900_dataops_update_easter_progress.md
```

---

### **3. DECISION (Decision Record)**

**Purpose:** Document a major decision

**Template Sections:**
- Executive Summary
- Context/Background
- Options Considered
- Decision Made
- Rationale
- Impact
- Action Items
- Review Date

**Example:**
```
251124_1400_team_decision_microservices_architecture.md
```

---

### **4. REVIEW (Meeting Notes)**

**Purpose:** Document meeting outcomes

**Template Sections:**
- Executive Summary
- Attendees
- Agenda Items
- Discussion Summary
- Decisions Made
- Action Items (with owners and deadlines)
- Next Meeting

**Example:**
```
251124_1600_team_review_architecture_design.md
```

---

### **5. ESCALATION (Issue/Problem)**

**Purpose:** Escalate urgent issues

**Template Sections:**
- Executive Summary
- Problem Description
- Impact
- Root Cause (if known)
- Immediate Actions Taken
- Required Response
- Timeline for Resolution
- Contact for Updates

**Example:**
```
251124_1800_novaops_escalation_service_down.md
```

---

### **6. REQUEST (Ask for Help/Info)**

**Purpose:** Request assistance or information

**Template Sections:**
- Executive Summary
- What You Need
- Why You Need It
- Deadline
- Context/Background
- Proposed Approach
- Questions

**Example:**
```
251125_0900_easter_request_infrastructure_access.md
```

---

### **7. COMPLETE (Completion Notice)**

**Purpose:** Announce completion of a milestone

**Template Sections:**
- Executive Summary
- What Was Completed
- Key Achievements
- Metrics/Results
- Deliverables
- Lessons Learned
- Next Steps

**Example:**
```
251125_1700_dataops_complete_continuity_integration.md
```

---

### **8. MVP (MVP Achievement)**

**Purpose:** Announce MVP completion (AI speed)

**Template Sections:**
- Executive Summary
- MVP Scope
- What's Working
- Testing Results
- Performance Metrics
- Next Phase
- Deployment Instructions

**Example:**
```
251123_0830_dataops_mvp_continuity_complete.md
```

---

## ⚡ AI SPEED DEVELOPMENT NOTES

**Easter is an AI-speed project:**
- **MVP Timeline:** 2 hours (not 2 weeks)
- **Iterative:** Build as we go
- **Responsive:** Updates in real-time
- **Focused:** Ship MVP, then enhance

**For rapid updates:**
- Use UPDATE messages hourly if needed
- Tag with "AI-SPEED" in subject for urgent items
- Response time: 15 minutes (not 4 hours)
- Standups: Every 30 minutes during MVP phase

---

## 🔄 THREADED DISCUSSIONS

### **For Follow-up Messages:**

```markdown
**References:** 251123_0530_dataops_init_easter.md
**Reply-To:** DataOps Team
**Subject:** RE: DataOps Introduction & Architecture Plan

[Content...]
```

### **For Updates to Existing Threads:**

```markdown
**References:** 251123_0530_dataops_init_easter.md
**Updates:** Section on microservices architecture
**Changes:** Added VectorService to Phase 2

[Content...]
```

---

## 📦 DIRECTORY STRUCTURE

```
/adapt/projects/easter/team_comms/
├── 251123_0530_dataops_init_easter.md
├── 251123_1400_novaops_dataops_progress.md
├── MESSAGE_FORMATS.md (this file)
├── [YYMMDD_HHMM_team_recipient_topic.md]
└── archive/
    ├── 2025/
    └── 2026/
```

---

## ✅ QUALITY CHECKLIST

Before sending a message, verify:

- [ ] File name follows convention
- [ ] Header is complete and accurate
- [ ] Subject is clear and descriptive
- [ ] Priority is appropriate
- [ ] Distribution list is correct
- [ ] Executive summary is 2-3 sentences
- [ ] Action items are clearly marked
- [ ] Timeline is specified where relevant
- [ ] Next steps are defined
- [ ] Contact information is included
- [ ] Formatting is consistent
- [ ] No sensitive information included
- [ ] Spell check completed

---

## 📞 COORDINATION PROTOCOLS

### **Response Times (AI Speed):**

| Priority | Response Time | Example |
|----------|---------------|---------|
| Critical | 15 minutes | MVP blocker, urgent fix needed |
| High | 30 minutes | Integration issue |
| Medium | 2 hours | Question, clarification |
| Low | 8 hours | FYI, documentation |

### **Meeting Cadence (MVP Phase):**

- **Standup**: Every 30 minutes during MVP
- **Quick Sync**: As needed via team_comms
- **Architecture Review**: After MVP complete
- **Sprint Planning**: As we go
- **Emergency Escalation**: Immediate via team_comms

---

## 🚀 BEST PRACTICES

### **DO:**

✅ Use clear, concise language
✅ Include actionable items
✅ Tag relevant teams/individuals
✅ Reference related documents
✅ Use consistent formatting
✅ Include timelines and deadlines
✅ Set appropriate priority levels
✅ Archive old messages
✅ Use threading for discussions

### **DON'T:**

❌ Use unclear subjects
❌ Include unrelated information
❌ Skip the executive summary
❌ Forget to tag action items
❌ Use inconsistent formatting
❌ Send to too many people
❌ Include sensitive data
❌ Forget to follow up
❌ Leave action items without owners

---

## 📚 TEMPLATE LIBRARY

### **Quick Templates** (Copy and customize):

**Init Template:**
- Use: `/adapt/projects/easter/team_comms/251123_0530_dataops_init_easter.md`

**Update Template:**
```markdown
# TEAM COMMUNICATION MEMO - UPDATE
**Date:** [Date] [Time] MST
**From:** [Team]
**To:** [Recipient]
**Subject:** [Topic] - Weekly Update
**Priority:** Medium
**Distribution:** [List]

## 🎯 EXECUTIVE SUMMARY
[Brief summary of status]

## 📈 PROGRESS
[What happened since last update]

## 🎯 CURRENT STATUS
[Where we are now]

## 📋 ACTION ITEMS
- [ ] [Owner]: [Action] (Due: [Date])

## 🚀 NEXT STEPS
[What's coming up]

---
```

---

**Use this guide for all Easter project communications. Consistency ensures clarity and efficiency.**
