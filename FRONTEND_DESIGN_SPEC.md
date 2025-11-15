# Men's Health App - Frontend Design Specification

## 🎨 Design Philosophy

### Core Principles
- **Masculine & Professional** - Strong, confident design without being overly aggressive
- **Clean & Minimalist** - Focus on content, remove clutter
- **Motivational** - Inspire action and progress
- **Trust-Building** - Medical-grade professionalism for health advice
- **Mobile-First** - Optimized for on-the-go fitness tracking

---

## 🎯 Target Audience

**Primary Users:**
- Men aged 25-45
- Fitness enthusiasts (beginner to advanced)
- Health-conscious professionals
- Busy individuals seeking guidance

**User Goals:**
- Get quick, actionable health/fitness advice
- Track conversations and progress
- Access personalized recommendations
- Build consistent habits

---

## 🎨 Visual Design System

### Color Palette

**Primary Colors:**
```
Deep Navy Blue: #1a2332 (Main background, headers)
Electric Blue: #2563eb (Primary CTA, links, active states)
Slate Gray: #64748b (Secondary text, borders)
```

**Accent Colors:**
```
Success Green: #10b981 (Achievements, positive metrics)
Warning Orange: #f59e0b (Alerts, important notices)
Error Red: #ef4444 (Warnings, errors)
```

**Neutrals:**
```
Pure White: #ffffff (Cards, input backgrounds)
Light Gray: #f8fafc (Page background)
Dark Gray: #0f172a (Primary text)
Medium Gray: #94a3b8 (Secondary text)
```

**Gradient Accents:**
```
Hero Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Card Hover: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)
```

### Typography

**Font Families:**
```css
/* Headings */
font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
font-weight: 700 (Bold), 600 (Semibold);

/* Body Text */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
font-weight: 400 (Regular), 500 (Medium);

/* Code/Metrics */
font-family: 'JetBrains Mono', 'Courier New', monospace;
```

**Type Scale:**
```
H1 (Hero): 48px / 56px, font-weight: 700
H2 (Section): 36px / 44px, font-weight: 600
H3 (Card Title): 24px / 32px, font-weight: 600
H4 (Subsection): 20px / 28px, font-weight: 600
Body Large: 18px / 28px, font-weight: 400
Body: 16px / 24px, font-weight: 400
Body Small: 14px / 20px, font-weight: 400
Caption: 12px / 16px, font-weight: 500
```

### Spacing System
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
3xl: 64px
```

### Border Radius
```
Small (Buttons, Tags): 6px
Medium (Cards, Inputs): 12px
Large (Modal, Panels): 16px
Full (Avatar, Pills): 9999px
```

### Shadows
```css
/* Cards */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);

/* Cards Hover */
box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);

/* Modal */
box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);

/* Floating Button */
box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
```

---

## 📱 Screen Layouts

### 1. **Authentication Screens**

#### Sign Up / Sign In
```
┌─────────────────────────────┐
│                             │
│      [LOGO]                 │
│   Men's Health AI           │
│                             │
│  ┌─────────────────────┐   │
│  │ Email               │   │
│  └─────────────────────┘   │
│                             │
│  ┌─────────────────────┐   │
│  │ Password            │   │
│  └─────────────────────┘   │
│                             │
│  [Sign In - Blue Button]    │
│                             │
│  Don't have account? Sign Up│
│                             │
└─────────────────────────────┘
```

**Design Notes:**
- Clean, centered layout
- Large touch-friendly inputs (min height: 48px)
- Strong CTA button with gradient
- Subtle background pattern/gradient
- Social login optional (Google, Apple)

---

#### Email Verification
```
┌─────────────────────────────┐
│                             │
│    [Mail Icon - Large]      │
│                             │
│   Check Your Email          │
│                             │
│  We sent a code to          │
│  walter@example.com         │
│                             │
│  ┌───┬───┬───┬───┬───┬───┐ │
│  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ │
│  └───┴───┴───┴───┴───┴───┘ │
│                             │
│  [Verify - Blue Button]     │
│                             │
│  Didn't receive? Resend     │
│                             │
└─────────────────────────────┘
```

**Design Notes:**
- Large 6-digit code input boxes
- Auto-focus and auto-advance
- Clear resend option
- Email address visible for confirmation

---

### 2. **Home/Dashboard Screen**

```
┌─────────────────────────────────────┐
│ ☰  Men's Health     [Avatar] [🔔]  │
├─────────────────────────────────────┤
│                                     │
│  Hi Walter! 👋                      │
│  Ready for today's workout?         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🏃 Today's Activity          │   │
│  │ ────────────────             │   │
│  │ Steps: 5,234 / 10,000       │   │
│  │ Calories: 342 / 2,500       │   │
│  └─────────────────────────────┘   │
│                                     │
│  Quick Actions                      │
│  ┌───────┐ ┌───────┐ ┌───────┐    │
│  │ 💬    │ │ 🏋️    │ │ 🥗    │    │
│  │ Chat  │ │Workout│ │ Meal  │    │
│  └───────┘ └───────┘ └───────┘    │
│                                     │
│  Recent Conversations               │
│  ┌─────────────────────────────┐   │
│  │ Muscle Building Tips        │   │
│  │ 2 hours ago            →    │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Nutrition Plan              │   │
│  │ Yesterday              →    │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Notes:**
- Personal greeting with user's name
- Dashboard cards with metrics
- Large, tappable quick action buttons
- Recent conversations list
- Bottom navigation bar (on mobile)

---

### 3. **Chat Screen** (Main Feature)

```
┌─────────────────────────────────────┐
│ ← Chat Assistant          [⋮]       │
├─────────────────────────────────────┤
│                                     │
│     ┌─────────────────────┐         │
│     │ Hello! How can I    │         │
│     │ help with your      │ [BOT]   │
│     │ fitness today?      │         │
│     └─────────────────────┘         │
│                 10:30 AM            │
│                                     │
│  [USER]  ┌─────────────────────┐   │
│          │ I want to build     │   │
│          │ muscle mass         │   │
│          └─────────────────────┘   │
│                 10:31 AM            │
│                                     │
│     ┌─────────────────────┐         │
│     │ Great goal! Let's   │         │
│     │ start with...       │ [BOT]   │
│     │                     │         │
│     │ [View Full Plan →]  │         │
│     └─────────────────────┘         │
│                 10:31 AM            │
│                                     │
│  [Typing...]                        │
│                                     │
├─────────────────────────────────────┤
│ [+] Type your message...      [↑]  │
└─────────────────────────────────────┘
```

**Design Notes:**
- WhatsApp/iMessage style chat bubbles
- User messages: Right-aligned, blue gradient
- Bot messages: Left-aligned, white/light gray
- Timestamps subtle and small
- Typing indicator with animation
- Fixed input bar at bottom
- Smooth scroll animation
- Message status indicators (sending, sent, error)

**Chat Bubble Styles:**
```css
/* User Message */
background: linear-gradient(135deg, #2563eb, #1d4ed8);
color: white;
border-radius: 18px 18px 4px 18px;
max-width: 70%;

/* Bot Message */
background: #f1f5f9;
color: #0f172a;
border-radius: 18px 18px 18px 4px;
max-width: 80%;
```

---

### 4. **Sessions/History Screen**

```
┌─────────────────────────────────────┐
│ ← Conversations         [Search 🔍] │
├─────────────────────────────────────┤
│                                     │
│  Today                              │
│  ┌─────────────────────────────┐   │
│  │ 💪 Muscle Building Tips      │   │
│  │ What exercises should I...   │   │
│  │ 2:30 PM              [···]   │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🥗 Nutrition for Gains       │   │
│  │ I need a high protein...     │   │
│  │ 10:15 AM             [···]   │   │
│  └─────────────────────────────┘   │
│                                     │
│  Yesterday                          │
│  ┌─────────────────────────────┐   │
│  │ 🏃 Cardio Routine            │   │
│  │ Best cardio for fat...       │   │
│  │ Yesterday 3PM        [···]   │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Start New Chat +]                 │
│                                     │
└─────────────────────────────────────┘
```

**Design Notes:**
- Grouped by date (Today, Yesterday, This Week, etc.)
- Session cards with emoji icons
- Preview of first message
- Swipe actions: Delete, Archive
- Floating "New Chat" button
- Search functionality

---

### 5. **Profile Screen**

```
┌─────────────────────────────────────┐
│ ← Profile                  [Edit]   │
├─────────────────────────────────────┤
│                                     │
│          [Avatar Photo]             │
│         Walter Banda                │
│      walterbanda98@gmail.com        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📊 Health Stats              │   │
│  │                              │   │
│  │ Age: 30 | Height: 6'0"       │   │
│  │ Weight: 180 lbs              │   │
│  │ Fitness Level: Intermediate  │   │
│  └─────────────────────────────┘   │
│                                     │
│  Goals                              │
│  [Muscle Gain] [Weight Loss]        │
│  [Endurance]                        │
│                                     │
│  Settings                           │
│  Notifications               [→]    │
│  Privacy & Security          [→]    │
│  Help & Support              [→]    │
│  About                       [→]    │
│                                     │
│  [Sign Out]                         │
│                                     │
└─────────────────────────────────────┘
```

**Design Notes:**
- Large avatar with edit option
- Stats card with key metrics
- Tag-based goals display
- List-style settings menu
- Prominent sign out button

---

## 🎭 Component Design Specs

### Buttons

**Primary Button (CTA)**
```css
background: linear-gradient(135deg, #2563eb, #1d4ed8);
color: white;
padding: 14px 24px;
border-radius: 12px;
font-weight: 600;
font-size: 16px;
box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
transition: transform 0.2s, box-shadow 0.2s;

/* Hover/Press */
transform: translateY(-2px);
box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
```

**Secondary Button**
```css
background: white;
color: #2563eb;
border: 2px solid #2563eb;
padding: 14px 24px;
border-radius: 12px;
font-weight: 600;
```

**Icon Button**
```css
background: #f1f5f9;
width: 48px;
height: 48px;
border-radius: 12px;
display: flex;
align-items: center;
justify-content: center;
```

---

### Input Fields

```css
background: white;
border: 2px solid #e2e8f0;
border-radius: 12px;
padding: 14px 16px;
font-size: 16px;
transition: border-color 0.2s;

/* Focus */
border-color: #2563eb;
box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);

/* Error */
border-color: #ef4444;
box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
```

---

### Cards

```css
background: white;
border-radius: 16px;
padding: 20px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
transition: box-shadow 0.3s, transform 0.3s;

/* Hover */
box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
transform: translateY(-2px);
```

---

### Navigation

**Bottom Navigation (Mobile)**
```
┌─────────────────────────────────────┐
│ [🏠]    [💬]    [📊]    [👤]       │
│ Home    Chat   Stats  Profile       │
└─────────────────────────────────────┘
```

**Design:**
- Fixed at bottom
- 4 main sections
- Active state: Blue color + indicator line
- Icons + labels
- Safe area padding for iOS

---

## 🎬 Animations & Interactions

### Micro-interactions

**Button Press:**
```
Scale down: 0.95
Duration: 100ms
Easing: ease-out
```

**Chat Message Appear:**
```
Fade in + Slide up
Duration: 300ms
Easing: cubic-bezier(0.4, 0, 0.2, 1)
```

**Typing Indicator:**
```
3 dots bouncing
Animation delay: 150ms each
Loop infinitely
```

**Card Hover:**
```
Translate Y: -4px
Shadow increase
Duration: 200ms
```

### Page Transitions

```
Slide Right (Back): 300ms
Slide Left (Forward): 300ms
Fade (Modal): 200ms
```

---

## 📐 Layout Specifications

### Mobile (320px - 768px)
- Single column layout
- Full-width cards
- Bottom navigation
- Hamburger menu for secondary nav
- 16px page margins

### Tablet (769px - 1024px)
- Two-column layout where appropriate
- Side navigation visible
- Larger cards with more breathing room
- 24px page margins

### Desktop (1025px+)
- Three-column layout (sidebar, main, detail)
- Persistent navigation
- Chat in center column
- Sessions list in left sidebar
- 32px page margins
- Max-width: 1440px (centered)

---

## 🌟 Key Features to Highlight

### 1. **Real-time Chat Experience**
- Instant message delivery
- Typing indicators
- Message status (sending, sent, delivered)
- Smooth scrolling
- Auto-scroll to latest message

### 2. **Personalization**
- User's name throughout the app
- Contextual recommendations based on profile
- Progress tracking
- Achievement badges

### 3. **Accessibility**
- Minimum touch target: 44x44px
- High contrast text (WCAG AA)
- Screen reader support
- Keyboard navigation
- Focus indicators

### 4. **Performance**
- Skeleton loaders for content
- Optimistic UI updates
- Image lazy loading
- Smooth 60fps animations

---

## 🎨 UI States

### Loading States
```
┌─────────────────────────────┐
│ ▓▓▓▓▓▓░░░░░░░░░░░░░         │ (Shimmer)
│ ▓▓▓░░░░░░░░░░               │
│ ▓▓▓▓▓▓▓░░░░░░░░░            │
└─────────────────────────────┘
```

### Empty States
```
┌─────────────────────────────┐
│         [Icon]              │
│    No conversations yet     │
│  Start chatting to get      │
│  personalized advice        │
│                             │
│   [Start New Chat]          │
└─────────────────────────────┘
```

### Error States
```
┌─────────────────────────────┐
│         [⚠️ Icon]           │
│  Oops! Something went wrong │
│                             │
│  [Try Again]                │
└─────────────────────────────┘
```

---

## 🎯 Success Metrics for Design

**User Engagement:**
- Time in chat session > 3 minutes
- Messages per session > 5
- Return user rate > 60%

**UX Quality:**
- Time to first message < 10 seconds
- Error rate < 2%
- Task completion rate > 90%

**Performance:**
- First Contentful Paint < 1.5s
- Time to Interactive < 3.5s
- Animation FPS: 60

---

## 🛠️ Recommended Tech Stack

### Frontend Framework
- **React** or **React Native** (for cross-platform)
- **Next.js** (for web with SSR)
- **Tailwind CSS** (for styling)

### UI Component Libraries
- **shadcn/ui** (Customizable components)
- **Headless UI** (Accessible components)
- **Framer Motion** (Animations)

### State Management
- **Zustand** or **Redux Toolkit**
- **React Query** (Server state)

### WebSocket
- **Socket.io-client** or native **WebSocket API**

### Icons
- **Lucide React** or **Heroicons**

---

## 📱 Mobile App Considerations

### Native Features
- Push notifications for responses
- Biometric authentication (Face ID, Touch ID)
- Offline mode with sync
- Camera access for photo uploads
- Health app integration (iOS Health, Google Fit)

### Platform-Specific Design
- **iOS:** Follow Human Interface Guidelines
- **Android:** Follow Material Design 3
- Native navigation patterns
- Platform-specific animations

---

## 🎨 Example Mockup Tools

Use these tools to create mockups:
- **Figma** (Recommended - collaborative)
- **Sketch** (Mac only)
- **Adobe XD**
- **Framer** (Interactive prototypes)

---

## ✅ MVP Feature Checklist

**Must Have (Phase 1):**
- [ ] Authentication (Sign up, Sign in, Email verification)
- [ ] Real-time chat interface with WebSocket
- [ ] Session list view
- [ ] Basic profile page
- [ ] Responsive mobile layout

**Should Have (Phase 2):**
- [ ] Search conversations
- [ ] Dark mode toggle
- [ ] Push notifications
- [ ] Export conversation
- [ ] Rich text formatting in chat

**Nice to Have (Phase 3):**
- [ ] Voice input
- [ ] Image sharing
- [ ] Health metrics dashboard
- [ ] Workout plan builder
- [ ] Meal planning interface

---

## 🎯 Design Inspiration

**Apps to Reference:**
- **ChatGPT Mobile** - Clean chat interface
- **MyFitnessPal** - Health tracking
- **Headspace** - Calming, masculine design
- **Strava** - Fitness metrics and motivation
- **Calm** - Minimalist, focused UI

**Design Systems:**
- Tailwind UI components
- Material Design 3
- iOS Human Interface Guidelines
- Ant Design

---

## 📞 Final Notes

**Design Goals:**
1. **Fast** - Users get answers in < 5 seconds
2. **Clear** - No confusion on what to do next
3. **Motivating** - Feels like a personal coach
4. **Trustworthy** - Professional enough for health advice
5. **Masculine** - Appeals to target demographic without stereotypes

**Remember:**
- Mobile-first approach
- Dark mode support from day 1
- Accessibility is not optional
- Test on real devices
- Iterate based on user feedback

---

**Ready to build?** Use this spec as your north star, but don't be afraid to iterate based on user testing and feedback!
