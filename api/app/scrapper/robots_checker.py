"""
robots.txt compliance checking for responsible scraping.
"""

import logging
import time
import urllib.robotparser
from functools import lru_cache
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def _get_robot_parser(base_url: str) -> urllib.robotparser.RobotFileParser:
    """
    Get and cache a RobotFileParser for a given base URL.

    Args:
        base_url: Base URL (scheme + netloc, e.g., 'https://indeed.com')

    Returns:
        RobotFileParser instance for the base URL
    """
    robots_url = f"{base_url}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        logger.debug(f"Loaded robots.txt from {robots_url}")
    except Exception as e:
        logger.warning(f"Could not load robots.txt from {robots_url}: {e}")
    return rp


def can_scrape(site_url: str, user_agent: str = "JobAggregatorBot") -> bool:
    """
    Check if a URL can be scraped according to robots.txt.

    Respects robots.txt rules and optional crawl delays.

    Args:
        site_url: Full URL to check (e.g., 'https://indeed.com/jobs')
        user_agent: User-Agent string (used in robots.txt rules)

    Returns:
        True if scraping is allowed, False if disallowed by robots.txt
    """
    try:
        parsed = urlparse(site_url)

        if not parsed.scheme or not parsed.netloc:
            logger.error(f"Invalid site URL: {site_url}")
            return False

        base_url = f"{parsed.scheme}://{parsed.netloc}"
        rp = _get_robot_parser(base_url)

        # Check if User-Agent is allowed to fetch this URL
        allowed = rp.can_fetch(user_agent, site_url)

        if not allowed:
            logger.warning(f"robots.txt disallows scraping {site_url} for {user_agent}")
            return False

        # Optionally respect crawl delay (non-blocking advisory)
        try:
            crawl_delay = rp.crawl_delay(user_agent)
            if crawl_delay:
                logger.debug(f"robots.txt suggests crawl delay: {crawl_delay}s for {user_agent}")
                # Could implement sleep here if desired; currently just log
        except Exception as e:
            logger.debug(f"Could not get crawl delay: {e}")

        logger.debug(f"robots.txt allows scraping {site_url}")
        return True

    except Exception as e:
        logger.error(f"Error checking robots.txt for {site_url}: {e}")
        # Fail open: allow scraping if there's an error parsing robots.txt
        return True


def get_base_url(site_name: str) -> str:
    """
    Map site name to base URL for robots.txt checking.

    Args:
        site_name: Site name (e.g., 'indeed', 'linkedin', 'zip_recruiter')

    Returns:
        Base URL for the site
    """
    base_urls = {
        "indeed": "https://indeed.com",
        "linkedin": "https://linkedin.com",
        "zip_recruiter": "https://www.ziprecruiter.com",
        "glassdoor": "https://glassdoor.com",
        "google": "https://www.google.com",
        "bayt": "https://bayt.com",
        "naukri": "https://naukri.com",
        "bdjobs": "https://bdjobs.com",
    }
    return base_urls.get(site_name, f"https://{site_name}.com")


def can_scrape_site(site_name: str, user_agent: str = "JobAggregatorBot") -> bool:
    """
    Check if a job site can be scraped according to its robots.txt.

    Args:
        site_name: Name of the job site
        user_agent: User-Agent string

    Returns:
        True if allowed, False otherwise
    """
    base_url = get_base_url(site_name)
    # Check robots.txt for base URL (not a specific path)
    return can_scrape(base_url, user_agent)
