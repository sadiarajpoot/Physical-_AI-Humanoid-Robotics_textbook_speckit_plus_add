---
id: 1
title: AI Textbook Constitution
stage: constitution
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Sadia Khan
command: /sp.constitution
labels: [constitution, textbook, robotics]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution
Project: AI/Spec-Driven Textbook Creation for Physical AI & Humanoid Robotics
Core principles:
- Absolute fidelity to the original course details provided — no additions, omissions, or external information
- Educational excellence with clear, structured, and engaging presentation of complex robotics and AI concepts
- Spec-driven development ensuring consistency, traceability, and modularity across all content
- Professional quality suitable for a GIAIC capstone quarter textbook
- Foundation for future RAG chatbot integration and bonus features
Key standards:
- Built exclusively with Docusaurus (classic template preferred, TypeScript optional)
- Content creation and refinement strictly guided by Spec-Kit Plus specifications
- Claude Code utilized for generating accurate code examples, technical explanations, and diagrams where relevant to robotics modules
- Full coverage of every section from the provided document:
  - Quarter Overview and Introduction
  - Why Physical AI Matters
  - Learning Outcomes
  - Module 1: The Robotic Nervous System (ROS 2)
  - Module 2: The Digital Twin (Gazebo & Unity)
  - Module 3: The AI-Robot Brain (NVIDIA Isaac™)
  - Module 4: Vision-Language-Action (VLA)
  - Weekly Breakdown (Weeks 1-13)
  - Capstone Project: The Autonomous Humanoid
  - Assessments
  - Hardware Requirements (including all tables: Digital Twin Workstation, Edge Kit, Robot Options, Cloud Alternatives, Economy Jetson Kit)
- Proper Markdown formatting: headings, bullet points, numbered lists, code blocks, and accurate Markdown tables
- Intuitive sidebar navigation with logical categories (e.g., Modules, Weekly Breakdown, Hardware)
Constraints:
- All content must originate solely from the provided course description document
- Implementation confined to the frontend folder in a monorepo structure
- No backend code, databases, authentication, or chatbot functionality in this phase
- Deployment as a static site via GitHub Pages or Vercel
- Timeline priority: Complete textbook as a standalone, fully functional deliverable before RAG phase
Success criteria:
- Live deployed textbook that is fully navigable, responsive, and visually clean
- Every section from the original document accurately represented and well-formatted
- All hardware and architecture tables correctly rendered in Markdown
- Spec-Kit Plus specifications defined and validated for key chapters
- Local build (npm start) and deployed build function without errors
- Content ready for direct ingestion into a vector database for the subsequent RAG chatbot phase
- Clear placeholders or hooks prepared for future bonus features (personalization, translation, Claude Subagents)

## Response snapshot

Updated the project constitution with specific principles and guidelines for the AI/Spec-Driven Textbook Creation for Physical AI & Humanoid Robotics project. The constitution now includes 6 core principles covering fidelity to original content, educational excellence, spec-driven development, professional quality standards, future-ready foundation, and implementation standards compliance. The document also includes sections for key standards, constraints, success criteria, and governance.

## Outcome

- ✅ Impact: Constitution updated with project-specific principles and guidelines
- 🧪 Tests: No tests required for documentation update
- 📁 Files: .specify/memory/constitution.md updated
- 🔁 Next prompts: Project can proceed with updated constitutional guidelines
- 🧠 Reflection: Constitution now properly reflects the specific requirements and constraints of the AI textbook project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A