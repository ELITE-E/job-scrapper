import asyncio
import logging
from typing import List

from .config import load_config
from .base import ScrapeResult,BaseScrapper
from app.database import  async_session_maker as async_session_factory

logger=logging.getLogger("scraper.orcherstrator")
logger.setLevel(logging.INFO)

async def run_full_scrape(config_path:str="config/scaper_config.yaml")->List[ScrapeResult]:

    config=load_config(config_path)

    results:List[ScrapeResult]=[]

    for site in config.sites:
        if not site.enabled:
            continue

        logger.info(f"Starting scraper for site :{site.name}")

        scraper=BaseScrapper(
            site_config=site,
            global_config=config.global_,
            session_factory=async_session_factory
        )

        result =await scraper.run()
        results.append(result)

        logger.info(f"Finished scraper for site :{site.name} -> {result}")

        await asyncio.sleep(config.global_.delay_between_sites)

    return results