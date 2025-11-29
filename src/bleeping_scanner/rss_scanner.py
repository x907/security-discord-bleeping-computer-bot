"""RSS feed scanner for BleepingComputer."""

import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RSSScanner:
    """Scans BleepingComputer RSS feed for new articles."""

    RSS_FEED_URL = "https://www.bleepingcomputer.com/feed/"

    def __init__(self):
        """Initialize the RSS scanner."""
        self.feed_url = self.RSS_FEED_URL

    def fetch_articles(self) -> List[Dict]:
        """
        Fetch articles from the RSS feed.

        Returns:
            List of article dictionaries with title, link, published date, etc.
        """
        try:
            logger.info(f"Fetching RSS feed from {self.feed_url}")
            feed = feedparser.parse(self.feed_url)

            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")

            articles = []
            for entry in feed.entries:
                # Filter out sponsored/ad posts
                if self._is_sponsored(entry):
                    logger.info(f"Skipping sponsored post: {entry.get('title', 'Unknown')}")
                    continue

                article = self._parse_entry(entry)
                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles (filtered out sponsored content)")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return []

    def _is_sponsored(self, entry: Dict) -> bool:
        """
        Check if an RSS entry is sponsored/ad content.

        Args:
            entry: RSS feed entry

        Returns:
            True if sponsored, False otherwise
        """
        title = entry.get('title', '').lower()
        summary = entry.get('summary', '').lower()

        # Common indicators of sponsored content
        sponsored_keywords = [
            'sponsored',
            'advertisement',
            'promoted',
            '[ad]',
            '(ad)',
            'partner content'
        ]

        for keyword in sponsored_keywords:
            if keyword in title or keyword in summary:
                return True

        # Check tags/categories
        tags = entry.get('tags', [])
        for tag in tags:
            tag_term = tag.get('term', '').lower()
            if 'sponsored' in tag_term or 'advertisement' in tag_term:
                return True

        return False

    def _parse_entry(self, entry: Dict) -> Dict:
        """
        Parse an RSS entry into a structured article dictionary.

        Args:
            entry: RSS feed entry

        Returns:
            Parsed article dictionary
        """
        return {
            'title': entry.get('title', 'No Title'),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'published_parsed': entry.get('published_parsed'),
            'summary': entry.get('summary', ''),
            'author': entry.get('author', 'BleepingComputer'),
            'id': entry.get('id', entry.get('link', '')),
        }
