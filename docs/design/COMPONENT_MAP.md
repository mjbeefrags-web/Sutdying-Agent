# Component map

```text
app/
  (marketing)/page.tsx                 Cinematic landing
  app/library/page.tsx                 Library 3D + accessible 2D list
  app/courses/[courseId]/page.tsx       Course workspace
  app/courses/[courseId]/read/...       Reading environment
  app/courses/[courseId]/tutor/page.tsx AI tutor and citations
  app/courses/[courseId]/cards/page.tsx Flashcard review
  app/courses/[courseId]/exams/...      Exam room and review
  app/analytics/page.tsx                Learning analytics
  app/settings/profile/page.tsx         Profile/subscription status
components/
  shell/{AppShell,Sidebar,CommandBar}
  library/{LibraryScene,CourseShelf,CourseListFallback}
  reading/{Reader,Outline,CitationAnchor}
  tutor/{Conversation,Answer,CitationList,Composer}
  practice/{Flashcard,ExamTimer,Question,AnswerReview}
  analytics/{MasteryMap,StudyPlan,TrendChart}
  ui/{Button,Dialog,Input,Toast,...}     shadcn/ui primitives
features/                               Route-owned hooks, schemas, API adapters
```

The map describes intended product components; the Phase 1 skeleton does not yet implement these screens. Keep WebGL scene behind `LibraryScene` boundary and share course selection contract with `CourseListFallback`.
