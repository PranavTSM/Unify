# Unified Inbox Application

A modern, professional unified inbox application built with React.js, Tailwind CSS, and Shadcn UI principles. This application provides a comprehensive messaging and calendar management system with AI-powered insights.

## Features

### 🎯 Dashboard
- Real-time statistics and metrics
- Recent messages overview
- Today's schedule at a glance
- Quick action buttons for common tasks

### 📧 Inbox
- Unified message view across multiple platforms (Teams, Outlook)
- Three-column layout: filters, message list, and preview pane
- Smart filtering by platform
- Real-time message search
- Message preview with attachment support
- Quick actions (Reply, Forward, Archive, etc.)

### 📊 View Details
- Full message content display
- AI-powered summarization
- Intelligent insights and sentiment analysis
- Key points extraction
- Suggested actions
- Related messages
- Priority and sentiment indicators
- Downloadable attachments

### 📅 Calendar
- Interactive monthly calendar view
- Event management and scheduling
- Color-coded event types
- Daily event details
- Upcoming events sidebar
- Quick statistics
- Multi-attendee support

## Technology Stack

- **Frontend Framework**: React 18.3+
- **Build Tool**: Vite 5.4+
- **Styling**: Tailwind CSS 3.4+
- **Routing**: React Router DOM 6.26+
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to:
```
http://localhost:5173
```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   └── Badge.jsx
│   │   └── Layout.jsx    # Main layout with sidebar
│   ├── pages/            # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Inbox.jsx
│   │   ├── ViewDetails.jsx
│   │   └── Calendar.jsx
│   ├── data/
│   │   └── mockData.js   # Mock data for demo
│   ├── lib/
│   │   └── utils.js      # Utility functions
│   ├── App.jsx           # Main app with routing
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Design Features

### Professional Theme
- Clean, modern interface with a professional color scheme
- Consistent spacing and typography
- Smooth transitions and hover effects
- Responsive design (mobile-friendly)

### UX Best Practices
- Intuitive navigation with clear visual hierarchy
- Contextual actions based on user selection
- Real-time feedback for interactions
- Accessible color contrast ratios
- Loading states and empty states

### UI Components
- Custom-built components following Shadcn UI principles
- Consistent design system with CSS variables
- Reusable and composable components
- Dark mode ready (CSS variables configured)

## Customization

### Colors
Edit the CSS variables in `src/index.css` to customize the color scheme:

```css
:root {
  --primary: 199 89% 48%;
  --secondary: 210 40% 96.1%;
  /* ... more variables */
}
```

### Mock Data
Update `src/data/mockData.js` to customize messages and calendar events.

### Adding New Pages
1. Create a new component in `src/pages/`
2. Add a route in `src/App.jsx`
3. Add navigation item in `src/components/Layout.jsx`

## Features Showcase

### Dashboard
- Statistics cards with trend indicators
- Recent messages with read/unread status
- Today's schedule with event types
- Quick action shortcuts

### Inbox
- Filter by platform (All, Teams, Outlook)
- Search functionality
- Message preview with sender avatar
- Attachment indicators
- Category badges
- Smooth navigation to detail view

### View Details
- Complete message content
- AI summarization with key points
- Sentiment analysis
- Priority indicators
- Suggested actions
- Related messages
- Export and print options

### Calendar
- Interactive month view
- Day selection with event display
- Color-coded event types
- Time and duration display
- Attendee information
- Upcoming events list
- Weekly statistics

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Design inspired by modern email clients and productivity apps
- Icons by Lucide Icons
- UI principles from Shadcn UI

