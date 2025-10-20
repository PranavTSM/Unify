# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Open Your Browser
Navigate to: **http://localhost:5173**

---

## 📱 Application Overview

### Navigation
Use the sidebar to navigate between:
- **Dashboard**: Overview of messages and today's schedule
- **Inbox**: Unified message center
- **View Details**: Detailed message analysis with AI insights
- **Calendar**: Schedule and event management

### Key Features to Try

#### 📊 Dashboard
- View statistics cards with trends
- Check recent messages
- See today's schedule
- Use quick action buttons

#### 📧 Inbox
1. Click on any message to preview
2. Use filters (All/Teams/Outlook) to organize
3. Search messages using the search bar
4. Click "View Full Details" for AI insights
5. Try Reply, Forward, or Archive actions

#### 🔍 View Details
- Read full message content
- View AI-generated summary
- Check key points extraction
- See sentiment and priority analysis
- Access suggested actions
- Download attachments

#### 📅 Calendar
- Click on any day to view events
- Use arrow buttons to navigate months
- Click "Today" to return to current date
- View event details in sidebar
- Check upcoming events list

---

## 🎨 Customization Tips

### Change Colors
Edit `src/index.css` and modify CSS variables:
```css
--primary: 199 89% 48%; /* Main brand color */
```

### Add Your Data
Replace mock data in `src/data/mockData.js` with:
- Your actual messages
- Real calendar events
- Custom dashboard stats

### Add Features
1. Create new components in `src/components/`
2. Add new pages in `src/pages/`
3. Update routing in `src/App.jsx`

---

## 🛠️ Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |

---

## 🎯 What's Next?

1. **Connect Real Data**: Replace mock data with API calls
2. **Add Authentication**: Implement user login
3. **Database Integration**: Connect to your backend
4. **Email Integration**: Link to actual email services
5. **Calendar Sync**: Integrate with Google Calendar, Outlook, etc.
6. **Notifications**: Add real-time notifications
7. **Dark Mode**: Enable theme switching
8. **Mobile App**: Convert to React Native

---

## 📞 Need Help?

- Check the full README.md for detailed documentation
- Review component code in `src/components/` and `src/pages/`
- All components are well-commented and self-documenting

---

## ✨ Pro Tips

- Use `Ctrl+Click` (or `Cmd+Click` on Mac) to open links in new tabs
- The application is fully responsive - try it on mobile!
- All dates and times are automatically formatted based on your locale
- Unread messages are highlighted with a blue background
- Today's date is highlighted in the calendar with a blue circle

Enjoy your Unified Inbox Application! 🎉

