"""Web scraper for extracting article details from BleepingComputer."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes article pages for additional details."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the web scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_article(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape article page for additional details.

        Args:
            url: Article URL

        Returns:
            Dictionary with scraped details (description, image_url, category)
        """
        try:
            logger.info(f"Scraping article: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            return {
                'description': self._extract_description(soup),
                'image_url': self._extract_image(soup),
                'category': self._extract_category(soup),
            }

        except requests.RequestException as e:
            logger.error(f"Error scraping article {url}: {e}")
            return {
                'description': None,
                'image_url': None,
                'category': None,
            }

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article description/excerpt."""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        # Try first paragraph of article content
        article = soup.find('div', class_='articleBody')
        if article:
            first_p = article.find('p')
            if first_p:
                text = first_p.get_text().strip()
                # Limit length
                return text[:300] + '...' if len(text) > 300 else text

        return None

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article featured image URL."""
        # Try Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']

        # Try Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']

        # Try article header image
        article_img = soup.find('img', class_='article_header_img')
        if article_img and article_img.get('src'):
            return article_img['src']

        return None

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article category."""
        # Try breadcrumb navigation
        breadcrumb = soup.find('div', class_='breadcrumbs')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) > 1:
                return links[-1].get_text().strip()

        # Try category meta tag
        category_meta = soup.find('meta', property='article:section')
        if category_meta and category_meta.get('content'):
            return category_meta['content']

        return None
