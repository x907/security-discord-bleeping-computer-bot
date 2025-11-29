"""Discord webhook poster for BleepingComputer articles."""

import requests
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscordPoster:
    """Posts formatted articles to Discord via webhook."""

    def __init__(self, webhook_url: str):
        """
        Initialize the Discord poster.

        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url

    def post_article(self, article: Dict, scraped_data: Optional[Dict] = None) -> bool:
        """
        Post an article to Discord.

        Args:
            article: Article data from RSS feed
            scraped_data: Additional scraped data (optional)

        Returns:
            True if posted successfully, False otherwise
        """
        try:
            embed = self._create_embed(article, scraped_data)
            payload = {
                'embeds': [embed]
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"Posted article to Discord: {article['title']}")
            return True

        except requests.RequestException as e:
            logger.error(f"Error posting to Discord: {e}")
            return False

    def _create_embed(self, article: Dict, scraped_data: Optional[Dict] = None) -> Dict:
        """
        Create a Discord embed for the article.

        Args:
            article: Article data
            scraped_data: Scraped additional data

        Returns:
            Discord embed dictionary
        """
        scraped_data = scraped_data or {}

        # Build description
        description = scraped_data.get('description') or article.get('summary', '')
        # Strip HTML tags from summary if present
        if description:
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'html.parser').get_text()
            # Limit to 300 characters for clean formatting
            if len(description) > 300:
                description = description[:297] + '...'

        # Parse published date
        timestamp = self._parse_timestamp(article.get('published'))

        # Build embed
        embed = {
            'title': article['title'],
            'url': article['link'],
            'description': description,
            'color': 0xE74C3C,  # BleepingComputer red
            'timestamp': timestamp,
            'footer': {
                'text': 'BleepingComputer',
                'icon_url': 'https://www.bleepstatic.com/favicon/apple-icon-60x60.png'
            },
            'author': {
                'name': article.get('author', 'BleepingComputer'),
            }
        }

        # Add image if available
        image_url = scraped_data.get('image_url')
        if image_url:
            embed['image'] = {'url': image_url}

        # Add category as field if available
        category = scraped_data.get('category')
        if category:
            embed['fields'] = [
                {
                    'name': 'Category',
                    'value': category,
                    'inline': True
                }
            ]

        return embed

    def _parse_timestamp(self, published: str) -> Optional[str]:
        """
        Parse published date to ISO 8601 format for Discord.

        Args:
            published: Published date string

        Returns:
            ISO 8601 formatted timestamp or None
        """
        try:
            from dateutil import parser
            dt = parser.parse(published)
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Could not parse timestamp '{published}': {e}")
            return None
