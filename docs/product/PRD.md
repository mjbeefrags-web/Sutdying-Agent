# Product requirements: Study Platform

## Vision and target customer
An evidence-grounded study workspace for university students who learn from dense, fragmented course material. The initial customer is an individual student (18+) taking one or more text-heavy university courses, primarily on a laptop. Buyers are students; later institutional pilots require a distinct privacy, procurement, and administration review.

## Problem and value
Students spend time locating, organizing, and re-explaining course content; generic chatbots can answer confidently without grounding; revision is often reactive and performance feedback is fragmented. The product turns a student's own lectures into a searchable course knowledge base, then supports cited tutoring, retrieval practice, and a manageable plan. The 3D library provides orientation and delight, while all learning tasks remain available in fast, accessible 2D views.

## Product principles
1. Evidence before fluency: course-grounded claims cite source passages; uncertainty is explicit.
2. Student control: uploaded material is private by default; AI output is editable, attributable, and deletable.
3. Calm by default: one primary task per view, restrained motion, no streak pressure or unsolicited notifications.
4. Learning outcomes over time-in-app: prioritize recall, mastery, and confidence calibration.
5. Progressive enhancement: 3D is optional and never gates a core workflow.

## Goals and measures
- Validate a student's complete loop: create course → upload lecture → process → ask cited question → practice → review.
- Measure activation: >=60% of invited beta students complete the loop within 7 days.
- Measure grounding: >=90% of sampled answer claims have a valid supporting citation; unsupported answer rate <5% in curated evaluation.
- Measure learning: >=10 percentage-point improvement on delayed retrieval checks versus a baseline cohort, evaluated before claiming impact.
- Measure usability: >=80% of usability-test participants complete upload-to-first-practice without help.
- Reliability: API availability >=99.5% for beta, ingestion job success >=98% excluding invalid input/provider outages.

## Functional requirements
- Account sign-up, verified email, session management, account export/deletion.
- Create, rename, archive, and delete private courses.
- Upload supported PDF and text documents with limits and visible processing states.
- Extract text, preserve page/source locations, index chunks, and surface retryable failures.
- Course-scoped tutor with citations, abstention when evidence is insufficient, and feedback.
- Create/edit flashcards and practice exams from selected course material; record attempts.
- Review due cards and answer history; show explainable mastery/weakness indicators.
- Build and adjust a weekly study plan using due work, exam dates, and user availability.
- Library, course, reading, tutor, exam, flashcard, analytics, profile and billing areas.
- Subscription integration is deferred; settings and plan presentation may be prototyped only.

## Non-functional requirements
TLS in transit; encryption at rest via managed platform; tenant-scoped authorization; documented retention and deletion; WCAG 2.2 AA target; p95 API <500ms for non-AI requests at beta load; AI latency shown as a job/streaming state; supported browsers current and previous major Chrome/Firefox/Safari/Edge.

## Out of scope for Phase 1
Institutional SSO/rosters, social sharing, mobile native apps, unrestricted web search, automated high-stakes grading, payment collection, video/audio transcription at scale, and autonomous scheduling changes.

## Assumptions and open decisions
Initial launch is English-language, individual accounts, US/EU provider availability subject to legal review. Confirm supported file size/page limits, age policy, retention periods, regions, model vendors, pricing, and whether institutional pilots are in the first commercial release.
