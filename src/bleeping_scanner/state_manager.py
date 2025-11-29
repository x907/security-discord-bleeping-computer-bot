"""State management for tracking processed articles."""

import json
import os
from typing import Set, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Manages state to prevent duplicate posts."""

    def __init__(self, state_file: str = 'posted_articles.json', retention_days: int = 30):
        """
        Initialize the state manager.

        Args:
            state_file: Path to the state file
            retention_days: Number of days to keep article IDs in state
        """
        self.state_file = state_file
        self.retention_days = retention_days
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, str]:
        """
        Load state from file.

        Returns:
            Dictionary mapping article IDs to posted timestamps
        """
        if not os.path.exists(self.state_file):
            logger.info(f"State file not found, starting fresh")
            return {}

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                logger.info(f"Loaded state with {len(state)} articles")
                return state
        except Exception as e:
            logger.error(f"Error loading state file: {e}")
            return {}

    def _save_state(self) -> None:
        """Save state to file."""
        try:
            # Clean old entries before saving
            self._cleanup_old_entries()

            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
                logger.info(f"Saved state with {len(self.state)} articles")
        except Exception as e:
            logger.error(f"Error saving state file: {e}")

    def _cleanup_old_entries(self) -> None:
        """Remove entries older than retention_days."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_timestamp = cutoff_date.isoformat()

        old_count = len(self.state)
        self.state = {
            article_id: timestamp
            for article_id, timestamp in self.state.items()
            if timestamp >= cutoff_timestamp
        }

        removed = old_count - len(self.state)
        if removed > 0:
            logger.info(f"Cleaned up {removed} old entries from state")

    def is_posted(self, article_id: str) -> bool:
        """
        Check if an article has been posted.

        Args:
            article_id: Unique article identifier

        Returns:
            True if article has been posted, False otherwise
        """
        return article_id in self.state

    def mark_posted(self, article_id: str) -> None:
        """
        Mark an article as posted.

        Args:
            article_id: Unique article identifier
        """
        self.state[article_id] = datetime.now().isoformat()
        self._save_state()

    def get_new_articles(self, articles: list) -> list:
        """
        Filter out articles that have already been posted.

        Args:
            articles: List of article dictionaries

        Returns:
            List of new articles not yet posted
        """
        new_articles = [
            article for article in articles
            if not self.is_posted(article['id'])
        ]

        logger.info(f"Found {len(new_articles)} new articles out of {len(articles)} total")
        return new_articles
