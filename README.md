# BleepingComputer RSS to Discord Bot

A professional Python bot that monitors BleepingComputer's RSS feed and automatically posts new security articles to a Discord channel via webhooks.

## Features

- Scans BleepingComputer RSS feed for new articles
- Filters out sponsored/advertisement content
- Scrapes article pages for additional details (images, descriptions, categories)
- Posts beautifully formatted embeds to Discord
- Maintains state to prevent duplicate posts
- Runs automatically every hour via GitHub Actions
- Automatic cleanup of old state entries (30-day retention)

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── scan.yml              # GitHub Actions workflow
├── src/
│   └── bleeping_scanner/
│       ├── __init__.py
│       ├── rss_scanner.py        # RSS feed parser
│       ├── web_scraper.py        # Article detail scraper
│       ├── discord_poster.py     # Discord webhook integration
│       └── state_manager.py      # Duplicate prevention
├── main.py                       # Entry point
├── requirements.txt              # Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.11 or higher
- A Discord webhook URL
- GitHub repository (for automated runs)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/x907/security-discord-bleeping-computer-bot.git
cd security-discord-bleeping-computer-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
export LOG_LEVEL="INFO"  # Optional: DEBUG, INFO, WARNING, ERROR
```

4. Run manually:
```bash
python main.py
```

### Discord Webhook Setup

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Configure the webhook:
   - Name: BleepingComputer Bot
   - Channel: Select your desired channel
5. Copy the webhook URL

### GitHub Actions Setup

The bot runs automatically every hour via GitHub Actions. To set it up:

1. The workflow file is already created at `.github/workflows/scan.yml`

2. You need to add your Discord webhook as a GitHub secret:
   - The secret name should be: `DISCORD_WEBHOOK_URL`
   - You'll be prompted to provide this value

3. The workflow will:
   - Run every hour (on the hour)
   - Install dependencies
   - Scan for new articles
   - Post to Discord
   - Commit the updated state file

### Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab:
1. Go to your repository on GitHub
2. Click "Actions"
3. Select "Scan BleepingComputer RSS"
4. Click "Run workflow"

## Configuration

### Environment Variables

- `DISCORD_WEBHOOK_URL` (required): Discord webhook URL for posting
- `LOG_LEVEL` (optional): Logging level (default: INFO)

### State Management

The bot maintains a `posted_articles.json` file to track posted articles:
- Prevents duplicate posts
- Automatically cleaned up (30-day retention)
- Committed to the repository by GitHub Actions

## How It Works

1. **RSS Scanning**: Fetches the BleepingComputer RSS feed
2. **Filtering**: Removes sponsored/advertisement content
3. **State Check**: Compares against posted articles
4. **Web Scraping**: Extracts additional details (image, description, category)
5. **Discord Post**: Creates formatted embed and posts via webhook
6. **State Update**: Marks article as posted

## Discord Post Format

Each article is posted as a rich embed with:
- Article title (clickable link)
- Featured image
- Article description/excerpt
- Category badge
- Author name
- Publication timestamp
- BleepingComputer branding

## Dependencies

- `feedparser`: RSS feed parsing
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing for web scraping
- `python-dateutil`: Date parsing

## License

MIT License - See repository for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
