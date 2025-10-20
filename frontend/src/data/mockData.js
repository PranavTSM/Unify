export const messages = [
  {
    id: 1,
    sender: 'Alice Johnson',
    subject: 'Project Alpha - Meeting notes',
    preview: 'Hi Team, Please find attached the meeting notes from our Project Alpha discussion on Tuesday. Key action items include finalizing the mockups by end-of-week...',
    content: 'Hi Team, Please find attached the meeting notes from our Project Alpha discussion on Tuesday. Key action items include finalizing the mockups by end-of-week and preparing the client presentation for next Monday. We also need to review the Q3 budget proposals. Best regards, Alice Johnson',
    time: new Date('2024-10-11T10:30:00'),
    read: false,
    hasAttachment: true,
    category: 'Teams',
    avatar: 'AJ'
  },
  {
    id: 2,
    sender: 'Bob Williams',
    subject: 'Daily Standup - Team Sync',
    preview: 'Hey everyone, Quick reminder for our daily standup in 5 minutes. Please come prepared with your updates on current tasks and any blockers. Link is in the usual Teams channel.',
    content: 'Hey everyone, Quick reminder for our daily standup in 5 minutes. Please come prepared with your updates on current tasks and any blockers. Link is in the usual Teams channel.',
    time: new Date('2024-10-11T09:00:00'),
    read: false,
    hasAttachment: false,
    category: 'Teams',
    avatar: 'BW'
  },
  {
    id: 3,
    sender: 'Charlie Davis',
    subject: 'Invoice #2024-001 for March Services',
    preview: 'Dear Accounts Team, Attached is invoice #2024-001 for the services rendered in March. Please process at your earliest convenience. Let me know if you need any further documentation.',
    content: 'Dear Accounts Team, Attached is invoice #2024-001 for the services rendered in March. Please process at your earliest convenience. Let me know if you need any further documentation.',
    time: new Date('2024-10-10T14:20:00'),
    read: true,
    hasAttachment: true,
    category: 'Outlook',
    avatar: 'CD'
  },
  {
    id: 4,
    sender: 'Diana Prince',
    subject: 'Urgent: Server Maintenance Notification',
    preview: 'Attention All Users, Our IT team will be performing urgent server maintenance tonight from 11 PM to 1 AM PST. Services may be temporarily unavailable during this window. We apologize for any inconvenience.',
    content: 'Attention All Users, Our IT team will be performing urgent server maintenance tonight from 11 PM to 1 AM PST. Services may be temporarily unavailable during this window. We apologize for any inconvenience.',
    time: new Date('2024-10-09T16:45:00'),
    read: true,
    hasAttachment: false,
    category: 'Teams',
    avatar: 'DP'
  },
  {
    id: 5,
    sender: 'Eve Adams',
    subject: 'Marketing Campaign Q2 Brainstorm',
    preview: "Hey marketing squad, Let's schedule a brainstorm for our Q2 campaign strategy. I've put together some initial ideas in a shared document. Please review before our meeting.",
    content: "Hey marketing squad, Let's schedule a brainstorm for our Q2 campaign strategy. I've put together some initial ideas in a shared document. Please review before our meeting.",
    time: new Date('2024-10-07T11:30:00'),
    read: true,
    hasAttachment: true,
    category: 'Teams',
    avatar: 'EA'
  },
];

export const dashboardStats = [
  { title: 'Total Messages', value: '1,284', change: '+12%', trend: 'up' },
  { title: 'Unread', value: '23', change: '-5%', trend: 'down' },
  { title: 'Sent Today', value: '18', change: '+8%', trend: 'up' },
  { title: 'Response Time', value: '2.4h', change: '-15%', trend: 'down' },
];

export const calendarEvents = [
  {
    id: 1,
    title: 'Team Standup',
    date: new Date('2024-10-11T09:00:00'),
    duration: '30 min',
    type: 'meeting',
    attendees: ['John Doe', 'Jane Smith', 'Bob Williams'],
  },
  {
    id: 2,
    title: 'Project Alpha Review',
    date: new Date('2024-10-11T14:00:00'),
    duration: '1 hour',
    type: 'meeting',
    attendees: ['Alice Johnson', 'Charlie Davis', 'Diana Prince'],
  },
  {
    id: 3,
    title: 'Client Presentation',
    date: new Date('2024-10-14T10:00:00'),
    duration: '2 hours',
    type: 'presentation',
    attendees: ['Team Alpha', 'Client Representatives'],
  },
  {
    id: 4,
    title: 'Q3 Budget Review',
    date: new Date('2024-10-15T15:00:00'),
    duration: '1 hour',
    type: 'meeting',
    attendees: ['Finance Team', 'Department Heads'],
  },
];

