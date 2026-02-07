
Vina Frontend - Complete Product Requirements Document
Version: 3.0 (Final)
Last Updated: February 7, 2026
Status: Ready for Development
Target: Commit To Change: AI Agents Hackathon
Prepared for: LLM Code Generation

Table of Contents

Executive Summary
Project Overview
User Personas & Flows
Complete Feature Specification
Screen-by-Screen Specifications
Component Architecture
Data Models & State Management
API Endpoint Specifications
Visual Design System
Technical Implementation Guide
Testing & Validation
Deployment Strategy
Future Enhancements


1. Executive Summary
1.1 Product Vision
Vina is a mobile-first, adaptive video learning platform that personalizes LLM education for professionals. The platform demonstrates AI-powered personalization from the first interaction through:

Profession-specific content
Pre-assessment placement
Real-time content adaptation
Continuous difficulty adjustment

1.2 Core Value Proposition
For professionals: Learn LLMs in 3-5 minute lessons tailored to your role, with content that adapts as you learn.
For hackathon judges: Demonstrates agentic AI through multi-step content generation, quality review, and adaptive regeneration based on user feedback.
1.3 Hackathon Scope (MVP)
Timeline: 3 days
Team Size: 2 developers
Delivery:

Fully functional mobile web app
17 personalized lessons × 4 professions = 68 unique lesson variants pre-generated
Real-time adaptation (regenerate on user request)
Pre-assessment quiz for smart placement
Daily practice mode
Progress tracking with streaks & points


2. Project Overview
2.1 Technical Stack
LayerTechnologyReasoningFrameworkNext.js 14 (App Router)SSR, optimal performance, easy deploymentStylingTailwind CSSRapid development, consistent design systemState ManagementReact Context + LocalStorageSimple, no external state library neededVideo PlayerHTML5 Video + Custom ControlsFull control over UX, mobile-optimizedDeploymentVercelZero-config, instant deploys, preview URLsBackendFastAPI (Python) on RailwaySeparate repo, API-first architecture
2.2 Browser Support
Primary Targets:

iOS Safari 16+ (iPhone)
Chrome 120+ (Android)

Secondary Targets:

Desktop Chrome (mobile emulator view)
Desktop Safari (mobile emulator view)

Not Supported:

Internet Explorer (EOL)
Safari <16

2.3 Device Targets
Primary:

iPhone 14 Pro (390 × 844)
Samsung Galaxy S23 (360 × 800)

Secondary:

iPhone SE (375 × 667) - small screen
Desktop (430px container, centered)

Aspect Ratio: 9:16 vertical (portrait only)

3. User Personas & Flows
3.1 Target Professions
ProfessionIndustry OptionsTypical Use CasesClinical ResearcherPharma/Biotech, Academic Research, Medical DevicesProtocol drafting, adverse event summaries, literature reviewsHR ManagerTech Company, Financial Services, ManufacturingJob descriptions, policy documents, candidate screeningProject ManagerSoftware/Tech, Construction, HealthcareStatus reports, risk assessments, stakeholder communicationsMarketing ManagerE-Commerce, B2B SaaS, Consumer GoodsAd copy, email campaigns, product descriptions
3.2 Primary User Flow (First-Time User)
1. WELCOME SCREEN
   ↓ [Get Started]
   
2. PROFESSION SELECTION
   ↓ Select profession from dropdown → [Continue]
   
3. PRE-ASSESSMENT QUIZ
   ↓ Answer 10 questions (auto-advance, can skip anytime)
   ↓ Backend calculates starting lesson
   
4. COURSE MAP
   ↓ Shows 17 lessons, starting lesson unlocked
   ↓ Tap active lesson node
   
5. LESSON PLAYER
   ↓ Watch video (can adapt, adjust speed)
   ↓ Video completes
   
6. LESSON QUIZ
   ↓ Answer 3 questions (retry until correct)
   ↓ Pass (2/3 or 3/3)
   
7. QUIZ RESULTS
   ↓ Earn points, update streak
   ↓ [Continue Learning]
   
8. COURSE MAP (Next lesson unlocked)
   ↓ Repeat steps 4-8 for each lesson
3.3 Secondary User Flow (Returning User)
1. AUTO-LOAD COURSE MAP
   ↓ Resume where left off (current lesson highlighted)
   
2. OPTIONS:
   a) Continue current lesson
   b) Review completed lesson
   c) Daily Practice (if available)
   d) Check Progress stats
3.4 Adaptation Flow
During Lesson:
1. Tap screen → Controls appear
2. Tap [Adapt] button (always visible, floating right)
3. Overlay menu shows 4 options
4. Select option (e.g., "Simplify this")
5. Loading state ("Personalizing your lesson...")
6. New video loads
7. Resume watching
3.5 "I Know This Already" Flow
During Lesson:
1. Tap [Adapt] → Select "I know this already"
2. Video pauses
3. Checkpoint quiz overlay appears (3 questions)
4. Answer all 3 questions

IF PASS (2/3 or 3/3):
   5a. Success message ("Great! Moving to next lesson...")
   6a. Mark current lesson complete
   7a. Update streak & points
   8a. Navigate to next lesson

IF FAIL (0/3 or 1/3):
   5b. Encouragement message ("Let's review together...")
   6b. Resume video from same position

4. Complete Feature Specification
4.1 Feature List (Included in Hackathon MVP)
FeaturePriorityComplexityStatusWelcome ScreenP1Low✅ IncludeProfession SelectionP1Low✅ IncludePre-Assessment QuizP1Medium✅ IncludeCourse Map (17 lessons)P1Medium✅ IncludeLesson Player (video + controls)P1High✅ IncludeAdapt Button (4 options)P1High✅ IncludeLesson Quiz (3 MCQs)P1Medium✅ Include"I Know This Already" (checkpoint quiz)P1Medium✅ IncludeQuiz Results & FeedbackP1Low✅ IncludeLet's Practice Tab (daily quiz)P2Medium✅ IncludeProgress Tab (stats dashboard)P2Low✅ IncludeTop Bar (XP, Streak)P2Low✅ IncludeBottom Navigation (3 tabs)P2Low✅ IncludeLocalStorage PersistenceP1Medium✅ IncludeSpeed Control (1x, 1.25x, 1.5x)P2Low✅ IncludeReplay ButtonP2Low✅ IncludeLoading StatesP1Low✅ IncludeError HandlingP1Medium✅ Include
4.2 Features Excluded (Future Enhancements)
FeatureReason for ExclusionPost-Hackathon PriorityIndustry/Experience SelectionSimplify onboardingMediumTopic Groups (5 groups)Flat 17 lessons simplerLowProfile TabContent moved to ProgressLowSkills Portfolio TabOnly 1 courseMediumNotificationsNo backend supportLowLearning Time TrackerNot core valueLowLeaderboardBackend complexityHighAchievements/BadgesGamification layerMediumMulti-select Quiz QuestionsComplexityLowVideo ScrubbingLinear engagement betterMediumPWA Install PromptPost-launch featureHighAdvanced AnimationsTime constraintMediumSocial SharingNot coreLow

5. Screen-by-Screen Specifications
5.1 Welcome Screen
Route: /
Purpose: First impression, set expectations, brand introduction
Trigger: First visit (no LocalStorage profile)
Layout:
┌─────────────────────────┐
│                         │
│    [Vina Logo]          │ ← 120×120px, centered
│    (checkmark person)   │
│                         │
│   Learn LLMs Your Way   │ ← H1, 32px, bold
│                         │
│   Personalized lessons  │ ← Body, 16px, gray
│   that adapt to you     │
│                         │
│                         │
│   [Get Started →]       │ ← Primary button, teal
│                         │
│                         │
└─────────────────────────┘
Components:

Logo image (PNG, 240×240px @2x)
Title text (H1)
Subtitle text (Body)
CTA button (Primary)

Interactions:

Tap "Get Started" → Navigate to /profession-select
If LocalStorage has profile → Auto-redirect to /course-map

Animations (Optional):

Logo fade-in (0.5s)
Text fade-in stagger (0.3s delay)
Button subtle pulse

Accessibility:

Skip link: "Skip to main content" (hidden, keyboard-accessible)
Logo alt text: "Vina - Personalized LLM Learning"
Button aria-label: "Get started with Vina"

Exit Criteria:

User taps CTA → Navigate
User already has profile → Skip this screen


5.2 Profession Selection Screen
Route: /profession-select
Purpose: Capture user's profession for content personalization
Trigger: New user flow, or returning user edits profile
Layout:
┌─────────────────────────┐
│  [← Back]  Let's Get    │ ← Header with back button
│            Started       │
│                         │
│  What's your role?      │ ← Label, 20px, semibold
│                         │
│  [Dropdown ▼          ] │ ← Select input
│   Clinical Researcher   │
│                         │
│  We'll personalize your │ ← Help text, 14px, gray
│  learning experience    │
│                         │
│                         │
│                         │
│                         │
│  [Continue →]           │ ← Disabled until selection
│                         │
└─────────────────────────┘
Dropdown Options:
javascriptconst PROFESSIONS = [
  "Clinical Researcher",
  "HR Manager",
  "Project Manager",
  "Marketing Manager"
];
Components:

Header with back button
Label text
Dropdown select (native <select> element for mobile optimization)
Help text
CTA button (disabled state initially)

Interactions:

Tap Back: Navigate to Welcome Screen (or previous screen)
Select profession: Enable Continue button
Tap Continue:

POST to /api/v1/profiles with { profession }
Save to LocalStorage
Navigate to /pre-assessment



Validation:

Must select a profession (Continue button disabled until selected)
Default state: No selection (placeholder: "Select your profession...")

Accessibility:

Label for select: <label for="profession">What's your role?</label>
Select aria-describedby: Help text ID
Button disabled state: aria-disabled="true"

State Management:
javascript// Local component state
const [profession, setProfession] = useState("");
const [isLoading, setIsLoading] = useState(false);

// On Continue
const handleContinue = async () => {
  setIsLoading(true);
  const response = await fetch('/api/v1/profiles', {
    method: 'POST',
    body: JSON.stringify({ profession })
  });
  const { userId, profile } = await response.json();
  
  // Save to LocalStorage
  localStorage.setItem('vina_user', JSON.stringify({ userId, profile }));
  
  // Navigate
  router.push('/pre-assessment');
};
```

---

### **5.3 Pre-Assessment Quiz Screen**

**Route:** `/pre-assessment`  
**Purpose:** Place user at appropriate starting lesson based on existing knowledge  
**Trigger:** After profession selection (new users)  

**Layout:**
```
┌─────────────────────────┐
│  [Skip Quiz]            │ ← Top-right corner, text button
│                         │
│  Quick Knowledge Check  │ ← Title, 24px, semibold
│                         │
│  Question 3 of 10       │ ← Progress text, 14px
│  ●●●○○○○○○○            │ ← Progress dots
│                         │
│  What causes LLMs to    │ ← Question text, 18px
│  generate incorrect     │
│  information?           │
│                         │
│  ○ A) Limited training  │ ← Option A (radio button)
│     data                │
│                         │
│  ○ B) Pattern-based     │ ← Option B
│     prediction          │
│                         │
│  ○ C) User errors in    │ ← Option C
│     prompting           │
│                         │
│  ○ D) Insufficient      │ ← Option D
│     context             │
│                         │
└─────────────────────────┘
```

**Question Format:**
- All single-choice (MCQ, 4 options)
- No multi-select
- No retry (select answer → auto-advance after 0.5s)
- No explanations shown

**Flow:**
```
1. Question appears
2. User selects answer (A, B, C, or D)
3. Brief pause (0.5s) - selection highlights
4. Auto-advance to next question
5. Repeat for up to 10 questions
6. OR: If user gets 2 wrong in a row → Auto-end quiz
7. Backend calculates starting lesson
8. Navigate to Course Map
Components:

Skip button (top-right, always visible)
Title
Progress indicator (text + dots)
Question text
4 radio button options
Auto-advance logic (no Submit button)

Interactions:

Tap Skip Quiz:

Immediate navigate to /course-map
Start at L01 (all other lessons locked)
Save to LocalStorage: { preAssessmentCompleted: false, startingLesson: "l01" }


Select Answer:

Highlight selected option (teal border)
Wait 0.5s
Track answer (correct/incorrect)
If 2 wrong in a row: End quiz early
Move to next question (or submit if Q10)


Quiz Complete:

POST to /api/v1/assessment/submit with answers array
Backend responds with: { startingLesson: "l06_bias_issues", score: 6 }
Save to LocalStorage
Navigate to /course-map



Progress Tracking:
javascriptconst [currentQuestion, setCurrentQuestion] = useState(0);
const [answers, setAnswers] = useState([]);
const [consecutiveWrong, setConsecutiveWrong] = useState(0);

const handleAnswer = (selectedOption) => {
  const isCorrect = selectedOption === questions[currentQuestion].correctAnswer;
  
  // Track answer
  answers.push({
    questionId: questions[currentQuestion].id,
    selected: selectedOption,
    correct: isCorrect
  });
  
  // Check consecutive wrong
  if (!isCorrect) {
    setConsecutiveWrong(prev => prev + 1);
    if (consecutiveWrong + 1 >= 2) {
      // End quiz early
      submitQuiz();
      return;
    }
  } else {
    setConsecutiveWrong(0);
  }
  
  // Auto-advance after 0.5s
  setTimeout(() => {
    if (currentQuestion < 9) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      // Last question
      submitQuiz();
    }
  }, 500);
};
```

**Accessibility:**
- Progress: `aria-live="polite"` (announces "Question 3 of 10")
- Radio buttons: Proper `<input type="radio">` with labels
- Question text: `<legend>` for radio group
- Skip button: `aria-label="Skip placement quiz and start from beginning"`

**Edge Cases:**
- User refreshes mid-quiz → Start over (don't save progress)
- All 10 questions answered without 2-in-a-row fails → Submit all answers
- User clicks Skip after answering 5 questions → Discard answers, start at L01

---

### **5.4 Course Map Screen** (Home Tab)

**Route:** `/course-map`  
**Purpose:** Visual learning path, progress tracking, lesson selection  
**Trigger:** After pre-assessment, or tap Home tab  

**Layout:**
```
┌─────────────────────────┐
│ [🔥 4] [💎 80]   [👤]  │ ← Top bar (sticky)
│                         │
│  LLM Foundations        │ ← Course title, 24px bold
│  ▓▓▓░░░░░░░░░░░░ 3/17  │ ← Progress bar + text
│                         │
│ ┌─────────────────────┐ │ ← Scrollable area starts
│ │     ┌─○─┐           │ │   (vertical scroll)
│ │     │17 │ 🔒       │ │
│ │     └───┘           │ │
│ │   L17: Prompting    │ │
│ │   for Your Role     │ │
│ │                     │ │
│ │     ┌─○─┐           │ │
│ │     │16 │ 🔒       │ │
│ │     └───┘           │ │
│ │   L16: Iteration    │ │
│ │                     │ │
│ │   [... 11 more ...]  │ │
│ │                     │ │
│ │     ┌─●─┐           │ │ ← Active (pulsing)
│ │     │ 4 │           │ │
│ │     └───┘           │ │
│ │   L04: Where LLMs   │ │
│ │   Excel             │ │
│ │                     │ │
│ │     ┌─✓─┐           │ │ ← Completed
│ │     │ 3 │           │ │
│ │     └───┘           │ │
│ │   L03: Why Outputs  │ │
│ │   Vary              │ │
│ └─────────────────────┘ │
│                         │
│ [🏠] [📝] [📊]         │ ← Bottom nav (sticky)
│ Home Practice Progress  │
└─────────────────────────┘
Node States:
StateVisualCSSClickableDescriptionCompleted✓ in teal circlebg-teal-600 text-whiteYesLesson passed (quiz 2/3+)Active● in teal circle, pulsingbg-teal-600 animate-pulseYesNext available lessonLocked○ in gray circlebg-gray-300 text-gray-500NoPrerequisites incomplete
Node Structure (Each Lesson):
html<div class="lesson-node">
  <div class="node-circle {state-class}">
    {state === 'completed' ? '✓' : lessonNumber}
  </div>
  <div class="node-label">
    <div class="lesson-id">L{lessonNumber.padStart(2, '0')}</div>
    <div class="lesson-title">{shortTitle}</div>
  </div>
</div>
Components:

Top Bar (sticky, fixed to top)

Streak counter (🔥 + number)
Points counter (💎 + number)
Profile avatar (tap to open settings - future)


Course Header

Course title
Progress bar (17 segments)
Progress text (X/17)


Scrollable Lesson List

17 lesson nodes (vertically stacked)
Each node: Circle + Lesson ID + Short Title


Bottom Navigation (sticky, fixed to bottom)

Interactions:

Tap Completed Lesson:

Navigate to /lesson/{lessonId}?mode=review
Video plays in review mode (doesn't affect progress)


Tap Active Lesson:

Navigate to /lesson/{lessonId}
Start lesson at current difficulty


Tap Locked Lesson:

No action (visual feedback only)
Optional: Show tooltip "Complete previous lessons first"



Data Flow:
javascript// On mount
useEffect(() => {
  const { completedLessons, startingLesson } = getFromLocalStorage();
  
  // Build lesson states
  const lessonStates = allLessons.map(lesson => {
    if (completedLessons.includes(lesson.id)) return 'completed';
    if (lesson.id === getNextLesson(completedLessons, startingLesson)) return 'active';
    return 'locked';
  });
  
  setLessons(lessonStates);
}, []);
```

**Scroll Behavior:**
- On mount: Auto-scroll to active lesson (bring into view)
- User can manually scroll up/down
- Scroll position saved in sessionStorage (persist on tab switch)

**Accessibility:**
- Progress bar: `role="progressbar" aria-valuenow="3" aria-valuemax="17"`
- Locked lessons: `aria-disabled="true"`
- Active lesson: `aria-current="step"`

**Edge Cases:**
- User completes L17 (last lesson) → All nodes show checkmark, no active node
- User skipped pre-assessment → Only L01 active, all others locked
- User completed pre-assessment, placed at L06 → L01-L05 locked, L06 active, L07-L17 locked

---

### **5.5 Lesson Player Screen**

**Route:** `/lesson/{lessonId}`  
**Purpose:** Core learning experience - watch video, adapt content  
**Trigger:** Tap lesson node from Course Map  

**Layout:**
```
┌─────────────────────────┐
│ [✕]         L05 (3min)  │ ← Header (auto-hide after 3s)
│                         │
│                         │
│                         │
│      VIDEO AREA         │
│    (9:16 aspect)        │
│    1080 × 1920          │
│                         │
│                   [⚡]  │ ← Adapt button (floating)
│                  Adapt  │    Always visible
│                         │
│ ▓▓▓▓▓░░░░░░░░ 45%      │ ← Progress bar
│ [▶] [🔇] [1x] [↻]     │ ← Controls
└─────────────────────────┘
Components:
1. Header (Auto-Hide):
javascript// Auto-hide after 3 seconds of inactivity
// Show on tap anywhere on screen
<header className={`transition-opacity ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
  <button onClick={handleClose}>✕ Close</button>
  <span>{lessonId}: {lessonTitle}</span>
  <span>{duration} min</span>
</header>
2. Video Player:
html<video
  ref={videoRef}
  src={videoUrl}
  className="w-full h-full object-cover"
  onTimeUpdate={handleProgress}
  onEnded={handleVideoEnd}
  playsInline
  preload="auto"
>
  <track
    kind="captions"
    src={captionsUrl}
    srcLang="en"
    label="English"
    default
  />
</video>
3. Adapt Button (Floating, Always Visible):
javascript<button
  className="fixed right-4 top-1/2 -translate-y-1/2 z-50
             bg-teal-600 text-white px-4 py-3 rounded-full
             shadow-lg hover:bg-teal-700 active:scale-95
             transition-all duration-200"
  onClick={handleAdaptClick}
>
  <span className="text-2xl">⚡</span>
  <span className="block text-sm font-semibold">Adapt</span>
</button>
Position: right: 16px, top: 50% (vertically centered, right side)
Z-index: 50 (above video, below overlays)
Always visible: Does NOT auto-hide
4. Progress Bar:
javascript<div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
  <div
    className="h-full bg-teal-500 transition-all duration-300"
    style={{ width: `${(currentTime / duration) * 100}%` }}
  />
</div>
<span className="text-white text-sm">{Math.round((currentTime / duration) * 100)}%</span>
5. Bottom Controls:
javascript<div className="flex items-center justify-between px-4 py-2 bg-black/50">
  {/* Play/Pause */}
  <button onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
    {isPlaying ? '⏸' : '▶'}
  </button>
  
  {/* Mute */}
  <button onClick={toggleMute} aria-label={isMuted ? 'Unmute' : 'Mute'}>
    {isMuted ? '🔇' : '🔊'}
  </button>
  
  {/* Speed (Toggle Cycle) */}
  <button onClick={cycleSpeed} aria-label={`Speed: ${speed}x`}>
    {speed}x
  </button>
  
  {/* Replay */}
  <button onClick={handleReplay} aria-label="Replay from start">
    ↻
  </button>
</div>
Speed Cycle Logic:
javascriptconst [speed, setSpeed] = useState(1);

const cycleSpeed = () => {
  const speeds = [1, 1.25, 1.5];
  const currentIndex = speeds.indexOf(speed);
  const nextSpeed = speeds[(currentIndex + 1) % speeds.length];
  setSpeed(nextSpeed);
  videoRef.current.playbackRate = nextSpeed;
};
Interactions:
Tap Video Area:

Toggle play/pause
Show controls (if hidden)
Reset auto-hide timer (3s)

Tap Adapt Button:

Pause video
Show Adapt Menu overlay (see 5.6)

Tap Close:

Stop video
Navigate back to Course Map
Save current position to LocalStorage (for resume)

Video End:

Auto-pause
Navigate to Quiz screen (/quiz/{lessonId})

Tap Replay:

Reset video to 0:00
Resume playing

Keyboard Controls (Desktop):

Space: Play/Pause
M: Mute
S: Cycle speed
R: Replay
Escape: Close

State Management:
javascriptconst [videoUrl, setVideoUrl] = useState(null);
const [isPlaying, setIsPlaying] = useState(false);
const [isMuted, setIsMuted] = useState(false);
const [speed, setSpeed] = useState(1);
const [currentTime, setCurrentTime] = useState(0);
const [duration, setDuration] = useState(0);

// On mount: Fetch video URL
useEffect(() => {
  const fetchVideo = async () => {
    const { userId } = getFromLocalStorage();
    const { currentDifficulty } = getProgressData();
    
    const response = await fetch(
      `/api/v1/lessons/${lessonId}?userId=${userId}&difficulty=${currentDifficulty}`
    );
    const { videoUrl, duration, captionsUrl } = await response.json();
    
    setVideoUrl(videoUrl);
    setDuration(duration);
  };
  
  fetchVideo();
}, [lessonId]);
Loading State:
javascriptif (!videoUrl) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-teal-600 border-t-transparent"></div>
      <p className="mt-4 text-gray-600">Loading your personalized lesson...</p>
    </div>
  );
}
Error State:
javascriptif (error) {
  return (
    <div className="flex flex-col items-center justify-center h-screen px-6 text-center">
      <p className="text-xl font-semibold text-gray-800 mb-2">Oops!</p>
      <p className="text-gray-600 mb-6">Couldn't load this lesson. Please try again.</p>
      <button onClick={handleRetry} className="btn-primary">Retry</button>
      <button onClick={handleGoBack} className="btn-secondary mt-2">Go Back</button>
    </div>
  );
}
```

**Accessibility:**
- Video has captions (served from backend as .vtt)
- All buttons have aria-labels
- Keyboard navigation supported
- Focus visible (teal outline)

---

### **5.6 Adapt Menu Overlay**

**Trigger:** User taps Adapt button during lesson  
**Purpose:** Select adaptation type  

**Layout:**
```
┌─────────────────────────┐
│                         │
│   VIDEO (dimmed 50%)    │
│                         │
│  ┌─────────────────────┐│
│  │ How can we adapt?   ││ ← Modal header
│  │                     ││
│  │ [🧩 Simplify this]  ││ ← Option 1
│  │ Make it easier      ││    (icon + title + subtitle)
│  │                     ││
│  │ [⚡ Get to the point]││ ← Option 2
│  │ Skip the fluff      ││
│  │                     ││
│  │ [✅ I know this]    ││ ← Option 3
│  │ Quiz me to skip     ││
│  │                     ││
│  │ [💡 More examples]  ││ ← Option 4
│  │ Show me more        ││
│  │                     ││
│  │ [Cancel]            ││ ← Cancel button (text)
│  └─────────────────────┘│
│                         │
└─────────────────────────┘
Components:

Full-screen overlay (bg-black/50)
Centered modal card (bg-white rounded-2xl)
4 option buttons (large tap targets)
Cancel button (text link)

Option Buttons:
javascriptconst adaptOptions = [
  {
    id: 'simplify_this',
    icon: '🧩',
    title: 'Simplify this',
    subtitle: 'Make it easier to understand',
    color: 'green'
  },
  {
    id: 'get_to_the_point',
    icon: '⚡',
    title: 'Get to the point',
    subtitle: 'Skip the fluff',
    color: 'orange'
  },
  {
    id: 'i_know_this_already',
    icon: '✅',
    title: 'I know this already',
    subtitle: 'Quiz me to skip ahead',
    color: 'blue'
  },
  {
    id: 'more_examples',
    icon: '💡',
    title: 'More examples',
    subtitle: 'Show me real-world cases',
    color: 'purple'
  }
];
```

**Interactions:**

**Tap "Simplify this":**
1. Close overlay
2. Show loading state (see 5.7)
3. POST `/api/v1/lessons/adapt` with `{ type: 'simplify_this', lessonId, userId, currentDifficulty }`
4. Backend returns new video URL (difficulty 1)
5. Load new video
6. Resume playing from 0:00

**Tap "Get to the point":**
1. Same as above, but `type: 'get_to_the_point'`
2. Backend returns difficulty 5 video

**Tap "I know this already":**
1. Close overlay
2. Keep video paused (don't navigate away)
3. Show Checkpoint Quiz overlay (see 5.8)

**Tap "More examples":**
1. Close overlay
2. Show loading state
3. POST `/api/v1/lessons/adapt` with `{ type: 'more_examples' }`
4. Backend returns pre-rendered "more examples" video
5. Load and play new video

**Tap "Cancel":**
1. Close overlay
2. Resume video from where it paused

**Tap outside modal (on dimmed background):**
1. Same as Cancel

**Accessibility:**
- Modal: `role="dialog" aria-labelledby="adapt-title" aria-modal="true"`
- Trap focus inside modal (Tab cycles through options)
- Escape key: Close modal
- First focusable element: First option button

**Animation:**
- Modal slides up from bottom (0.3s ease-out)
- Overlay fades in (0.3s)

---

### **5.7 Adaptation Loading State**

**Trigger:** User selects adaptation type (except "I know this already")  
**Purpose:** Show progress while backend generates new video  
**Duration:** 10-30 seconds (pre-generated) or up to 2 minutes (on-demand)  

**Layout:**
```
┌─────────────────────────┐
│                         │
│                         │
│   [Animated Spinner]    │ ← Rotating circle
│                         │
│  Personalizing your     │ ← Status text, 18px
│  lesson...              │
│                         │
│  💡 Did you know?       │ ← Fun fact header
│  GPT-3 has 175 billion  │ ← Rotating fact
│  parameters             │
│                         │
│                         │
└─────────────────────────┘
Components:

Spinner (CSS animation or SVG)
Status text
Fun fact display (rotates every 3 seconds)

Fun Facts (Rotate):
javascriptconst funFacts = [
  "GPT-3 has 175 billion parameters",
  "LLMs can write code in 50+ languages",
  "Claude can process 200K tokens of context",
  "The first GPT was released in 2018",
  "Transformers were invented in 2017",
  "ChatGPT reached 100M users in 2 months",
  "LLMs are trained on trillions of words",
  "GPT-4 can analyze images and text"
];

const [factIndex, setFactIndex] = useState(0);

useEffect(() => {
  const interval = setInterval(() => {
    setFactIndex(prev => (prev + 1) % funFacts.length);
  }, 3000);
  return () => clearInterval(interval);
}, []);
Timeout Handling:
javascript// If generation takes >2 minutes, show error
const [isTimeout, setIsTimeout] = useState(false);

useEffect(() => {
  const timeout = setTimeout(() => {
    setIsTimeout(true);
  }, 120000); // 2 minutes
  
  return () => clearTimeout(timeout);
}, []);

if (isTimeout) {
  return (
    <div className="error-state">
      <p>This is taking longer than expected.</p>
      <button onClick={handleRetry}>Try Again</button>
      <button onClick={handleGoBack}>Go Back to Original</button>
    </div>
  );
}
```

**Accessibility:**
- Status: `aria-live="polite"` (announces status changes)
- Spinner: `aria-label="Loading your personalized lesson"`

---

### **5.8 Checkpoint Quiz Overlay** ("I Know This Already")

**Trigger:** User taps "I know this already" from Adapt Menu  
**Purpose:** Validate knowledge, skip lesson if passed  

**Layout:**
```
┌─────────────────────────┐
│ [✕]                     │ ← Close button (top-right)
│                         │
│  Prove it! 🎯          │ ← Title, 24px bold
│  Answer 2/3 correctly   │ ← Subtitle, 14px
│  to skip ahead          │
│                         │
│  Question 1 of 3        │ ← Progress text
│                         │
│  [Quiz UI - see 5.9]    │ ← Same as lesson quiz
│                         │
└─────────────────────────┘
```

**Flow:**
1. Show 3 questions (from backend)
2. User answers all 3 (same UI as lesson quiz)
3. Calculate score

**IF PASS (2/3 or 3/3):**
```
┌─────────────────────────┐
│      ✅                 │
│   Nice work!            │
│                         │
│   You got 3/3 correct   │
│   Skipping to L06...    │
│                         │
│   [Continue →]          │
└─────────────────────────┘
```
- Mark current lesson as complete
- Update streak & points (+30 for 3/3, +20 for 2/3)
- Navigate to next lesson (`/lesson/{nextLessonId}`)

**IF FAIL (0/3 or 1/3):**
```
┌─────────────────────────┐
│      📚                 │
│   Not quite there yet   │
│                         │
│   You got 1/3 correct   │
│   Let's review together │
│                         │
│   [Resume Lesson]       │
└─────────────────────────┘
```
- Close overlay
- Resume video from where it paused
- Do NOT mark lesson complete
- Do NOT award points

**Components:**
- Same quiz UI as 5.9 (reusable component)
- Success/failure modals

**Interactions:**
- Tap Close (✕): Cancel quiz, resume video
- Tap Continue (after pass): Navigate to next lesson
- Tap Resume Lesson (after fail): Close modal, resume video

---

### **5.9 Quiz Screen** (Lesson Quiz)

**Route:** `/quiz/{lessonId}`  
**Trigger:** Video completes OR checkpoint quiz  
**Purpose:** Validate learning, unlock next lesson  

**Layout:**
```
┌─────────────────────────┐
│  [← Back]               │
│                         │
│  Quiz: L05              │ ← Title
│  Question 1 of 3        │ ← Progress
│                         │
│  What causes LLMs to    │ ← Question text (18px)
│  hallucinate?           │
│                         │
│  ○ A) Lack of training  │ ← Option A (default state)
│     data                │
│                         │
│  ○ B) Pattern prediction│ ← Option B
│     over facts          │
│                         │
│  ○ C) User error        │ ← Option C
│                         │
│  ○ D) Poor prompting    │ ← Option D
│                         │
└─────────────────────────┘
```

**Question Flow (No Retries):**

**1. Initial State:**
- All options unselected (radio buttons)
- No feedback shown

**2. User Selects Answer:**
- Selected option highlights (teal border)
- Instant feedback appears

**3a. Correct Answer:**
```
┌─────────────────────────┐
│  ✅ Correct!            │ ← Feedback banner (green bg)
│                         │
│  ● B) Pattern prediction│ ← Selected option (green border)
│     over facts          │
│                         │
│  Explanation:           │ ← Explanation text (from backend)
│  LLMs prioritize        │
│  probability over truth │
│  which can lead to      │
│  hallucinations.        │
│                         │
│  [Next Question →]      │ ← Auto-appear after 1s
└─────────────────────────┘
```

**3b. Wrong Answer:**
```
┌─────────────────────────┐
│  ❌ Not quite           │ ← Feedback banner (red bg)
│                         │
│  ○ A) Lack of training  │ ← Selected option (red border)
│     data                │
│                         │
│  Explanation:           │ ← Explanation text
│  While training data    │
│  matters, hallucinations│
│  stem from pattern-based│
│  prediction...          │
│                         │
│  [Next Question →]      │ ← Auto-appear after 1s
└─────────────────────────┘
Note: With "no retries" (Q4 answer), user CANNOT change their answer after selecting. They see feedback immediately and move to next question.
4. After 3 Questions:

Navigate to Quiz Results (5.10)

Components:

Header with back button
Quiz title + progress
Question text
4 radio button options
Feedback banner (conditional)
Explanation text (conditional)
Next button (conditional)

State Management:
javascriptconst [questions, setQuestions] = useState([]);
const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
const [userAnswers, setUserAnswers] = useState([]);
const [showFeedback, setShowFeedback] = useState(false);

const handleSelectAnswer = (selectedOption) => {
  const question = questions[currentQuestionIndex];
  const isCorrect = selectedOption === question.correctAnswer;
  
  // Record answer
  const newAnswer = {
    questionId: question.id,
    selected: selectedOption,
    correct: isCorrect
  };
  setUserAnswers([...userAnswers, newAnswer]);
  
  // Show feedback
  setShowFeedback(true);
  
  // Auto-show Next button after 1s
  setTimeout(() => {
    setShowNextButton(true);
  }, 1000);
};

const handleNext = () => {
  if (currentQuestionIndex < questions.length - 1) {
    // Next question
    setCurrentQuestionIndex(prev => prev + 1);
    setShowFeedback(false);
    setShowNextButton(false);
  } else {
    // Quiz complete
    navigateToResults();
  }
};
Data Flow:
javascript// On mount: Fetch quiz questions
useEffect(() => {
  const fetchQuiz = async () => {
    const { userId } = getFromLocalStorage();
    const response = await fetch(`/api/v1/quizzes/${lessonId}?userId=${userId}`);
    const { questions } = await response.json();
    setQuestions(questions);
  };
  
  fetchQuiz();
}, [lessonId]);
```

**Accessibility:**
- Radio group: `<fieldset><legend>{questionText}</legend>...</fieldset>`
- Feedback: `aria-live="assertive"` (immediate announcement)
- Progress: `aria-label="Question 1 of 3"`

---

### **5.10 Quiz Results Screen**

**Route:** `/quiz/{lessonId}/results`  
**Trigger:** User completes all 3 quiz questions  
**Purpose:** Show score, award points, unlock next lesson  

**Layout - Pass (2/3 or 3/3):**
```
┌─────────────────────────┐
│      🎉                 │ ← Celebration icon (large)
│   Lesson Complete!      │ ← Title, 28px bold
│                         │
│   You got 3/3 correct   │ ← Score, 20px
│                         │
│   +30 points  💎        │ ← Points earned
│   🔥 4 day streak       │ ← Streak maintained/increased
│                         │
│                         │
│   [Continue Learning →] │ ← Primary CTA
│                         │
│   [Review Lesson]       │ ← Secondary action (text link)
└─────────────────────────┘
```

**Layout - Fail (0/3 or 1/3):**
```
┌─────────────────────────┐
│      📚                 │
│   Let's try again       │
│                         │
│   You got 1/3 correct   │
│                         │
│   Don't worry! Learning │
│   takes time.           │
│                         │
│   [Re-watch Lesson]     │ ← Primary CTA
│                         │
│   [Try Simpler Version] │ ← Alternative (optional)
└─────────────────────────┘
Scoring Logic:
ScoreResultPointsStreakNext Lesson3/3Pass+30✓ Maintain/IncreaseUnlocked2/3Pass+20✓ MaintainUnlocked1/3Fail+10✗ No changeLocked0/3Fail+0✗ No changeLocked
Interactions:
Pass → "Continue Learning":

Update LocalStorage:

Add lesson to completedLessons
Increment totalPoints by earned amount
Update streak if applicable
Mark next lesson as unlocked


Navigate to /course-map
Auto-scroll to next lesson (active node)

Pass → "Review Lesson":

Navigate to /lesson/{lessonId}?mode=review
Play lesson again (doesn't affect progress)

Fail → "Re-watch Lesson":

Navigate to /lesson/{lessonId}
Play lesson at same difficulty
Quiz score NOT saved (can retry)

Fail → "Try Simpler Version":

Update current difficulty to currentDifficulty - 1 (minimum 1)
Navigate to /lesson/{lessonId}
Backend serves easier version
Quiz score NOT saved

Components:

Icon (emoji, large, centered)
Title
Score display
Points/streak display (conditional, pass only)
CTA buttons

State Updates:
javascriptconst handleContinue = () => {
  // Update LocalStorage
  const progress = getProgressData();
  
  updateProgress({
    completedLessons: [...progress.completedLessons, lessonId],
    totalPoints: progress.totalPoints + pointsEarned,
    streak: calculateStreak(progress.lastActiveDate),
    lastActiveDate: new Date().toISOString().split('T')[0]
  });
  
  // Navigate
  router.push('/course-map');
};
```

**Accessibility:**
- Score announced: `aria-live="polite"`
- Buttons: Clear aria-labels
- Focus on primary CTA on load

---

### **5.11 Let's Practice Tab**

**Route:** `/practice`  
**Trigger:** Tap "Let's Practice" in bottom nav  
**Purpose:** Daily active recall quiz from completed lessons  

**Layout - Available:**
```
┌─────────────────────────┐
│  Let's Practice 📝      │ ← Tab title
│                         │
│  Daily Challenge        │ ← Section header
│  Test your knowledge!   │
│                         │
│  ┌─────────────────────┐│
│  │ 🎯 10 Questions     ││ ← Info card
│  │ 💎 10 pts each      ││
│  │ 🔥 Keep your streak ││
│  │                     ││
│  │ [Start Practice →]  ││ ← CTA
│  └─────────────────────┘│
│                         │
│  From lessons:          │ ← Context
│  • L01-L05 (completed)  │
│                         │
└─────────────────────────┘
```

**Layout - In Progress:**
```
┌─────────────────────────┐
│  Practice Quiz          │
│  Question 3 of 10       │ ← Progress
│                         │
│  [Quiz UI - see 5.9]    │ ← Same quiz component
│                         │
└─────────────────────────┘
```

**Layout - Completed:**
```
┌─────────────────────────┐
│  Let's Practice 📝      │
│                         │
│  ✅ Completed Today     │
│                         │
│  Great work! You earned │
│  80/100 points          │
│                         │
│  ┌─────────────────────┐│
│  │ Your Answers:       ││
│  │ ✓✓✓✓✓✓✗✓✗✓        ││ ← Visual summary
│  │                     ││
│  │ 8/10 correct        ││
│  └─────────────────────┘│
│                         │
│  ⏰ Next challenge in   │
│  14h 32m                │
│                         │
└─────────────────────────┘
```

**Layout - Locked (No Completed Lessons):**
```
┌─────────────────────────┐
│  Let's Practice 📝      │
│                         │
│  🔒 Locked              │
│                         │
│  Complete your first    │
│  lesson to unlock daily │
│  practice!              │
│                         │
│  [Go to Lessons →]      │
│                         │
└─────────────────────────┘
States:
StateConditionDisplayAvailableCompleted ≥1 lesson AND haven't practiced today"Start Practice" buttonIn ProgressStarted practice, haven't finishedResume quizCompletedFinished today's practiceScore summary + countdownLockedNo completed lessonsLocked message
Daily Reset Logic:
javascriptconst isDailyPracticeAvailable = () => {
  const { completedLessons, lastPracticeDate } = getProgressData();
  
  // Check if any lessons completed
  if (completedLessons.length === 0) return false;
  
  // Check if practiced today
  const today = new Date().toISOString().split('T')[0];
  if (lastPracticeDate === today) return false;
  
  return true;
};
Question Serving:

Backend serves up to 10 random questions from completed lessons
All single-choice MCQ
No retries (same as lesson quiz behavior)
Instant feedback per question

Scoring:

10 points per correct answer
Max 100 points per day
Score saved to LocalStorage

Interactions:
Tap "Start Practice":

Fetch questions: GET /api/v1/practice/daily?userId={userId}
Backend returns up to 10 questions
Show quiz UI (same as 5.9)

Complete Practice:

Calculate score (correct answers × 10)
Update LocalStorage:

practicePointsToday: score
lastPracticeDate: today
totalPoints: totalPoints + score


Show completion screen

Countdown Timer:
javascriptconst getTimeUntilReset = () => {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);
  
  const diff = tomorrow - now;
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
};
```

**Accessibility:**
- Practice status: `aria-live="polite"`
- Locked state: Clear explanation why locked

---

### **5.12 Progress Tab**

**Route:** `/progress`  
**Trigger:** Tap "Progress" in bottom nav  
**Purpose:** View learning stats, streak, points, lesson history  

**Layout:**
```
┌─────────────────────────┐
│  Your Progress 📊       │ ← Title
│                         │
│  Overall Progress       │ ← Section header
│  ▓▓▓░░░░░░░░░░░░░░      │ ← Progress bar (17 segments)
│  3/17 Lessons (18%)     │ ← Text summary
│                         │
│  ┌─────────────────────┐│
│  │ 🔥 4 Day Streak     ││ ← Stats card
│  │ 💎 80 Points        ││
│  │ ⏱️ 45 min learned   ││
│  │ ✅ 3 Completed      ││
│  └─────────────────────┘│
│                         │
│  Recent Activity        │ ← Section header
│  ┌─────────────────────┐│
│  │ ✓ L03: Why Outputs  ││ ← Completed lesson
│  │   Vary              ││
│  │   Yesterday • 3/3   ││ ← Date + score
│  └─────────────────────┘│
│  ┌─────────────────────┐│
│  │ ✓ L02: Tokens       ││
│  │   2 days ago • 2/3  ││
│  └─────────────────────┘│
│  ┌─────────────────────┐│
│  │ ✓ L01: What LLMs Are││
│  │   3 days ago • 3/3  ││
│  └─────────────────────┘│
│                         │
│  Daily Practice         │ ← Section header
│  ┌─────────────────────┐│
│  │ Today: 8/10 ✓       ││
│  │ This week: 5/7 days ││
│  └─────────────────────┘│
│                         │
└─────────────────────────┘
Components:
1. Overall Progress:

Visual progress bar (17 segments, colored based on completion)
Text summary (X/17, percentage)

2. Stats Card:

Streak (🔥 + number)
Points (💎 + number)
Learning time (⏱️ + minutes)
Completed count (✅ + number)

3. Recent Activity:

List of last 5 completed lessons
Each entry: Lesson title, date, quiz score
Tap to review lesson

4. Daily Practice:

Today's practice status
Weekly practice summary (days practiced this week)

Data Sources:
javascript// From LocalStorage
const {
  completedLessons,
  lessonScores,
  totalPoints,
  streak,
  lastActiveDate,
  totalLearningTimeSeconds
} = getProgressData();

// Calculate stats
const completionPercentage = Math.round((completedLessons.length / 17) * 100);
const learningTimeMinutes = Math.round(totalLearningTimeSeconds / 60);

// Get recent activity
const recentLessons = completedLessons
  .map(lessonId => ({
    id: lessonId,
    title: getLessonTitle(lessonId),
    score: lessonScores[lessonId]?.score,
    total: lessonScores[lessonId]?.total,
    date: lessonScores[lessonId]?.passedAt
  }))
  .sort((a, b) => new Date(b.date) - new Date(a.date))
  .slice(0, 5);
```

**Interactions:**

**Tap Completed Lesson:**
- Navigate to `/lesson/{lessonId}?mode=review`
- Play lesson in review mode

**No other interactions** (read-only stats page)

**Accessibility:**
- Progress bar: `role="progressbar" aria-valuenow="3" aria-valuemax="17"`
- Stats: Semantic HTML (dl, dt, dd)
- Recent activity: `<ol>` list with proper structure

---

### **5.13 Bottom Navigation**

**Component:** Fixed bottom bar, always visible  
**Routes:** All screens except Welcome, Profession Select, Pre-Assessment  

**Layout:**
```
┌─────────────────────────┐
│                         │
│   [Screen Content]      │
│                         │
├─────────────────────────┤
│ [🏠]    [📝]    [📊]   │ ← Icons (48×48 tap target)
│ Home   Practice Progress│ ← Labels (12px)
└─────────────────────────┘
Tabs:
IconLabelRouteBadge🏠Home/course-mapNone📝Let's Practice/practiceRed dot if available📊Progress/progressNone
Active State:

Icon color: Teal (#007373)
Label: Bold
Background: Subtle teal background (10% opacity)

Inactive State:

Icon color: Gray (#9CA3AF)
Label: Regular weight

Badge Logic:
javascriptconst isPracticeBadgeVisible = () => {
  const { completedLessons, lastPracticeDate } = getProgressData();
  const today = new Date().toISOString().split('T')[0];
  
  // Show badge if practice available (completed lessons + haven't practiced today)
  return completedLessons.length > 0 && lastPracticeDate !== today;
};
Implementation:
javascript<nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-inset-bottom">
  <div className="flex items-center justify-around h-16">
    {tabs.map(tab => (
      <Link
        key={tab.id}
        href={tab.route}
        className={`flex flex-col items-center justify-center flex-1 h-full
                   ${isActive ? 'text-teal-600 bg-teal-50' : 'text-gray-500'}`}
      >
        <div className="relative">
          <span className="text-2xl">{tab.icon}</span>
          {tab.badge && <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />}
        </div>
        <span className="text-xs mt-1">{tab.label}</span>
      </Link>
    ))}
  </div>
</nav>
```

**Accessibility:**
- `<nav aria-label="Main navigation">`
- Active tab: `aria-current="page"`
- Badge: `aria-label="New practice available"`

---

### **5.14 Top Bar**

**Component:** Sticky header, visible on Course Map, Practice, Progress  
**Not visible:** Welcome, Profession Select, Pre-Assessment, Lesson Player  

**Layout:**
```
┌─────────────────────────┐
│ [🔥 4] [💎 80]   [👤]  │ ← Left: Streak, Center: Points, Right: Avatar
└─────────────────────────┘
Components:
1. Streak Counter:
javascript<div className="flex items-center gap-1">
  <span className="text-xl">🔥</span>
  <span className="text-sm font-semibold">{streak}</span>
</div>
2. Points Counter:
javascript<div className="flex items-center gap-1">
  <span className="text-xl">💎</span>
  <span className="text-sm font-semibold">{totalPoints}</span>
</div>
3. Profile Avatar (Future):
javascript<button className="w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold">
  {initials}
</button>

For hackathon: Shows user initials (e.g., "CR" for Clinical Researcher)
Tap: No action (future: open settings modal)

Data Sources:
javascriptconst { streak, totalPoints, profession } = getProgressData();
const initials = profession.split(' ').map(w => w[0]).join('');
```

**Accessibility:**
- Streak: `aria-label="${streak} day learning streak"`
- Points: `aria-label="${totalPoints} points earned"`
- Avatar: `aria-label="User profile"`

---

## **6. Component Architecture**

### **6.1 Component Hierarchy**
```
App
├── Layout
│   ├── TopBar (conditional)
│   ├── <Page Content>
│   └── BottomNav (conditional)
│
├── Pages
│   ├── WelcomeScreen
│   ├── ProfessionSelect
│   ├── PreAssessment
│   ├── CourseMap
│   ├── LessonPlayer
│   ├── QuizScreen
│   ├── QuizResults
│   ├── Practice
│   └── Progress
│
├── Shared Components
│   ├── Button (Primary, Secondary, Text)
│   ├── Card
│   ├── Input (Text, Select, Radio)
│   ├── Modal (Overlay, Dialog)
│   ├── ProgressBar
│   ├── LoadingSpinner
│   ├── ErrorMessage
│   └── QuizQuestion (Reusable)
│
└── Contexts
    ├── UserContext (profile data)
    ├── ProgressContext (learning progress)
    └── LessonContext (active lesson state)
6.2 Reusable Components
Button Component:
tsx// components/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'text';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant,
  children,
  onClick,
  disabled,
  className
}) => {
  const baseStyles = 'px-6 py-3 rounded-lg font-semibold transition-all duration-200';
  
  const variants = {
    primary: 'bg-teal-600 text-white hover:bg-teal-700 active:scale-95 disabled:bg-gray-300',
    secondary: 'bg-white text-teal-600 border-2 border-teal-600 hover:bg-teal-50',
    text: 'bg-transparent text-teal-600 hover:text-teal-700'
  };
  
  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
Quiz Question Component:
tsx// components/QuizQuestion.tsx
interface QuizQuestionProps {
  question: {
    id: string;
    questionText: string;
    options: string[];
    correctAnswer: string;
    explanation: string;
  };
  onAnswer: (selected: string, isCorrect: boolean) => void;
  allowRetry?: boolean;
}

export const QuizQuestion: React.FC<QuizQuestionProps> = ({
  question,
  onAnswer,
  allowRetry = false
}) => {
  const [selected, setSelected] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  
  const handleSelect = (option: string) => {
    if (showFeedback && !allowRetry) return; // No retry allowed
    
    setSelected(option);
    const isCorrect = option === question.correctAnswer;
    setShowFeedback(true);
    
    onAnswer(option, isCorrect);
  };
  
  return (
    <div className="quiz-question">
      <h3 className="text-lg font-semibold mb-4">{question.questionText}</h3>
      
      <div className="space-y-3">
        {question.options.map((option) => (
          <button
            key={option}
            onClick={() => handleSelect(option)}
            disabled={showFeedback && !allowRetry}
            className={`
              w-full text-left p-4 rounded-lg border-2 transition-all
              ${selected === option
                ? showFeedback
                  ? selected === question.correctAnswer
                    ? 'border-green-500 bg-green-50'
                    : 'border-red-500 bg-red-50'
                  : 'border-teal-500 bg-teal-50'
                : 'border-gray-300 hover:border-teal-300'
              }
            `}
          >
            {option}
          </button>
        ))}
      </div>
      
      {showFeedback && (
        <div className={`mt-4 p-4 rounded-lg ${
          selected === question.correctAnswer ? 'bg-green-100' : 'bg-red-100'
        }`}>
          <p className="font-semibold mb-2">
            {selected === question.correctAnswer ? '✅ Correct!' : '❌ Not quite'}
          </p>
          <p className="text-sm">{question.explanation}</p>
        </div>
      )}
    </div>
  );
};
Loading Spinner Component:
tsx// components/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  message?: string;
  showFunFact?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  showFunFact = false
}) => {
  const funFacts = [
    "GPT-3 has 175 billion parameters",
    "LLMs can write code in 50+ languages",
    "Claude can process 200K tokens of context"
  ];
  
  const [factIndex, setFactIndex] = useState(0);
  
  useEffect(() => {
    if (!showFunFact) return;
    
    const interval = setInterval(() => {
      setFactIndex(prev => (prev + 1) % funFacts.length);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [showFunFact]);
  
  return (
    <div className="flex flex-col items-center justify-center h-screen px-6">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-teal-600 border-t-transparent mb-4" />
      <p className="text-gray-600 text-center mb-2">{message}</p>
      
      {showFunFact && (
        <div className="mt-4 text-center">
          <p className="text-sm font-semibold text-teal-600 mb-1">💡 Did you know?</p>
          <p className="text-sm text-gray-600">{funFacts[factIndex]}</p>
        </div>
      )}
    </div>
  );
};

7. Data Models & State Management
7.1 LocalStorage Schema
Key: vina_user
typescriptinterface VinaUser {
  userId: string; // UUID v4
  profession: string; // "Clinical Researcher" | "HR Manager" | "Project Manager" | "Marketing Manager"
  createdAt: string; // ISO timestamp
}
Key: vina_progress
typescriptinterface VinaProgress {
  currentLessonId: string; // e.g., "l05_hallucinations"
  completedLessons: string[]; // ["l01_what_llms_are", "l02_tokens_context", ...]
  
  lessonScores: {
    [lessonId: string]: {
      score: number; // 0-3
      total: number; // Always 3
      passedAt: string; // ISO timestamp
    };
  };
  
  currentDifficulty: number; // 1, 3, or 5
  
  totalPoints: number; // Accumulated points
  streak: number; // Days
  lastActiveDate: string; // "2026-02-07" (YYYY-MM-DD)
  
  practicePointsToday: number; // 0-100
  lastPracticeDate: string; // "2026-02-07"
  
  totalLearningTimeSeconds: number; // Cumulative
  
  preAssessmentCompleted: boolean;
  preAssessmentScore: number; // 0-10
  startingLesson: string; // e.g., "l06_bias_issues"
  preAssessmentDate: string; // ISO timestamp
}
Key: vina_session
typescriptinterface VinaSession {
  currentVideoUrl: string;
  videoPosition: number; // Seconds
  adaptationHistory: Array<{
    lessonId: string;
    fromDifficulty: number;
    toDifficulty: number;
    type: 'simplify_this' | 'get_to_the_point' | 'more_examples';
    timestamp: string;
  }>;
}
7.2 React Context Providers
UserContext:
tsx// contexts/UserContext.tsx
interface UserContextType {
  user: VinaUser | null;
  updateUser: (user: VinaUser) => void;
  clearUser: () => void;
}

export const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<VinaUser | null>(() => {
    const saved = localStorage.getItem('vina_user');
    return saved ? JSON.parse(saved) : null;
  });
  
  const updateUser = (newUser: VinaUser) => {
    setUser(newUser);
    localStorage.setItem('vina_user', JSON.stringify(newUser));
  };
  
  const clearUser = () => {
    setUser(null);
    localStorage.removeItem('vina_user');
  };
  
  return (
    <UserContext.Provider value={{ user, updateUser, clearUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser must be used within UserProvider');
  return context;
};
ProgressContext:
tsx// contexts/ProgressContext.tsx
interface ProgressContextType {
  progress: VinaProgress;
  updateProgress: (updates: Partial<VinaProgress>) => void;
  markLessonComplete: (lessonId: string, score: number) => void;
  incrementPoints: (amount: number) => void;
  updateStreak: () => void;
  resetProgress: () => void;
}

export const ProgressProvider: React.FC = ({ children }) => {
  const [progress, setProgress] = useState<VinaProgress>(() => {
    const saved = localStorage.getItem('vina_progress');
    return saved ? JSON.parse(saved) : DEFAULT_PROGRESS;
  });
  
  const updateProgress = (updates: Partial<VinaProgress>) => {
    const newProgress = { ...progress, ...updates };
    setProgress(newProgress);
    localStorage.setItem('vina_progress', JSON.stringify(newProgress));
  };
  
  const markLessonComplete = (lessonId: string, score: number) => {
    updateProgress({
      completedLessons: [...progress.completedLessons, lessonId],
      lessonScores: {
        ...progress.lessonScores,
        [lessonId]: {
          score,
          total: 3,
          passedAt: new Date().toISOString()
        }
      }
    });
  };
  
  const incrementPoints = (amount: number) => {
    updateProgress({
      totalPoints: progress.totalPoints + amount
    });
  };
  
  const updateStreak = () => {
    const today = new Date().toISOString().split('T')[0];
    const lastActive = new Date(progress.lastActiveDate);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    let newStreak = progress.streak;
    
    if (progress.lastActiveDate === today) {
      // Already active today, no change
    } else if (progress.lastActiveDate === yesterday.toISOString().split('T')[0]) {
      // Active yesterday, increment
      newStreak += 1;
    } else {
      // Streak broken, reset to 1
      newStreak = 1;
    }
    
    updateProgress({
      streak: newStreak,
      lastActiveDate: today
    });
  };
  
  const resetProgress = () => {
    setProgress(DEFAULT_PROGRESS);
    localStorage.removeItem('vina_progress');
  };
  
  return (
    <ProgressContext.Provider value={{
      progress,
      updateProgress,
      markLessonComplete,
      incrementPoints,
      updateStreak,
      resetProgress
    }}>
      {children}
    </ProgressContext.Provider>
  );
};

8. API Endpoint Specifications
8.1 Overview
Base URL: https://vina-api.railway.app/api/v1
Authentication: None (use userId in request)
Content-Type: application/json

8.2 Profile Endpoints
POST /profiles
Create or retrieve user profile.
Request:
json{
  "profession": "Clinical Researcher"
}
Response (201 Created):
json{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "profile": {
    "profession": "Clinical Researcher",
    "industry": null,
    "experience_level": "Intermediate",
    "daily_responsibilities": [...],
    "pain_points": [...],
    "typical_outputs": [...],
    "technical_comfort_level": "Medium",
    "learning_style_notes": "...",
    "professional_goals": [...],
    "safety_priorities": [...],
    "high_stakes_areas": [...]
  }
}
```

**Notes:**
- For hackathon, `industry` is always `null` (not collected)
- Backend generates profile based on profession only
- Returns existing profile if already created for this profession

---

### **8.3 Pre-Assessment Endpoints**

#### **GET /assessment/pre-quiz**

Get pre-assessment questions for placement.

**Request:**
```
GET /assessment/pre-quiz?profession=Clinical+Researcher
Response (200 OK):
json{
  "questions": [
    {
      "id": "aq_001",
      "questionText": "What does LLM stand for?",
      "options": [
        "A) Large Language Model",
        "B) Linear Learning Machine",
        "C) Logical Language Module",
        "D) Limited Language Memory"
      ],
      "correctAnswer": "A",
      "associatedLesson": "l01_what_llms_are",
      "difficultyLevel": 1
    },
    // ... 9 more questions (total 10)
  ]
}
Notes:

Questions are profession-specific
Ordered by increasing difficulty
Used to determine starting lesson


POST /assessment/submit
Submit pre-assessment answers, get starting lesson.
Request:
json{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "answers": [
    {
      "questionId": "aq_001",
      "selected": "A",
      "correct": true
    },
    {
      "questionId": "aq_002",
      "selected": "C",
      "correct": false
    }
    // ... up to 10 answers
  ]
}
Response (200 OK):
json{
  "startingLesson": "l06_bias_issues",
  "score": 6,
  "placement": "intermediate"
}
Placement Logic (Backend):
pythondef calculate_starting_lesson(answers):
    score = sum(1 for a in answers if a['correct'])
    
    if score <= 2:
        return "l01_what_llms_are"  # Beginner
    elif score <= 4:
        return "l04_where_llms_excel"  # Early intermediate
    elif score <= 6:
        return "l06_bias_issues"  # Mid intermediate
    elif score <= 8:
        return "l09_good_fit_poor_fit"  # Advanced intermediate
    else:
        return "l13_choosing_your_setup"  # Advanced
```

**Notes:**
- If user gets 2 wrong in a row, frontend stops quiz early and submits partial answers
- Backend still calculates placement from partial answers

---

### **8.4 Course Structure Endpoints**

#### **GET /courses/c_llm_foundations**

Get course structure and metadata.

**Request:**
```
GET /courses/c_llm_foundations
Response (200 OK):
json{
  "courseId": "c_llm_foundations",
  "courseTitle": "LLM Foundations",
  "description": "Learn how to use Large Language Models effectively in your professional work",
  "totalLessons": 17,
  "estimatedDuration": "50 minutes",
  
  "lessons": [
    {
      "lessonId": "l01_what_llms_are",
      "lessonNumber": 1,
      "lessonName": "What LLMs Are",
      "shortTitle": "What LLMs Are",
      "topicGroup": "The Foundations",
      "estimatedDuration": 3,
      "prerequisites": []
    },
    {
      "lessonId": "l02_tokens_context",
      "lessonNumber": 2,
      "lessonName": "Tokens & Context Windows",
      "shortTitle": "Tokens & Context",
      "topicGroup": "The Foundations",
      "estimatedDuration": 3,
      "prerequisites": ["l01_what_llms_are"]
    }
    // ... all 17 lessons
  ]
}
```

**Notes:**
- Frontend uses this to build Course Map
- `prerequisites` array determines lesson locking logic
- For hackathon, can be hardcoded in frontend (static data)

---

### **8.5 Lesson Endpoints**

#### **GET /lessons/{lessonId}**

Get video URL for a lesson at specific difficulty.

**Request:**
```
GET /lessons/l05_hallucinations?userId=550e8400-e29b-41d4-a716-446655440000&difficulty=3
Response (200 OK):
json{
  "videoUrl": "https://res.cloudinary.com/vina/video/upload/v1/lessons/l05_clinical_researcher_d3.mp4",
  "duration": 180,
  "captionsUrl": "https://res.cloudinary.com/vina/raw/upload/v1/lessons/l05_clinical_researcher_d3.vtt",
  "difficulty": 3,
  "cached": true
}
Response (202 Accepted - Generating):
json{
  "status": "generating",
  "estimatedSeconds": 45,
  "message": "Personalizing your lesson..."
}

Frontend polls every 3 seconds until status changes to "ready"

Response (500 Error):
json{
  "error": {
    "code": "VIDEO_GENERATION_FAILED",
    "message": "Unable to generate video. Please try again.",
    "retryable": true
  }
}
Notes:

If video is pre-generated (cache hit), returns immediately
If video needs generation (cache miss), returns 202 and generates in background
Frontend shows loading state with fun facts during generation


POST /lessons/adapt
Request adapted version of current lesson.
Request:
json{
  "lessonId": "l05_hallucinations",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "adaptationType": "simplify_this",
  "currentDifficulty": 3
}
Adaptation Types:

"simplify_this" → Regenerate at difficulty 1
"get_to_the_point" → Regenerate at difficulty 5
"more_examples" → Return pre-rendered "more examples" variant
"i_know_this_already" → (Handled separately via checkpoint quiz, not this endpoint)

Response (200 OK):
json{
  "videoUrl": "https://res.cloudinary.com/vina/video/upload/v1/lessons/l05_clinical_researcher_d1.mp4",
  "newDifficulty": 1,
  "duration": 240,
  "captionsUrl": "https://res.cloudinary.com/vina/...",
  "cached": true
}
```

**Response (202 Accepted):**
- Same as GET /lessons/{lessonId} (generating)

**Notes:**
- Frontend updates `currentDifficulty` in ProgressContext after successful adaptation
- This affects the difficulty of NEXT lesson (carry-forward)

---

### **8.6 Quiz Endpoints**

#### **GET /quizzes/{lessonId}**

Get quiz questions for a lesson.

**Request:**
```
GET /quizzes/l05_hallucinations?userId=550e8400-e29b-41d4-a716-446655440000
Response (200 OK):
json{
  "lessonId": "l05_hallucinations",
  "questions": [
    {
      "id": "q_l05_001",
      "questionText": "What causes LLMs to generate incorrect information?",
      "options": [
        "A) Lack of training data",
        "B) Pattern-based prediction",
        "C) User errors in prompting",
        "D) Insufficient context"
      ],
      "correctAnswer": "B",
      "explanation": "LLMs prioritize probability over truth, leading to hallucinations when patterns don't align with facts."
    },
    {
      "id": "q_l05_002",
      "questionText": "In clinical research, hallucinations are most dangerous when...",
      "options": [
        "A) Drafting initial protocol outlines",
        "B) Generating adverse event reports",
        "C) Summarizing published literature",
        "D) Creating meeting agendas"
      ],
      "correctAnswer": "B",
      "explanation": "Adverse event reports directly impact patient safety and regulatory compliance. Hallucinations here could lead to serious harm."
    },
    {
      "id": "q_l05_003",
      "questionText": "Best practice to prevent hallucinations in your work?",
      "options": [
        "A) Use only open-source LLMs",
        "B) Always verify outputs against source data",
        "C) Avoid using LLMs entirely",
        "D) Only use LLMs for final drafts"
      ],
      "correctAnswer": "B",
      "explanation": "Human-in-the-loop verification is essential. Always cross-check LLM outputs with authoritative sources."
    }
  ],
  "passThreshold": 2
}
```

**Notes:**
- Always 3 questions per lesson
- Questions are profession-specific (reference "clinical research" in options)
- Pass threshold is 2/3 correct
- Frontend handles retry logic (no retries for hackathon)

---

#### **GET /quizzes/{lessonId}/checkpoint**

Get checkpoint quiz for "I know this already" feature.

**Request:**
```
GET /quizzes/l05_hallucinations/checkpoint?userId=550e8400-e29b-41d4-a716-446655440000
Response (200 OK):
json{
  "lessonId": "l05_hallucinations",
  "type": "checkpoint",
  "questions": [
    // Same format as regular quiz (3 questions)
  ],
  "passThreshold": 2
}
Notes:

Questions may be slightly different from regular lesson quiz
May be harder (testing if user truly knows this)
Same pass threshold (2/3)


POST /quizzes/submit
Submit quiz answers, get results.
Request:
json{
  "lessonId": "l05_hallucinations",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "quizType": "lesson",
  "answers": [
    {
      "questionId": "q_l05_001",
      "selected": "B",
      "correct": true
    },
    {
      "questionId": "q_l05_002",
      "selected": "A",
      "correct": false
    },
    {
      "questionId": "q_l05_003",
      "selected": "B",
      "correct": true
    }
  ]
}
Quiz Types:

"lesson" → Regular lesson quiz
"checkpoint" → "I know this already" quiz
"practice" → Daily practice quiz

Response (200 OK):
json{
  "score": 2,
  "total": 3,
  "passed": true,
  "pointsEarned": 20,
  "feedback": "Great work! You understand the key concepts.",
  "nextDifficultyAdjustment": 0
}
```

**Next Difficulty Adjustment:**
- `+1`: User got 3/3, increase difficulty for next lesson
- `0`: User got 2/3, maintain difficulty
- `-1`: User got 0-1/3, decrease difficulty for next lesson

**Notes:**
- Backend doesn't store quiz results (stateless)
- Frontend updates LocalStorage with score and difficulty
- Points calculation: 3/3 = 30 pts, 2/3 = 20 pts, 1/3 = 10 pts, 0/3 = 0 pts

---

### **8.7 Practice Endpoints**

#### **GET /practice/daily**

Get daily practice questions.

**Request:**
```
GET /practice/daily?userId=550e8400-e29b-41d4-a716-446655440000
Response (200 OK):
json{
  "practiceDate": "2026-02-07",
  "questions": [
    {
      "id": "pq_001",
      "lessonId": "l01_what_llms_are",
      "questionText": "What is the primary mechanism LLMs use to generate text?",
      "options": [...],
      "correctAnswer": "B",
      "explanation": "..."
    }
    // ... up to 10 questions total
  ],
  "maxPoints": 100,
  "pointsPerQuestion": 10
}
Response (429 Too Many Requests - Already completed today):
json{
  "error": {
    "code": "DAILY_LIMIT_REACHED",
    "message": "You've completed today's practice. Come back tomorrow!",
    "nextResetAt": "2026-02-08T00:00:00Z"
  }
}
Notes:

Backend randomly selects up to 10 questions from user's completed lessons
Questions are at mixed difficulty levels
Reset at midnight UTC (or user's timezone if supported)
If user has <10 completed lessons, returns fewer questions


8.8 Error Codes
All endpoints may return these standard errors:
400 Bad Request:
json{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: userId"
  }
}
404 Not Found:
json{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Lesson l99_invalid not found"
  }
}
500 Internal Server Error:
json{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Something went wrong. Please try again.",
    "retryable": true
  }
}
503 Service Unavailable:
json{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Video generation service is temporarily unavailable",
    "retryable": true,
    "retryAfter": 30
  }
}

9. Visual Design System
9.1 Color Palette
Primary (Brand):
css--color-teal-dark: #005555;    /* Pressed states, headers */
--color-teal-primary: #007373;  /* Buttons, active states, logo */
--color-teal-light: #5EEAD4;    /* Hover states, highlights */
--color-teal-pale: #E0F2F1;     /* Backgrounds, subtle accents */
Neutrals:
css--color-white: #FFFFFF;
--color-gray-50: #F9FAFB;
--color-gray-100: #F3F4F6;
--color-gray-300: #D1D5DB;
--color-gray-500: #6B7280;
--color-gray-700: #374151;
--color-gray-900: #1F2937;
Semantic:
css--color-success: #10B981;  /* Correct answers, completion */
--color-error: #EF4444;    /* Wrong answers, errors */
--color-warning: #F59E0B;  /* Streaks, alerts */
--color-info: #3B82F6;     /* Informational messages */
Usage:
css/* Buttons */
.btn-primary {
  background: var(--color-teal-primary);
  color: var(--color-white);
}

.btn-primary:hover {
  background: var(--color-teal-light);
}

.btn-primary:active {
  background: var(--color-teal-dark);
}

/* Correct/Wrong states */
.quiz-option.correct {
  border-color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.quiz-option.incorrect {
  border-color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
}

9.2 Typography
Font Family:
css@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
Type Scale:Continue13:27css/* Type Scale */
.text-xs {
  font-size: 12px;
  line-height: 16px;
}

.text-sm {
  font-size: 14px;
  line-height: 20px;
}

.text-base {
  font-size: 16px;
  line-height: 24px;
}

.text-lg {
  font-size: 18px;
  line-height: 28px;
}

.text-xl {
  font-size: 20px;
  line-height: 28px;
}

.text-2xl {
  font-size: 24px;
  line-height: 32px;
}

.text-3xl {
  font-size: 28px;
  line-height: 36px;
}

.text-4xl {
  font-size: 32px;
  line-height: 40px;
}
Font Weights:
css.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
Usage Examples:
css/* Page Titles */
h1 {
  font-size: 32px;
  font-weight: 700;
  line-height: 40px;
  color: var(--color-gray-900);
}

/* Section Headers */
h2 {
  font-size: 24px;
  font-weight: 600;
  line-height: 32px;
  color: var(--color-gray-900);
}

/* Card Titles */
h3 {
  font-size: 20px;
  font-weight: 600;
  line-height: 28px;
  color: var(--color-gray-900);
}

/* Body Text */
p {
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  color: var(--color-gray-700);
}

/* Small Text (captions, labels) */
.caption {
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  color: var(--color-gray-500);
}

/* Metadata (dates, counts) */
.metadata {
  font-size: 12px;
  font-weight: 400;
  line-height: 16px;
  color: var(--color-gray-500);
}

9.3 Spacing System
Tailwind-Compatible Scale (4px increments):
css--spacing-0: 0px;
--spacing-1: 4px;
--spacing-2: 8px;
--spacing-3: 12px;
--spacing-4: 16px;
--spacing-5: 20px;
--spacing-6: 24px;
--spacing-8: 32px;
--spacing-10: 40px;
--spacing-12: 48px;
--spacing-16: 64px;
--spacing-20: 80px;
Common Patterns:
css/* Card Padding */
.card {
  padding: var(--spacing-4); /* 16px */
}

/* Section Spacing */
.section-gap {
  margin-bottom: var(--spacing-6); /* 24px */
}

/* Button Padding */
.btn {
  padding: var(--spacing-3) var(--spacing-6); /* 12px 24px */
}

/* Stack Spacing (between elements) */
.stack > * + * {
  margin-top: var(--spacing-4); /* 16px */
}

9.4 Border Radius
css--radius-sm: 4px;    /* Small elements (badges, tags) */
--radius-md: 8px;    /* Buttons, inputs */
--radius-lg: 12px;   /* Cards */
--radius-xl: 16px;   /* Modals */
--radius-2xl: 24px;  /* Large containers */
--radius-full: 9999px; /* Pills, circles */
Usage:
css.btn {
  border-radius: var(--radius-md);
}

.card {
  border-radius: var(--radius-lg);
}

.modal {
  border-radius: var(--radius-xl);
}

.avatar {
  border-radius: var(--radius-full);
}

9.5 Shadows
css--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
Usage:
css/* Cards */
.card {
  box-shadow: var(--shadow-md);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}

/* Floating Elements (Adapt button) */
.floating-button {
  box-shadow: var(--shadow-xl);
}

/* Modals */
.modal {
  box-shadow: var(--shadow-xl);
}

9.6 Component Styles
Buttons
css/* Primary Button */
.btn-primary {
  background: var(--color-teal-primary);
  color: var(--color-white);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-teal-dark);
}

.btn-primary:active {
  transform: scale(0.95);
}

.btn-primary:disabled {
  background: var(--color-gray-300);
  color: var(--color-gray-500);
  cursor: not-allowed;
}

/* Secondary Button */
.btn-secondary {
  background: var(--color-white);
  color: var(--color-teal-primary);
  border: 2px solid var(--color-teal-primary);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--color-teal-pale);
}

/* Text Button */
.btn-text {
  background: transparent;
  color: var(--color-teal-primary);
  border: none;
  padding: 8px 16px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s ease;
}

.btn-text:hover {
  color: var(--color-teal-dark);
}
Cards
css.card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-gray-100);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-lg);
}

.card-interactive {
  cursor: pointer;
}

.card-interactive:active {
  transform: scale(0.98);
}
Inputs
css/* Text Input */
.input-text {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.input-text:focus {
  outline: none;
  border-color: var(--color-teal-primary);
  box-shadow: 0 0 0 3px var(--color-teal-pale);
}

/* Select Dropdown */
.input-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font-size: 16px;
  background: var(--color-white);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.input-select:focus {
  outline: none;
  border-color: var(--color-teal-primary);
  box-shadow: 0 0 0 3px var(--color-teal-pale);
}

/* Radio Button */
.input-radio {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-full);
  margin-right: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.input-radio:checked {
  border-color: var(--color-teal-primary);
  background: var(--color-teal-primary);
  box-shadow: inset 0 0 0 3px var(--color-white);
}

.input-radio:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-teal-pale);
}
Progress Bar
css.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-teal-primary);
  transition: width 0.3s ease;
}

/* Segmented Progress (17 lessons) */
.progress-segmented {
  display: flex;
  gap: 4px;
  width: 100%;
}

.progress-segment {
  flex: 1;
  height: 8px;
  background: var(--color-gray-200);
  border-radius: 2px;
}

.progress-segment.completed {
  background: var(--color-teal-primary);
}
Modal Overlay
css.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

9.7 Animations
Transitions (Keep Simple for Hackathon):
css/* Default Transition */
.transition-default {
  transition: all 0.2s ease;
}

/* Button Press */
.btn:active {
  transform: scale(0.95);
}

/* Card Hover */
.card-hover {
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Loading Spinner */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Pulse (Active Lesson Node) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
No Complex Animations:

No confetti (future enhancement)
No page transitions (future enhancement)
No count-up animations (future enhancement)
Focus on functional, fast, simple


9.8 Mobile-Specific Considerations
Safe Area Insets (iPhone Notch):
css/* Bottom Navigation with Safe Area */
.bottom-nav {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Top Bar with Safe Area */
.top-bar {
  padding-top: env(safe-area-inset-top);
}
Touch Targets:
css/* Minimum 48×48px for accessibility */
.btn, .link, .nav-item {
  min-width: 48px;
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
Prevent Text Selection (Video Player Controls):
css.video-controls {
  user-select: none;
  -webkit-user-select: none;
}
Prevent Pull-to-Refresh on Video:
css.lesson-player {
  overscroll-behavior-y: contain;
}

10. Technical Implementation Guide
10.1 Project Setup
Initialize Next.js Project:
bashnpx create-next-app@latest vina-frontend --typescript --tailwind --app
cd vina-frontend
Install Dependencies:
bash# Core dependencies
npm install uuid
npm install date-fns

# Development dependencies (optional)
npm install -D @types/uuid
Environment Variables:
bash# .env.local
NEXT_PUBLIC_API_URL=https://vina-api.railway.app/api/v1
NEXT_PUBLIC_CLOUDINARY_BASE_URL=https://res.cloudinary.com/vina
```

**Folder Structure:**
```
vina-frontend/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Welcome screen
│   ├── profession-select/
│   │   └── page.tsx
│   ├── pre-assessment/
│   │   └── page.tsx
│   ├── course-map/
│   │   └── page.tsx
│   ├── lesson/
│   │   └── [lessonId]/
│   │       └── page.tsx
│   ├── quiz/
│   │   ├── [lessonId]/
│   │   │   └── page.tsx
│   │   └── [lessonId]/results/
│   │       └── page.tsx
│   ├── practice/
│   │   └── page.tsx
│   └── progress/
│       └── page.tsx
├── components/
│   ├── Layout/
│   │   ├── TopBar.tsx
│   │   └── BottomNav.tsx
│   ├── Shared/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorMessage.tsx
│   ├── Quiz/
│   │   ├── QuizQuestion.tsx
│   │   └── QuizResults.tsx
│   └── Lesson/
│       ├── VideoPlayer.tsx
│       └── AdaptMenu.tsx
├── contexts/
│   ├── UserContext.tsx
│   ├── ProgressContext.tsx
│   └── LessonContext.tsx
├── lib/
│   ├── api.ts                  # API client functions
│   ├── storage.ts              # LocalStorage utilities
│   └── constants.ts            # Static data (professions, lessons)
├── public/
│   └── images/
│       └── vina-logo.png
├── styles/
│   └── globals.css             # Global styles, CSS variables
└── types/
    └── index.ts                # TypeScript interfaces

10.2 Core Implementation Patterns
API Client (lib/api.ts)
typescript// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  headers?: Record<string, string>;
}

async function apiCall<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;
  
  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  };
  
  if (body) {
    config.body = JSON.stringify(body);
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }
  
  return response.json();
}

// API Functions
export const api = {
  // Profile
  createProfile: (profession: string) =>
    apiCall('/profiles', {
      method: 'POST',
      body: { profession }
    }),
  
  // Pre-Assessment
  getPreAssessment: (profession: string) =>
    apiCall(`/assessment/pre-quiz?profession=${encodeURIComponent(profession)}`),
  
  submitPreAssessment: (userId: string, answers: any[]) =>
    apiCall('/assessment/submit', {
      method: 'POST',
      body: { userId, answers }
    }),
  
  // Lessons
  getLesson: (lessonId: string, userId: string, difficulty: number) =>
    apiCall(`/lessons/${lessonId}?userId=${userId}&difficulty=${difficulty}`),
  
  adaptLesson: (lessonId: string, userId: string, type: string, currentDifficulty: number) =>
    apiCall('/lessons/adapt', {
      method: 'POST',
      body: { lessonId, userId, adaptationType: type, currentDifficulty }
    }),
  
  // Quizzes
  getQuiz: (lessonId: string, userId: string) =>
    apiCall(`/quizzes/${lessonId}?userId=${userId}`),
  
  getCheckpointQuiz: (lessonId: string, userId: string) =>
    apiCall(`/quizzes/${lessonId}/checkpoint?userId=${userId}`),
  
  submitQuiz: (lessonId: string, userId: string, quizType: string, answers: any[]) =>
    apiCall('/quizzes/submit', {
      method: 'POST',
      body: { lessonId, userId, quizType, answers }
    }),
  
  // Practice
  getDailyPractice: (userId: string) =>
    apiCall(`/practice/daily?userId=${userId}`)
};
LocalStorage Utilities (lib/storage.ts)
typescript// lib/storage.ts
import { v4 as uuidv4 } from 'uuid';

const STORAGE_KEYS = {
  USER: 'vina_user',
  PROGRESS: 'vina_progress',
  SESSION: 'vina_session'
};

// User Storage
export const userStorage = {
  get: () => {
    const data = localStorage.getItem(STORAGE_KEYS.USER);
    return data ? JSON.parse(data) : null;
  },
  
  set: (user: any) => {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  },
  
  clear: () => {
    localStorage.removeItem(STORAGE_KEYS.USER);
  }
};

// Progress Storage
const DEFAULT_PROGRESS = {
  currentLessonId: 'l01_what_llms_are',
  completedLessons: [],
  lessonScores: {},
  currentDifficulty: 3,
  totalPoints: 0,
  streak: 0,
  lastActiveDate: new Date().toISOString().split('T')[0],
  practicePointsToday: 0,
  lastPracticeDate: '',
  totalLearningTimeSeconds: 0,
  preAssessmentCompleted: false,
  preAssessmentScore: 0,
  startingLesson: 'l01_what_llms_are',
  preAssessmentDate: ''
};

export const progressStorage = {
  get: () => {
    const data = localStorage.getItem(STORAGE_KEYS.PROGRESS);
    return data ? JSON.parse(data) : DEFAULT_PROGRESS;
  },
  
  set: (progress: any) => {
    localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(progress));
  },
  
  update: (updates: Partial<typeof DEFAULT_PROGRESS>) => {
    const current = progressStorage.get();
    const updated = { ...current, ...updates };
    progressStorage.set(updated);
    return updated;
  },
  
  clear: () => {
    localStorage.removeItem(STORAGE_KEYS.PROGRESS);
  }
};

// Session Storage
export const sessionStorage = {
  get: () => {
    const data = localStorage.getItem(STORAGE_KEYS.SESSION);
    return data ? JSON.parse(data) : { adaptationHistory: [] };
  },
  
  set: (session: any) => {
    localStorage.setItem(STORAGE_KEYS.SESSION, JSON.stringify(session));
  },
  
  clear: () => {
    localStorage.removeItem(STORAGE_KEYS.SESSION);
  }
};

// Helper Functions
export const generateUserId = () => uuidv4();

export const calculateStreak = (lastActiveDate: string): number => {
  const today = new Date().toISOString().split('T')[0];
  
  if (lastActiveDate === today) {
    // Already active today, return current streak
    return progressStorage.get().streak;
  }
  
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split('T')[0];
  
  if (lastActiveDate === yesterdayStr) {
    // Active yesterday, increment streak
    return progressStorage.get().streak + 1;
  }
  
  // Streak broken, reset to 1
  return 1;
};
Static Data (lib/constants.ts)
typescript// lib/constants.ts
export const PROFESSIONS = [
  'Clinical Researcher',
  'HR Manager',
  'Project Manager',
  'Marketing Manager'
];

export const ALL_LESSONS = [
  {
    lessonId: 'l01_what_llms_are',
    lessonNumber: 1,
    lessonName: 'What LLMs Are',
    shortTitle: 'What LLMs Are',
    topicGroup: 'The Foundations',
    estimatedDuration: 3,
    prerequisites: []
  },
  {
    lessonId: 'l02_tokens_context',
    lessonNumber: 2,
    lessonName: 'Tokens & Context Windows',
    shortTitle: 'Tokens & Context',
    topicGroup: 'The Foundations',
    estimatedDuration: 3,
    prerequisites: ['l01_what_llms_are']
  },
  {
    lessonId: 'l03_why_outputs_vary',
    lessonNumber: 3,
    lessonName: 'Why Outputs Vary',
    shortTitle: 'Why Outputs Vary',
    topicGroup: 'The Foundations',
    estimatedDuration: 3,
    prerequisites: ['l02_tokens_context']
  },
  {
    lessonId: 'l04_where_llms_excel',
    lessonNumber: 4,
    lessonName: 'Where LLMs Excel',
    shortTitle: 'Where LLMs Excel',
    topicGroup: 'Capabilities & Risks',
    estimatedDuration: 3,
    prerequisites: ['l03_why_outputs_vary']
  },
  {
    lessonId: 'l05_hallucinations',
    lessonNumber: 5,
    lessonName: 'Hallucinations',
    shortTitle: 'Hallucinations',
    topicGroup: 'Capabilities & Risks',
    estimatedDuration: 3,
    prerequisites: ['l04_where_llms_excel']
  },
  {
    lessonId: 'l06_bias_issues',
    lessonNumber: 6,
    lessonName: 'Bias Issues',
    shortTitle: 'Bias Issues',
    topicGroup: 'Capabilities & Risks',
    estimatedDuration: 3,
    prerequisites: ['l05_hallucinations']
  },
  {
    lessonId: 'l07_safe_use_guidelines',
    lessonNumber: 7,
    lessonName: 'Safe Use Guidelines',
    shortTitle: 'Safe Use Guidelines',
    topicGroup: 'Capabilities & Risks',
    estimatedDuration: 3,
    prerequisites: ['l06_bias_issues']
  },
  {
    lessonId: 'l08_identifying_roi_tasks',
    lessonNumber: 8,
    lessonName: 'Identifying ROI Tasks',
    shortTitle: 'ROI Tasks',
    topicGroup: 'Business Use Cases',
    estimatedDuration: 3,
    prerequisites: ['l07_safe_use_guidelines']
  },
  {
    lessonId: 'l09_good_fit_poor_fit',
    lessonNumber: 9,
    lessonName: 'Good Fit vs Poor Fit',
    shortTitle: 'Good vs Poor Fit',
    topicGroup: 'Business Use Cases',
    estimatedDuration: 3,
    prerequisites: ['l08_identifying_roi_tasks']
  },
  {
    lessonId: 'l10_designing_workflows',
    lessonNumber: 10,
    lessonName: 'Designing Workflows',
    shortTitle: 'Workflows',
    topicGroup: 'Business Use Cases',
    estimatedDuration: 3,
    prerequisites: ['l09_good_fit_poor_fit']
  },
  {
    lessonId: 'l11_cloud_apis',
    lessonNumber: 11,
    lessonName: 'Cloud APIs',
    shortTitle: 'Cloud APIs',
    topicGroup: 'LLM Landscape',
    estimatedDuration: 3,
    prerequisites: ['l10_designing_workflows']
  },
  {
    lessonId: 'l12_self_hosted_models',
    lessonNumber: 12,
    lessonName: 'Self-Hosted Models',
    shortTitle: 'Self-Hosted',
    topicGroup: 'LLM Landscape',
    estimatedDuration: 3,
    prerequisites: ['l11_cloud_apis']
  },
  {
    lessonId: 'l13_choosing_your_setup',
    lessonNumber: 13,
    lessonName: 'Choosing Your Setup',
    shortTitle: 'Choose Setup',
    topicGroup: 'LLM Landscape',
    estimatedDuration: 3,
    prerequisites: ['l12_self_hosted_models']
  },
  {
    lessonId: 'l14_prompt_anatomy',
    lessonNumber: 14,
    lessonName: 'Prompt Anatomy',
    shortTitle: 'Prompt Anatomy',
    topicGroup: 'Prompting Skills',
    estimatedDuration: 3,
    prerequisites: ['l13_choosing_your_setup']
  },
  {
    lessonId: 'l15_few_shot_prompting',
    lessonNumber: 15,
    lessonName: 'Few-Shot Prompting',
    shortTitle: 'Few-Shot',
    topicGroup: 'Prompting Skills',
    estimatedDuration: 3,
    prerequisites: ['l14_prompt_anatomy']
  },
  {
    lessonId: 'l16_iteration_evaluation',
    lessonNumber: 16,
    lessonName: 'Iteration & Evaluation',
    shortTitle: 'Iteration',
    topicGroup: 'Prompting Skills',
    estimatedDuration: 3,
    prerequisites: ['l15_few_shot_prompting']
  },
  {
    lessonId: 'l17_prompting_for_your_role',
    lessonNumber: 17,
    lessonName: 'Prompting for Your Role',
    shortTitle: 'Your Role',
    topicGroup: 'Prompting Skills',
    estimatedDuration: 3,
    prerequisites: ['l16_iteration_evaluation']
  }
];

export const getNextLesson = (completedLessons: string[], startingLesson: string): string | null => {
  const progress = progressStorage.get();
  
  // If no lessons completed, return starting lesson from pre-assessment
  if (completedLessons.length === 0) {
    return startingLesson;
  }
  
  // Find first lesson that's not completed and has all prerequisites met
  for (const lesson of ALL_LESSONS) {
    if (completedLessons.includes(lesson.lessonId)) continue;
    
    const prerequisitesMet = lesson.prerequisites.every(prereq =>
      completedLessons.includes(prereq)
    );
    
    if (prerequisitesMet) {
      return lesson.lessonId;
    }
  }
  
  return null; // All lessons completed
};

export const getLessonState = (
  lessonId: string,
  completedLessons: string[],
  startingLesson: string
): 'completed' | 'active' | 'locked' => {
  if (completedLessons.includes(lessonId)) return 'completed';
  
  const lesson = ALL_LESSONS.find(l => l.lessonId === lessonId);
  if (!lesson) return 'locked';
  
  // Check if this is the next available lesson
  const nextLesson = getNextLesson(completedLessons, startingLesson);
  if (lessonId === nextLesson) return 'active';
  
  return 'locked';
};

10.3 Key Implementation Examples
Video Player Component
typescript// components/Lesson/VideoPlayer.tsx
'use client';

import { useRef, useState, useEffect } from 'react';

interface VideoPlayerProps {
  videoUrl: string;
  captionsUrl?: string;
  onEnded: () => void;
  onAdaptClick: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoUrl,
  captionsUrl,
  onEnded,
  onAdaptClick
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  
  const speeds = [1, 1.25, 1.5];
  
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    
    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleDurationChange = () => setDuration(video.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      onEnded();
    };
    
    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('ended', handleEnded);
    
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('ended', handleEnded);
    };
  }, [onEnded]);
  
  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;
    
    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };
  
  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;
    
    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };
  
  const cycleSpeed = () => {
    const currentIndex = speeds.indexOf(speed);
    const nextSpeed = speeds[(currentIndex + 1) % speeds.length];
    
    const video = videoRef.current;
    if (video) {
      video.playbackRate = nextSpeed;
    }
    
    setSpeed(nextSpeed);
  };
  
  const handleReplay = () => {
    const video = videoRef.current;
    if (!video) return;
    
    video.currentTime = 0;
    video.play();
    setIsPlaying(true);
  };
  
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  
  return (
    <div className="relative w-full h-screen bg-black">
      {/* Video */}
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full object-contain"
        playsInline
        preload="auto"
        onClick={togglePlay}
      >
        {captionsUrl && (
          <track
            kind="captions"
            src={captionsUrl}
            srcLang="en"
            label="English"
            default
          />
        )}
      </video>
      
      {/* Adapt Button (Always Visible) */}
      <button
        onClick={onAdaptClick}
        className="fixed right-4 top-1/2 -translate-y-1/2 z-50
                   bg-teal-600 text-white px-4 py-3 rounded-full
                   shadow-lg hover:bg-teal-700 active:scale-95
                   transition-all duration-200 flex flex-col items-center gap-1"
      >
        <span className="text-2xl">⚡</span>
        <span className="text-sm font-semibold">Adapt</span>
      </button>
      
      {/* Progress Bar */}
      <div className="absolute bottom-16 left-0 right-0 px-4">
        <div className="flex items-center gap-2 text-white">
          <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-teal-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-sm font-medium w-12 text-right">
            {Math.round(progress)}%
          </span>
        </div>
      </div>
      
      {/* Controls */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        <div className="flex items-center justify-between text-white">
          <button
            onClick={togglePlay}
            className="p-3 hover:bg-white/20 rounded-lg transition"
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            <span className="text-2xl">{isPlaying ? '⏸' : '▶'}</span>
          </button>
          
          <button
            onClick={toggleMute}
            className="p-3 hover:bg-white/20 rounded-lg transition"
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            <span className="text-2xl">{isMuted ? '🔇' : '🔊'}</span>
          </button>
          
          <button
            onClick={cycleSpeed}
            className="p-3 hover:bg-white/20 rounded-lg transition font-semibold"
            aria-label={`Speed: ${speed}x`}
          >
            {speed}x
          </button>
          
          <button
            onClick={handleReplay}
            className="p-3 hover:bg-white/20 rounded-lg transition"
            aria-label="Replay from start"
          >
            <span className="text-2xl">↻</span>
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

### **10.4 Routing & Navigation**

**App Router Structure:**
```
app/
├── layout.tsx                    # Root layout with providers
├── page.tsx                      # / (Welcome)
├── profession-select/
│   └── page.tsx                  # /profession-select
├── pre-assessment/
│   └── page.tsx                  # /pre-assessment
├── course-map/
│   └── page.tsx                  # /course-map (Home)
├── lesson/
│   └── [lessonId]/
│       └── page.tsx              # /lesson/l05_hallucinations
├── quiz/
│   └── [lessonId]/
│       ├── page.tsx              # /quiz/l05_hallucinations
│       └── results/
│           └── page.tsx          # /quiz/l05_hallucinations/results
├── practice/
│   └── page.tsx                  # /practice
└── progress/
    └── page.tsx                  # /progress
Root Layout with Providers:
typescript// app/layout.tsx
import { UserProvider } from '@/contexts/UserContext';
import { ProgressProvider } from '@/contexts/ProgressContext';
import '@/styles/globals.css';

export const metadata = {
  title: 'Vina - Personalized LLM Learning',
  description: 'Learn LLMs your way with adaptive video lessons',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  themeColor: '#007373'
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <UserProvider>
          <ProgressProvider>
            {children}
          </ProgressProvider>
        </UserProvider>
      </body>
    </html>
  );
}
Navigation Pattern:
typescript// Use Next.js Link for navigation
import Link from 'next/link';

// Or useRouter for programmatic navigation
import { useRouter } from 'next/navigation';

const MyComponent = () => {
  const router = useRouter();
  
  const handleComplete = () => {
    // Update state
    progressContext.markLessonComplete('l05', 3);
    
    // Navigate
    router.push('/course-map');
  };
  
  return <button onClick={handleComplete}>Complete</button>;
};

11. Testing & Validation
11.1 Manual Testing Checklist
Pre-Launch Testing:
Onboarding Flow:

 Welcome screen displays logo and CTA
 Profession dropdown shows all 4 options
 Cannot continue without selecting profession
 Profile creation succeeds
 LocalStorage saves user data
 Pre-assessment questions load (10 total)
 Selecting answer auto-advances after 0.5s
 Skip button works at any time
 2 wrong in a row ends quiz early
 Backend placement logic works (correct starting lesson)
 Navigate to Course Map after completion

Course Map:

 Shows all 17 lessons in order
 Starting lesson is unlocked (active state)
 All other lessons locked (gray)
 Completed lessons show checkmark
 Progress bar accurate (X/17)
 Top bar shows streak & points
 Tapping active lesson navigates to player
 Tapping locked lesson does nothing
 Bottom nav highlights Home tab

Lesson Player:

 Video loads and plays
 Play/Pause works
 Mute works
 Speed control cycles (1x → 1.25x → 1.5x → 1x)
 Replay button restarts video
 Progress bar updates in real-time
 Adapt button always visible
 Captions display (if available)
 Video ending triggers quiz

Adapt Menu:

 Overlay appears on Adapt click
 Video pauses when menu opens
 All 4 options visible
 "Simplify this" regenerates at difficulty 1
 "Get to the point" regenerates at difficulty 5
 "I know this already" opens checkpoint quiz
 "More examples" loads examples video
 Cancel closes menu and resumes video
 Tap outside closes menu

Loading States:

 Spinner shows during video generation
 Fun facts rotate every 3 seconds
 Timeout after 2 minutes shows error
 Retry button works
 Go Back button works

Checkpoint Quiz:

 Quiz loads 3 questions
 Answering works (same as lesson quiz)
 Pass (2/3) shows success modal
 Pass marks lesson complete
 Pass navigates to next lesson
 Fail (0-1/3) shows encouragement modal
 Fail resumes video at same position

Lesson Quiz:

 3 questions load
 Selecting answer highlights option
 Instant feedback (green/red border)
 Explanation displays
 No retry (single attempt per question)
 Next button appears after 1s
 After 3 questions → Results screen

Quiz Results:

 Pass (2/3 or 3/3) shows celebration
 Points awarded correctly (30 for 3/3, 20 for 2/3)
 Streak updates
 Next lesson unlocks
 Fail (0-1/3) shows encouragement
 "Continue Learning" navigates to Course Map
 "Review Lesson" replays lesson
 "Re-watch Lesson" replays at same difficulty
 "Try Simpler Version" lowers difficulty

Let's Practice:

 Tab shows locked if no completed lessons
 Tab shows "Start Practice" if available
 Daily challenge loads up to 10 questions
 Questions are from completed lessons
 Scoring works (10 pts per correct)
 Completion shows score summary
 Countdown timer to next reset
 Already completed shows "Completed Today"
 Badge appears on tab when available

Progress Tab:

 Overall progress bar accurate
 Stats display (streak, points, time, completed)
 Recent activity shows last 5 lessons
 Daily practice summary shows
 Tapping completed lesson opens review mode

Bottom Navigation:

 All 3 tabs visible
 Active tab highlighted
 Tapping switches tabs
 Badge appears on Practice when available

Top Bar:

 Streak counter accurate
 Points counter accurate
 Profile avatar shows initials

Persistence:

 Refresh page preserves progress
 Close/reopen browser preserves data
 Clear LocalStorage resets to welcome


11.2 Device Testing Matrix
DeviceBrowserScreen SizePriorityStatusiPhone 14 ProSafari 17390×844P1⬜iPhone SESafari 17375×667P2⬜Samsung S23Chrome 120360×800P1⬜iPad ProSafari 171024×1366P3⬜DesktopChrome 1201920×1080P2⬜DesktopSafari 171920×1080P3⬜
Test Scenarios:

Portrait Only: App forces portrait orientation on mobile
Landscape: App shows "Please rotate to portrait" message
Small Screens: All content readable, buttons tappable (48×48px min)
Desktop: Mobile container centered, max-width 430px


11.3 Error Scenarios
ScenarioExpected BehaviorStatusNo internet on load"No connection" message + Retry⬜API returns 500Error message + Retry button⬜Video generation fails"Couldn't generate" + Retry/Skip⬜Video URL 404Error message + Go Back⬜Quiz fetch failsError message + Retry⬜LocalStorage fullGraceful degradation (warn user)⬜Invalid professionValidation prevents submission⬜Mid-quiz refreshQuiz restarts (progress not saved)⬜

11.4 Performance Benchmarks
MetricTargetCriticalStatusInitial Page Load (Welcome)<2s<4s⬜Course Map Load<1.5s<3s⬜Video Start Time<1s<3s⬜Quiz Submit → Feedback<500ms<1s⬜Adapt Request → Response<15s<30s⬜LocalStorage Read/Write<50ms<200ms⬜
Tools:

Chrome DevTools (Lighthouse)
Network throttling (Slow 3G simulation)
Performance profiler


12. Deployment Strategy
12.1 Vercel Deployment
Prerequisites:

GitHub repository created
Vercel account connected to GitHub

Deployment Steps:
1. Push to GitHub:
bashgit init
git add .
git commit -m "Initial commit - Vina frontend MVP"
git branch -M main
git remote add origin https://github.com/your-username/vina-frontend.git
git push -u origin main
2. Deploy to Vercel:
bash# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set project name: vina-frontend
# - Framework: Next.js
# - Root directory: ./
# - Build command: npm run build
# - Output directory: .next
```

**3. Set Environment Variables in Vercel Dashboard:**
```
Production:
NEXT_PUBLIC_API_URL=https://vina-api.railway.app/api/v1
NEXT_PUBLIC_CLOUDINARY_BASE_URL=https://res.cloudinary.com/vina

Preview (optional):
NEXT_PUBLIC_API_URL=https://vina-api-staging.railway.app/api/v1
4. Configure Custom Domain (Optional):

Vercel Dashboard → Settings → Domains
Add: vina.app or vina.vercel.app

5. Enable Analytics (Optional):

Vercel Dashboard → Analytics
Track page views, performance


12.2 Production Checklist
Before Going Live:
Code Quality:

 No console.log statements (or wrapped in DEV check)
 No hardcoded API keys
 All environment variables in .env.local (gitignored)
 TypeScript errors resolved
 ESLint warnings addressed

Performance:

 Images optimized (WebP, correct sizes)
 Lighthouse score >90 (Performance)
 First Contentful Paint <2s
 Largest Contentful Paint <2.5s

SEO:

 Meta tags present (title, description)
 Open Graph tags (og:title, og:image)
 Favicon added
 robots.txt configured

Accessibility:

 WCAG AA color contrast
 All images have alt text
 Keyboard navigation works
 Screen reader tested (VoiceOver/NVDA)

Security:

 No sensitive data in LocalStorage
 HTTPS enforced
 CSP headers configured (optional)

Analytics:

 Vercel Analytics enabled
 Error tracking (Sentry optional)
 Conversion tracking (quiz completion, lesson completion)


12.3 Post-Deployment Monitoring
Metrics to Track:
User Engagement:

Total users (unique visitors)
Completion rate (% who complete L01)
Retention (return visitors)
Average lessons completed per user

Technical:

API error rate
Video load failures
Average video generation time
LocalStorage usage patterns

Performance:

Page load times (P50, P95)
API response times
Video start time

Tools:

Vercel Analytics (built-in)
PostHog (optional, open-source analytics)
Sentry (optional, error tracking)


13. Future Enhancements
13.1 Post-Hackathon Roadmap
Phase 1: Foundation (Week 1-2)

 Add authentication (email/Google OAuth)
 User accounts (persistent across devices)
 Industry + Experience selection
 Profile editing
 Enhanced error handling (retry logic, offline mode)

Phase 2: Engagement (Week 3-4)

 Pre-assessment quiz at onboarding
 Multi-course support (Skills Portfolio)
 Certificates on course completion
 Email notifications (streak reminders, new courses)
 Social sharing (LinkedIn, Twitter)

Phase 3: Gamification (Week 5-6)

 Leaderboard (compete with peers)
 Achievements/Badges system
 XP levels (Bronze, Silver, Gold, Platinum)
 Point redemption (unlock bonus content)
 Streak recovery (freeze streak once per month)

Phase 4: Advanced Features (Week 7-8)

 PWA installation prompt
 Offline mode (download lessons)
 Advanced animations (confetti, transitions)
 Learning time insights (weekly reports)
 Personalized recommendations ("Try this next")
 Community features (comments, discussions)

Phase 5: Enterprise (Month 3+)

 Team dashboards (manager view of team progress)
 Custom courses (company-specific content)
 SSO integration (Okta, Azure AD)
 Usage analytics (company-wide insights)
 White-label options (custom branding)


13.2 Known Limitations (Hackathon Scope)
Intentionally Excluded:

❌ No authentication (LocalStorage only)
❌ No backend sync (progress not backed up)
❌ No multi-device sync
❌ No password reset flow
❌ No email verification
❌ No social login
❌ No profile pictures (just initials)
❌ No collaborative features
❌ No comments/discussions
❌ No admin dashboard
❌ No content management system
❌ No A/B testing
❌ No advanced analytics
❌ No video scrubbing (intentional for engagement)
❌ No custom subtitles upload
❌ No video download

Technical Debt:

No comprehensive test suite (rely on manual testing)
No CI/CD pipeline (manual deploys)
No staging environment (use Vercel preview)
No database (pure client-side)
No real-time features (websockets)


13.3 Scalability Considerations
When to Add Backend Sync:



1000 active users


Users request cross-device sync
Need to analyze aggregate progress data

When to Add Authentication:

Enterprise customers require SSO
Need to prevent LocalStorage data loss
Want to enable community features

When to Add Database:

Need to track user behavior at scale
Want to run analytics queries
Compliance requires data audit trails

When to Add CDN:

Video delivery latency >3s in certain regions
Global user base (Asia-Pacific, Europe)
Bandwidth costs exceed $100/month


14. Final Summary
14.1 What You're Building
A mobile-first, adaptive video learning platform that:

Personalizes LLM education for 4 professions
Adapts content in real-time (4 adaptation types)
Places users at the right level (pre-assessment)
Gamifies learning (streaks, points, daily practice)
Works offline (LocalStorage persistence)
Deploys to Vercel in minutes

Total Development Time: 3 days (with 2 developers)
Estimated Effort:

Day 1: Setup + Onboarding + Course Map (8 hours)
Day 2: Lesson Player + Quiz + Adaptation (10 hours)
Day 3: Practice Tab + Progress Tab + Polish + Deploy (8 hours)

Total: 26 hours (13 hours per developer)

14.2 Success Criteria
Hackathon Demo:
✅ Show onboarding flow (30 seconds)
✅ Complete pre-assessment (1 minute)
✅ Watch lesson, adapt it (2 minutes)
✅ Pass quiz, unlock next lesson (1 minute)
✅ Show progress tracking (30 seconds)
✅ Demo daily practice (1 minute)
Total Demo: 6 minutes
Key Talking Points:

Adaptive AI: Content changes based on user feedback (live demo)
Smart Placement: Pre-assessment avoids forcing beginners through L01-L04
Gamification: Streaks + points drive engagement
Mobile-First: Native app-like experience (smooth, fast)
Profession-Specific: Clinical Researcher examples vs HR Manager examples


14.3 Delivery Checklist
Code Repository:

 GitHub repo public/accessible
 README with setup instructions
 .env.example file
 Clean commit history

Live Demo:

 Deployed to Vercel
 Custom domain (optional)
 All features working
 Test user created (demo account)

Documentation:

 This PRD (PDF export)
 API endpoint docs (for backend team)
 Component library (Storybook optional)
 Video walkthrough (2-3 minutes)

Presentation:

 Slide deck (10-15 slides)
 Demo script (6 minutes)
 Backup video (if live demo fails)
 Q&A prep (common questions)


14.4 Contact & Support
For Questions:

Frontend Issues: GitHub Issues
Backend Integration: API docs (Section 8)
Design Feedback: Figma file (if created)

Demo Day:

Arrive 30 min early
Test internet connection
Have backup video ready
Bring charged devices


APPENDIX A: API Endpoint Quick Reference
EndpointMethodPurpose/profilesPOSTCreate user profile/assessment/pre-quizGETGet 10 placement questions/assessment/submitPOSTSubmit answers, get starting lesson/lessons/{id}GETGet video URL at difficulty/lessons/adaptPOSTRequest adapted video/quizzes/{id}GETGet 3 lesson quiz questions/quizzes/{id}/checkpointGETGet 3 checkpoint quiz questions/quizzes/submitPOSTSubmit answers, get score/practice/dailyGETGet up to 10 daily practice questions

APPENDIX B: LocalStorage Keys
KeyDataPurposevina_userUser profile (profession, userId)Identityvina_progressLearning progress (completed, points, streak)Statevina_sessionCurrent video position, adaptation historySession

APPENDIX C: Color Hex Codes
ColorHexUsageBrand Teal#007373Primary buttons, active states, logoTeal Dark#005555Pressed states, headersTeal Light#5EEAD4Hover states, highlightsSuccess Green#10B981Correct answers, completionError Red#EF4444Wrong answers, errorsWarning Orange#F59E0BStreaks, alerts

APPENDIX D: Font Sizes
NameSizeUsagetext-xs12pxMetadata, tiny labelstext-sm14pxCaptions, secondary texttext-base16pxBody text, paragraphstext-lg18pxQuiz questions, emphasistext-xl20pxCard titlestext-2xl24pxSection headerstext-3xl28pxQuiz resultstext-4xl32pxPage titles

END OF DOCUMENT