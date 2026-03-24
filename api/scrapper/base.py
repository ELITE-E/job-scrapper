import asyncio
import logging
from typing import List,Tuple

from jobspy import scrape_jobs
from .config import GlobalConfig,SiteConfig
import pandas as pd

from tenacity import Retrying,stop_after_attempt,wait_exponential,retry_if_exception_type,before_log,after_log

from .schemas import ScrapedJob
class ScrapeResult:
    def __init__(self,site:str,total_terms:int,total_new:int):
        self.site=site
        self.total_terms=total_terms
        self.total_new=total_new

class BaseScrapper:

    def __init__(
             self,
             site_config:SiteConfig,
             global_config:GlobalConfig,
             session_factory,
             retry_config):
    
        self.site_config=site_config
        self.global_config=global_config
        self.session_factory=session_factory

        self.retry_config=retry_config

        self.logger=logging.getLogger(f"scrapper.{site_config.name}")
        self.logger.setLevel(logging.INFO)

    def _build_retryer(self):
        return Retrying(
            stop=stop_after_attempt(self.retry_config.max_attempts),
            wait=wait_exponential(
                multiplier=self.retry_config.wait_multiplier,
                min=self.retry_config.wait_min,
                max=self.retry_config.wait_max
            ),
            retry=retry_if_exception_type((Exception)),
            before=before_log(self.logger,logging.INFO),
            after=after_log(self.logger,logging.WARNING),
            reraise=True
        )
    

    async def run(self)->ScrapeResult:
        total_new_jobs=0
        errors=[]

        retryer = self._build_retryer()

        for term in self.site_config.search_terms:
            self.logger.info(f"Starting scrape for term:{term}")

            try:
                #Fetch
                #df=self._fetch(term)
                df=retryer(self._fetch,term)

                if df.empty:
                    #self.logger.info(f"No results for term: {term}")
                    continue
                #Transform
                jobs=self.transform(df)

                #Deduplicate
                jobs=await self._deduplicate(jobs)

                if not jobs:
                    #self.logger.info(f"No job after deduplication for term: {term} ")
                    continue

                #Persist
                new_count,_=await self._persist(jobs)
                total_new_jobs +=new_count

                self.logger.info(f"{new_count} new jobs stored for term:{term}.")

            except Exception as e:
                self.logger.exception(f"Error processing term '{term}':{e}")
            #Delay beetween terms
            await asyncio.sleep(self.site_config.delay_beetween_searches)

        return ScrapeResult(
            site=self.site_config.name,
            total_terms=len(self.site_config.search_terms),
            total_new=total_new_jobs
        )



    def _fetch(self,search_term:str)->pd.DataFrame:
        try:
            self.logger.debug(f"Fetching jobs for term: {search_term}")

            kwargs={
                 "site_name":self.site_config.name,
                 "search_term":search_term,
                 "location":self.site_config.location,

                 "results_wanted":self.site_config.results_wanted or self.global_config.results_wanted,
                 "hours_old":self.site_config.hours_old or self.global_config.hours_old,
                 "description_format":self.global_config.description_format,

                 "job_type":self.site_config.job_type,
                 "is_remote":self.site_config.is_remote,
                 "proxies":self.site_config.proxies or None,
                 
                 "country_indeed":self.site_config.country_indeed,
                 "linkedin_fetch_description":self.site_config.linkedin_fetch_description,}
            
            #Filter out None values
            kwargs={k:v for k,v in kwargs.items() if v is not None}      

            #self.logger.debug(f"Fetching with params: {kwargs}")
            self.logger.debug(f"Fetching jobs for term:{search_term}")

            return scrape_jobs(**kwargs)
        except Exception as e:
            self.logger.exception(
                f"Fetch failed | site={self.site_config.name} | term={search_term}"
            )
        
    
    def _transform(self,df:pd.DataFrame)->List[ScrapedJob]:
        from .transformer import transform_jobs#lazy import fix to avoid circular import

        return transform_jobs(df,self.site_config.name)
    
    async def _deduplicate(self,jobs:List[ScrapedJob])->List[ScrapedJob]:
        from .deduplicator import filter_new_jobs

        async with self.session_factory() as session:
            return await filter_new_jobs(session,jobs)
        
    async def _persist(self,jobs:List[ScrapedJob])->Tuple[int,int]:
        from .persistence import persist_jobs

        async with self.session_factory() as session:
            return await persist_jobs(session,jobs)
        
