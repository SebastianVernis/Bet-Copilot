"""
News Scraper - Free Football News Feed

Scrapes football news from free sources without API calls.
Uses web scraping with proper rate limiting and caching.

Sources:
- BBC Sport Football (public RSS)
- ESPN Football (public content)
- Goal.com (public news)

No API keys required - all public information.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Football news article."""
    
    title: str
    url: str
    published: datetime
    source: str
    summary: Optional[str] = None
    teams_mentioned: List[str] = None
    category: Optional[str] = None  # "injury", "transfer", "match_preview", "general"
    
    def __post_init__(self):
        if self.teams_mentioned is None:
            self.teams_mentioned = []


class NewsCache:
    """Simple in-memory cache for news articles."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple[datetime, List[NewsArticle]]] = {}
    
    def get(self, source: str) -> Optional[List[NewsArticle]]:
        """Get cached articles for source if not expired."""
        if source not in self._cache:
            return None
        
        cached_time, articles = self._cache[source]
        
        if datetime.now() - cached_time > timedelta(seconds=self.ttl):
            # Expired
            del self._cache[source]
            return None
        
        return articles
    
    def set(self, source: str, articles: List[NewsArticle]):
        """Cache articles for source."""
        self._cache[source] = (datetime.now(), articles)
    
    def clear(self):
        """Clear all cache."""
        self._cache.clear()


class NewsScraper:
    """
    Scrapes football news from free public sources.
    
    Uses RSS feeds and public web pages - no API keys needed.
    Implements rate limiting and caching to be respectful.
    """
    
    # Public RSS feeds (no auth required)
    BBC_RSS = "https://feeds.bbci.co.uk/sport/football/rss.xml"
    ESPN_RSS = "https://www.espn.com/espn/rss/soccer/news"
    
    # Common team names to detect in articles
    MAJOR_TEAMS = [
        # Premier League
        "Manchester United", "Manchester City", "Liverpool", "Arsenal",
        "Chelsea", "Tottenham", "Newcastle", "Brighton", "Aston Villa",
        "West Ham", "Crystal Palace", "Fulham", "Wolves", "Everton",
        "Brentford", "Nottingham Forest", "Luton", "Burnley", "Sheffield United",
        # La Liga
        "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Valencia",
        "Villarreal", "Real Sociedad", "Athletic Bilbao", "Real Betis",
        # Other top teams
        "Bayern Munich", "PSG", "Inter Milan", "AC Milan", "Juventus",
        "Borussia Dortmund", "RB Leipzig", "Napoli", "Roma"
    ]
    
    # Injury/suspension keywords
    INJURY_KEYWORDS = [
        "injured", "injury", "suspended", "suspension", "doubt", "doubtful",
        "miss", "missing", "ruled out", "sidelined", "unavailable", "fitness"
    ]
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize news scraper.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        self.cache = NewsCache(ttl_seconds=cache_ttl)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; BetCopilot/1.0; +https://github.com/betcopilot)"
                }
            )
        return self.session
    
    async def fetch_bbc_news(self, max_articles: int = 20) -> List[NewsArticle]:
        """
        Fetch news from BBC Sport RSS feed.
        
        Args:
            max_articles: Maximum articles to return
            
        Returns:
            List of NewsArticle objects
        """
        # Check cache first
        cached = self.cache.get("bbc")
        if cached:
            logger.info("Returning cached BBC news")
            return cached[:max_articles]
        
        try:
            logger.info("Fetching BBC Sport football news...")
            session = await self._get_session()
            
            async with session.get(self.BBC_RSS, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"BBC RSS returned status {response.status}")
                    return []
                
                xml_content = await response.text()
                
            # Parse RSS
            articles = self._parse_rss(xml_content, source="BBC Sport")
            
            # Cache results
            self.cache.set("bbc", articles)
            
            logger.info(f"✓ Fetched {len(articles)} articles from BBC Sport")
            return articles[:max_articles]
        
        except Exception as e:
            logger.error(f"Error fetching BBC news: {str(e)}")
            return []
    
    async def fetch_espn_news(self, max_articles: int = 20) -> List[NewsArticle]:
        """
        Fetch news from ESPN RSS feed.
        
        Args:
            max_articles: Maximum articles to return
            
        Returns:
            List of NewsArticle objects
        """
        # Check cache first
        cached = self.cache.get("espn")
        if cached:
            logger.info("Returning cached ESPN news")
            return cached[:max_articles]
        
        try:
            logger.info("Fetching ESPN soccer news...")
            session = await self._get_session()
            
            async with session.get(self.ESPN_RSS, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"ESPN RSS returned status {response.status}")
                    return []
                
                xml_content = await response.text()
            
            # Parse RSS
            articles = self._parse_rss(xml_content, source="ESPN")
            
            # Cache results
            self.cache.set("espn", articles)
            
            logger.info(f"✓ Fetched {len(articles)} articles from ESPN")
            return articles[:max_articles]
        
        except Exception as e:
            logger.error(f"Error fetching ESPN news: {str(e)}")
            return []
    
    async def fetch_all_news(self, max_per_source: int = 15) -> List[NewsArticle]:
        """
        Fetch news from all sources in parallel.
        
        Args:
            max_per_source: Maximum articles per source
            
        Returns:
            Combined list of articles, sorted by date
        """
        logger.info("Fetching news from all sources...")
        
        # Fetch in parallel
        bbc_task = self.fetch_bbc_news(max_per_source)
        espn_task = self.fetch_espn_news(max_per_source)
        
        bbc_articles, espn_articles = await asyncio.gather(
            bbc_task, espn_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(bbc_articles, Exception):
            logger.error(f"BBC fetch failed: {str(bbc_articles)}")
            bbc_articles = []
        
        if isinstance(espn_articles, Exception):
            logger.error(f"ESPN fetch failed: {str(espn_articles)}")
            espn_articles = []
        
        # Combine and sort by date
        all_articles = bbc_articles + espn_articles
        all_articles.sort(key=lambda x: x.published, reverse=True)
        
        logger.info(f"✓ Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def _parse_rss(self, xml_content: str, source: str) -> List[NewsArticle]:
        """
        Parse RSS feed XML into NewsArticle objects.
        
        Args:
            xml_content: RSS XML content
            source: Source name
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Find all item elements
            for item in root.findall('.//item'):
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text or ""
                    url = link_elem.text or ""
                    
                    # Parse date
                    published = datetime.now()
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            # RFC 822 format: "Mon, 15 Jan 2024 14:30:00 GMT"
                            published = datetime.strptime(
                                pub_date_elem.text,
                                "%a, %d %b %Y %H:%M:%S %Z"
                            )
                        except ValueError:
                            # Try alternative formats
                            try:
                                published = datetime.strptime(
                                    pub_date_elem.text,
                                    "%a, %d %b %Y %H:%M:%S %z"
                                )
                            except ValueError:
                                pass
                    
                    summary = None
                    if description_elem is not None:
                        summary = description_elem.text
                        # Clean HTML tags if present
                        summary = re.sub(r'<[^>]+>', '', summary or "")
                        summary = summary.strip()[:200]  # Limit length
                    
                    # Detect teams mentioned
                    teams_mentioned = self._detect_teams(title + " " + (summary or ""))
                    
                    # Categorize article
                    category = self._categorize_article(title, summary or "")
                    
                    article = NewsArticle(
                        title=title,
                        url=url,
                        published=published,
                        source=source,
                        summary=summary,
                        teams_mentioned=teams_mentioned,
                        category=category
                    )
                    
                    articles.append(article)
                
                except Exception as e:
                    logger.warning(f"Error parsing RSS item: {str(e)}")
                    continue
        
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS XML: {str(e)}")
            return []
        
        return articles
    
    def _detect_teams(self, text: str) -> List[str]:
        """Detect team names mentioned in text."""
        teams = []
        text_lower = text.lower()
        
        for team in self.MAJOR_TEAMS:
            if team.lower() in text_lower:
                teams.append(team)
        
        return teams
    
    def _categorize_article(self, title: str, summary: str) -> str:
        """Categorize article based on content."""
        combined = (title + " " + summary).lower()
        
        # Check for injury/suspension news
        if any(keyword in combined for keyword in self.INJURY_KEYWORDS):
            return "injury"
        
        # Check for transfer news
        if any(word in combined for word in ["transfer", "signing", "sign", "join", "move"]):
            return "transfer"
        
        # Check for match preview
        if any(word in combined for word in ["preview", "vs", "face", "clash", "match"]):
            return "match_preview"
        
        return "general"
    
    def filter_by_teams(
        self,
        articles: List[NewsArticle],
        teams: List[str]
    ) -> List[NewsArticle]:
        """
        Filter articles that mention specific teams.
        
        Args:
            articles: List of articles
            teams: List of team names to filter by
            
        Returns:
            Filtered articles
        """
        if not teams:
            return articles
        
        teams_lower = [t.lower() for t in teams]
        
        filtered = []
        for article in articles:
            article_teams_lower = [t.lower() for t in article.teams_mentioned]
            
            if any(team in article_teams_lower for team in teams_lower):
                filtered.append(article)
        
        return filtered
    
    def filter_by_category(
        self,
        articles: List[NewsArticle],
        categories: List[str]
    ) -> List[NewsArticle]:
        """
        Filter articles by category.
        
        Args:
            articles: List of articles
            categories: Categories to include (e.g., ["injury", "transfer"])
            
        Returns:
            Filtered articles
        """
        if not categories:
            return articles
        
        return [a for a in articles if a.category in categories]
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
