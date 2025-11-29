#!/usr/bin/env python3
"""Main entry point for BleepingComputer RSS to Discord bot."""

import os
import sys
import logging
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bleeping_scanner.rss_scanner import RSSScanner
from bleeping_scanner.web_scraper import WebScraper
from bleeping_scanner.discord_poster import DiscordPoster
from bleeping_scanner.state_manager import StateManager


def setup_logging(log_level: str = 'INFO') -> None:
    """
    Configure logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_discord_webhook() -> Optional[str]:
    """
    Get Discord webhook URL from environment.

    Returns:
        Webhook URL or None if not set
    """
    webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook:
        logging.error("DISCORD_WEBHOOK_URL environment variable not set")
        return None
    return webhook


def main() -> int:
    """
    Main execution function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Setup
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting BleepingComputer RSS scanner")

    # Get Discord webhook
    webhook_url = get_discord_webhook()
    if not webhook_url:
        return 1

    # Initialize components
    scanner = RSSScanner()
    scraper = WebScraper()
    poster = DiscordPoster(webhook_url)
    state_manager = StateManager()

    # Fetch articles from RSS feed
    logger.info("Fetching articles from RSS feed")
    articles = scanner.fetch_articles()

    if not articles:
        logger.warning("No articles found in RSS feed")
        return 0

    # Filter new articles
    new_articles = state_manager.get_new_articles(articles)

    if not new_articles:
        logger.info("No new articles to post")
        return 0

    # Process new articles
    posted_count = 0
    failed_count = 0

    for article in new_articles:
        logger.info(f"Processing: {article['title']}")

        # Scrape additional details
        scraped_data = scraper.scrape_article(article['link'])

        # Post to Discord
        success = poster.post_article(article, scraped_data)

        if success:
            state_manager.mark_posted(article['id'])
            posted_count += 1
        else:
            failed_count += 1
            logger.error(f"Failed to post article: {article['title']}")

    # Summary
    logger.info(f"Scan complete: {posted_count} posted, {failed_count} failed")

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
