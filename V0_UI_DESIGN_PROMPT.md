# v0 UI Design Prompt for EHR Research Platform

## Application Overview
Design a modern, professional Electronic Health Record (EHR) research platform interface. This is a self-adaptive, AI-assisted EHR system for research purposes (not production medical use). The design should be clean, medical-professional, and user-friendly for clinicians, researchers, and administrators.

## Design Requirements

### Style & Aesthetics
- **Color Scheme**: Medical professional palette
  - Primary: Indigo/Blue tones (trust, professionalism)
  - Accent: Red for critical alerts/warnings
  - Success: Green for resolved/active states
  - Background: Light gray/white for clean medical aesthetic
- **Typography**: Clean, readable sans-serif (Inter, System UI, or similar)
- **Layout**: Clean, spacious, card-based design with clear hierarchy
- **Icons**: Medical/healthcare icons where appropriate
- **Accessibility**: High contrast, WCAG compliant, clear focus states

### Key Pages to Design

#### 1. Login Page
- Clean, centered login form
- Email and password fields
- "Sign In" button
- Research platform disclaimer/notice
- Professional medical aesthetic

#### 2. Clinician Dashboard (Patient List)
- Header with user info and "New Patient" button
- Patient list table with:
  - Patient name, age, sex
  - Primary diagnosis
  - Risk level badges (routine, elevated, high, critical)
  - Flags/indicators for alerts
  - Last updated timestamp
- Search and filter functionality
- Pagination
- Sortable columns
- Risk level color coding (green, yellow, orange, red)

#### 3. Patient Detail Page
- **Patient Header Section**:
  - Patient name, age, sex prominently displayed
  - Risk level badge
  - Primary diagnosis
  - Quick action buttons
  
- **Tabbed Navigation** for sections:
  - Summary
  - Demographics
  - Diagnoses
  - Clinical Notes
  - Problems
  - Medications
  - Allergies
  - History (PMH, PSH, Family, Social)
  - Vitals
  - Labs
  - Imaging
  - AI Suggestions
  - Safety & Transparency

- **Section Content Cards**:
  - Each section in a clean white card with shadow
  - "Add" buttons for creating new entries
  - Lists/tables with edit/delete actions
  - Status badges and color coding
  - Empty states with helpful messages

#### 4. Clinical Notes Section
- List of notes (most recent first)
- Each note card showing:
  - Note type badge (Progress, Admission, Discharge, Consult)
  - Encounter date
  - SOAP structure display (CC, HPI, ROS, Physical Exam, Assessment, Plan)
  - Author and timestamp
- "New Note" button opens form with:
  - Note type selector
  - Encounter date picker
  - Text areas for each SOAP component
  - Save/Cancel buttons

#### 5. Problem List Section
- List of problems with:
  - Problem name (prominent)
  - Status badge (Active, Resolved, Chronic, Inactive)
  - ICD-10 code (if available)
  - Onset/resolved dates
  - Notes
- Filter by status dropdown
- "Add Problem" button
- "Mark Resolved" action for active problems
- Color coding: Red for active, Green for resolved

#### 6. Medications Section
- List of medications with:
  - Medication name (prominent)
  - Generic name
  - Dosage, frequency, route, quantity
  - Status badge (Active, Discontinued, Completed)
  - Start/end dates
  - Indication
  - Notes
- Filter by status
- "Add Medication" button with comprehensive form
- "Discontinue" action for active medications
- Color coding: Green for active, Red for discontinued

#### 7. Allergies Section
- List of allergies with:
  - Allergen name (prominent)
  - Severity badge (Mild, Moderate, Severe, Life-threatening)
  - Allergen type (Medication, Food, Environmental)
  - Reaction description
  - Warning banner for severe/life-threatening allergies
- "Add Allergy" button
- Prominent warning display for critical allergies
- Color coding: Red for severe/life-threatening

#### 8. Patient History Section
- Four editable sections:
  - Past Medical History (PMH)
  - Past Surgical History (PSH)
  - Family History
  - Social History
- Each section:
  - Current content display
  - "Edit" button
  - Text area for editing
  - Save/Cancel buttons
- Clean, organized layout

#### 9. Vitals Section
- Interactive trend graph (line chart)
- Time range selector
- Abnormal value highlighting
- Table view option
- Color coding for normal/abnormal ranges

#### 10. Labs Section
- Sortable, filterable table
- Abnormal value highlighting
- Trending indicators (↑ ↓)
- Pagination
- Date columns

#### 11. Imaging Section
- Image grid/list view
- Image viewer with zoom/pan controls
- AI heatmap overlay toggle
- Upload functionality
- Metadata display

#### 12. AI Suggestions Panel
- Suggestion cards with:
  - "Experimental" label (prominent)
  - Confidence score
  - Explanation
  - Action buttons (Accept, Ignore, Not Relevant)
- Safety warning banner
- Feedback collection

#### 13. Safety & Transparency Section
- AI Status Panel (active models and versions)
- Suggestion Audit Trail
- Transparency Information
- Safety guardrails display

#### 14. Researcher Dashboard
- Analytics metrics:
  - Suggestion acceptance/ignore rates
  - Navigation patterns
  - Adaptation events
  - Model performance
- Charts and visualizations
- Log viewer with filtering
- Export functionality

#### 15. Admin System Controls
- Tabbed interface:
  - User Management (list, create, edit, delete users)
  - System Status (backend, database, model services)
  - Synthetic Data Generation
  - Adaptation Configuration
  - System Logs
- Clean admin interface with status indicators

### Component Patterns

#### Cards
- White background
- Subtle shadow (shadow-sm)
- Rounded corners (rounded-lg)
- Padding for content
- Hover effects for interactivity

#### Badges/Status Indicators
- Small, rounded pills
- Color-coded:
  - Green: Active, Normal, Resolved
  - Yellow: Elevated, Warning
  - Orange: High Risk
  - Red: Critical, Severe, Discontinued
  - Gray: Inactive, Completed

#### Forms
- Clean input fields
- Clear labels
- Required field indicators (*)
- Validation error messages
- Submit buttons with loading states

#### Tables
- Clean, minimal design
- Sortable headers
- Hover row highlighting
- Pagination controls
- Action buttons (Edit, Delete, etc.)

#### Buttons
- Primary: Indigo/Blue (main actions)
- Secondary: Gray (cancel, secondary actions)
- Danger: Red (delete, critical actions)
- Success: Green (resolve, complete actions)
- Clear hover states
- Disabled states

#### Empty States
- Helpful message
- "Add" button or action
- Subtle illustration or icon

### Key Features to Emphasize

1. **Risk Level Indicators**: Prominent, color-coded badges throughout
2. **AI Experimental Labels**: Clear "Experimental" badges on all AI suggestions
3. **Safety Warnings**: Prominent warning banners for severe allergies, critical risks
4. **Adaptation Indicators**: Subtle indicators when UI has been adapted by MAPE-K system
5. **Status Badges**: Clear status indicators (Active, Resolved, etc.)
6. **Timestamps**: Clear date/time displays
7. **Loading States**: Skeleton loaders or spinners
8. **Error States**: Clear error messages with retry options

### Responsive Design
- Mobile-friendly navigation
- Collapsible sections on small screens
- Touch-friendly buttons and inputs
- Responsive tables (scrollable or card view on mobile)

### Accessibility
- High contrast text
- Clear focus indicators
- Keyboard navigation support
- Screen reader friendly
- ARIA labels where needed

## Design Inspiration
- Modern medical software (Epic, Cerner style but cleaner)
- Research platform aesthetics (clean, data-focused)
- Professional healthcare dashboards
- Clean, minimal design with medical color coding

## Technical Context
- Built with Next.js 14+ (React)
- TailwindCSS for styling
- TypeScript
- Component-based architecture
- Dark mode not required (light theme only)

---

## v0 Prompt (Copy This)

Design a modern Electronic Health Record (EHR) research platform interface with a clean, medical-professional aesthetic. The application serves clinicians, researchers, and administrators managing patient records in a research setting.

**Key Design Elements:**
- Color scheme: Indigo/blue primary, red for critical alerts, green for success, light gray backgrounds
- Clean, card-based layout with clear visual hierarchy
- Medical-professional typography (sans-serif, highly readable)
- Prominent status badges and risk level indicators (color-coded: green/yellow/orange/red)
- Clear "Experimental" labels on AI features

**Main Pages:**
1. **Login Page**: Centered form, professional medical aesthetic
2. **Clinician Dashboard**: Patient list table with risk badges, search/filter, sortable columns
3. **Patient Detail Page**: Tabbed navigation with sections for Summary, Demographics, Diagnoses, Clinical Notes (SOAP structure), Problems, Medications, Allergies, History (PMH/PSH/Family/Social), Vitals (trend graphs), Labs (sortable table), Imaging (viewer with zoom), AI Suggestions (with experimental labels), Safety & Transparency
4. **Clinical Notes**: List of SOAP notes with form for creating new notes (CC, HPI, ROS, Physical Exam, Assessment, Plan)
5. **Problem List**: Active/resolved problems with status badges, ICD codes, filter by status
6. **Medications**: Medication list with dosage/frequency/route, status filtering, comprehensive add form
7. **Allergies**: Allergy list with severity badges, prominent warnings for severe/life-threatening allergies
8. **Patient History**: Four editable sections (PMH, PSH, Family, Social) with edit/save functionality
9. **Researcher Dashboard**: Analytics with charts, metrics, log viewer
10. **Admin Controls**: Tabbed interface for user management, system status, data generation, configuration

**Component Patterns:**
- White cards with subtle shadows
- Color-coded badges (green=active/normal, red=critical/severe, yellow=warning, gray=inactive)
- Clean forms with clear labels and validation
- Sortable tables with hover effects
- Empty states with helpful messages
- Loading spinners/skeletons
- Error messages with retry options

**Key Features:**
- Risk level indicators throughout (routine/elevated/high/critical)
- AI experimental labels on all suggestions
- Safety warning banners for critical items
- Status badges (Active, Resolved, Discontinued, etc.)
- Responsive design (mobile-friendly)
- High contrast, accessible design

Create a cohesive, professional medical interface that feels trustworthy and modern while maintaining clarity and usability for healthcare professionals.

