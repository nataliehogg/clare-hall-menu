# Clare Hall menu calendar

An auto-updating calendar of lunch and dinner in the Clare Hall Dining Hall, scraped every few hours from the [college's weekly menu](https://sway.cloud.microsoft/b7Zz74Q2g96EIhE9).

Each day has an event for lunch (12:00–13:30) and dinner (18:00–19:00), titled **CH lunch**, **CH dinner** or **CH closed**. Tap the event to see the full menu.

## Subscribe

Copy this link — it's the only thing you need:

```
https://nataliehogg.github.io/clare-hall-menu/menu.ics
```

Then follow the instructions for your calendar app below. The calendar is read-only and refreshes itself automatically — you only need to do this once.

### On a phone — the quick way

Tap this link on your phone and your calendar app should offer to subscribe:

[webcal://nataliehogg.github.io/clare-hall-menu/menu.ics](webcal://nataliehogg.github.io/clare-hall-menu/menu.ics)

If that doesn't work, use the app-specific steps below.

### Google Calendar (in a web browser)

1. Open [calendar.google.com](https://calendar.google.com).
2. On the left, next to **Other calendars**, click the **+** button.
3. Choose **From URL**.
4. Paste the link above and click **Add calendar**.

> Note: Google only refreshes subscribed calendars every few hours, so last-minute menu changes may take a while to appear. This is a Google limitation, not a problem with the calendar.

### iPhone / iPad

1. Open the **Settings** app.
2. Scroll down and tap **Calendar** → **Accounts** → **Add Account**.
3. Tap **Other** → **Add Subscribed Calendar**.
4. Paste the link above and tap **Next**, then **Save**.

### Mac (Apple Calendar)

1. Open the **Calendar** app.
2. From the menu bar choose **File** → **New Calendar Subscription…**
3. Paste the link above and click **Subscribe**.
4. Set **Auto-refresh** to **Every hour** (or leave the default) and click **OK**.

### Outlook on the web (outlook.com / office.com)

1. Open your calendar in Outlook.
2. Click **Add calendar** → **Subscribe from web**.
3. Paste the link above, give the calendar a name, and click **Import**.

### Outlook desktop app (Windows)

1. In Calendar view, click **Add Calendar** → **From Internet…**
2. Paste the link above and click **Yes** when asked to confirm.

### Thunderbird

1. Go to the **Calendar** tab.
2. Right-click in the calendar list on the left → **New Calendar…**
3. Choose **On the Network**, then **Next**.
4. Paste the link above, click **Next**, give it a name, and finish.

## FAQ

**Do I need to update anything when the menu changes?**
No. Your calendar app checks for updates automatically every few hours.

**Will I get notifications before meals?**
By default subscribed calendars don't usually notify you. If you want reminders, most calendar apps let you add your own notifications to events you've subscribed to.

**Can anyone else see I've subscribed?**
No. Subscribing is private — only you can see your own calendar.

**The calendar looks empty or out of date.**
The college sometimes changes the menu late, and your calendar app may take a few hours to fetch the latest version. Google Calendar is the slowest at this (often 6+ hours). Try again later, or remove and re-add the subscription.

## How it works

A GitHub Actions workflow runs `menu.py` every few hours. The script fetches the college's weekly-menu Sway, pulls out each day's lunch and dinner, and writes `public/menu.ics` — a standard iCalendar file hosted on GitHub Pages. The whole thing runs itself; there's no server and nothing to maintain.

To run it locally: `python menu.py` (needs Chrome or Chromium installed).
