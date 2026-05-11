import asyncio
import logging
from pathlib import Path
from typing import List

from .config import load_yaml
from .base import ScrapeResult,BaseScrapper
from app.database import async_session_maker as async_session_factory

logger=logging.getLogger("scraper.orcherstrator")
logger.setLevel(logging.INFO)

async def run_full_scrape(config_path: str | None = None) -> List[ScrapeResult]:
    if config_path is None:
        resolved_config_path = (
            Path(__file__).resolve().parent / "config" / "scraper_config.yaml"
        )
    else:
        resolved_config_path = Path(config_path)
        if not resolved_config_path.is_absolute():
            resolved_config_path = (
                Path(__file__).resolve().parent / resolved_config_path
            ).resolve()

    config = load_yaml(str(resolved_config_path))

    results:List[ScrapeResult]=[]

    for site in config.sites:
        if not site.enabled:
            continue

        logger.info(f"Starting scraper for site :{site.name}")

        scraper=BaseScrapper(
            site_config=site,
            global_config=config.global_,
            session_factory=async_session_factory,
            retry_config = config.retry,
        )

        result =await scraper.run()
        results.append(result)

        logger.info(f"Finished scraper for site :{site.name} -> {result}")

        await asyncio.sleep(config.global_.delay_between_sites)

    return results