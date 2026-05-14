import asyncio
import logging
import os
from typing import List,Tuple
import time

from jobspy import scrape_jobs
from .config import GlobalConfig,SiteConfig
import pandas as pd

from tenacity import Retrying,stop_after_attempt,wait_exponential,retry_if_exception_type,before_log,after_log

from .schemas import ScrapedJob,ScrapeResult
from .validator import validate_batch
from .categorizer import JobCategorizer,load_categorizer_config
from .rate_limiter import RedisRateLimiter
from .robots_checker import can_scrape_site



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
        
        self.categorizer = JobCategorizer(load_categorizer_config())
        self.retry_config=retry_config
        
        # Phase 9: Initialize rate limiter
        self.rate_limiter = RedisRateLimiter()

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
        total_found_jobs = 0
        total_duplicates = 0
        errors=[]
        start_time = time.time()

        retryer = self._build_retryer()

        for loc_config in self.site_config.location:
            current_location = loc_config.name
            self.logger.info(f"Switching to location : {current_location}")

            for term in self.site_config.search_terms:
                self.logger.info(f"Starting scrape for term | Location : Term:{term} | Location: {current_location}")
    
                try:
                    #1.Fetch

                    #df=self._fetch(term)
                    df=retryer(self._fetch,term,current_location)

                    if df is None or df.empty:
                        self.logger.warning(f"No data returned for term: {term}")
                        continue
                    total_found_jobs+=len(df)

                    #2.Transform
                    transformed_dataframe=self._transform(df)

                    #3.Validate(Reporting)
                    valid_jobs ,report =validate_batch(transformed_dataframe)
                 
                    self.logger.info(report.model_dump())

                    #4.Deduplicate
                    deduped_jobs=await self._deduplicate(valid_jobs)

                    duplicates_for_term = max(len(valid_jobs) - len(deduped_jobs), 0)
                    total_duplicates += duplicates_for_term

                    if not deduped_jobs:
                        #self.logger.info(f"No job after deduplication for term: {term} ")
                        continue

                    #5.Categorize
                    categorized_jobs = self.categorizer.categorize_batch(deduped_jobs)

                    #6.Persist
                    new_count,_=await self._persist(categorized_jobs)
                    total_new_jobs +=new_count

                    self.logger.info(f"{new_count} new jobs stored for term:{term}.")

                except Exception as e:
                  self.logger.exception(f"Error processing term '{term}':{e}")
                #Delay beetween terms
                await asyncio.sleep(self.site_config.delay_beetween_searches)

        return ScrapeResult(
            site_name=self.site_config.name,
            #search_terms=len(self.site_config.search_terms),
            status="success" if not errors else 'partial_failure',
            jobs_found=total_found_jobs,
            jobs_new=total_new_jobs,
            jobs_duplicates=total_duplicates,
            errors=errors,
            duration_seconds= time.time() - start_time,
        )



    def _fetch(self,search_term:str,
               location_str : str)->pd.DataFrame:
        try:
            self.logger.debug(f"Fetching jobs for term: {search_term}")

            # Phase 9: Check rate limit
            rate_limit_allowed = self.rate_limiter.check_rate_limit(
                self.site_config.name,
                self.site_config.rate_limit
            )
            if not rate_limit_allowed:
                wait_time = 60
                self.logger.warning(
                    f"Rate limit exceeded for {self.site_config.name}, "
                    f"waiting {wait_time}s before retry"
                )
                time.sleep(wait_time)
                # Retry after sleep (recursive call for single retry)
                # For production, consider using tenacity with custom waiter

            # Phase 9: Check robots.txt compliance if enabled
            if self.site_config.respect_robots_txt:
                if not can_scrape_site(self.site_config.name, user_agent="JobAggregatorBot"):
                    self.logger.warning(
                        f"robots.txt disallows scraping {self.site_config.name} "
                        f"for search term: {search_term}"
                    )
                    return pd.DataFrame()  # Return empty DataFrame, skip this term

            # Supported countries for Indeed in JobSpy (validated enum)
            INDEED_SUPPORTED_COUNTRIES = {
                "usa", "can", "gbr", "aus", "nld", "fra", "deu", 
                "sgp", "are", "ind", "ire", "nzl", "phl", "mex", "bra"
            }

            kwargs={
                 "site_name":self.site_config.name,
                 "search_term":search_term,
                 "location":location_str,

                 "results_wanted":self.site_config.results_wanted or self.global_config.results_wanted,
                 "hours_old":self.site_config.hours_old or self.global_config.hours_old,
                 "description_format":self.global_config.description_format,

                 "job_type":self.site_config.job_type,
                 "is_remote":self.site_config.is_remote,
                 "proxies":self.site_config.proxies or None,
                 "linkedin_fetch_description":getattr(self.site_config,"linkedin_fetch_description",False),
                 }
            
            # Handle country_indeed with validation
            country_indeed = getattr(self.site_config, "country_indeed", None)
            if country_indeed:
                country_code = country_indeed.lower()
                if country_code in INDEED_SUPPORTED_COUNTRIES:
                    kwargs["country_indeed"] = country_code
                else:
                    self.logger.warning(
                        f"Country '{country_indeed}' not supported by Indeed. "
                        f"Allowed: {INDEED_SUPPORTED_COUNTRIES}. "
                        f"Falling back to location-only search in '{location_str}' "
                        f"(search may be limited without country context)."
                    )
            
            #Filter out None values
            kwargs={k:v for k,v in kwargs.items() if v is not None}      

            self.logger.debug(f"Fetching jobs for term:{search_term}")

            # Phase 9: Wrap scrape_jobs call to detect rate limit hits
            try:
                return scrape_jobs(**kwargs)
            except Exception as scrape_exc:
                # Phase 9: Detect rate limit hit (429 or rate limit text in error)
                error_msg = str(scrape_exc).lower()
                if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                    self._log_rate_limit_hit(scrape_exc, search_term, location_str)
                raise  # Re-raise for tenacity to handle retry

        except Exception as e:
            self.logger.exception(
                f"Fetch failed | site={self.site_config.name} | term={search_term}"
            )

    def _log_rate_limit_hit(self, exception, search_term: str, location_str: str) -> None:
        """
        Phase 9: Log rate limit hit with structured information.

        Args:
            exception: The exception that was raised
            search_term: The search term being scraped
            location_str: The location being scraped
        """
        self.logger.warning(
            f"🔴 RATE LIMIT HIT for site={self.site_config.name}, "
            f"search_term={search_term}, location={location_str}, "
            f"rate_limit_per_min={self.site_config.rate_limit}, "
            f"exception={exception}"
        )

        
    
    def _transform(self,df:pd.DataFrame)->List[ScrapedJob]:
        from .transformer import transform_dataframe#lazy import fix to avoid circular import

        return transform_dataframe(df,self.site_config.name)
    
    async def _deduplicate(self,jobs:List[ScrapedJob])->List[ScrapedJob]:
        from .deduplicator import filter_new_jobs

        async with self.session_factory() as session:
            return await filter_new_jobs(jobs, session)
        
    async def _persist(self,jobs:List[ScrapedJob])->Tuple[int,int]:
        from .persistence import persist_jobs

        async with self.session_factory() as session:
            return await persist_jobs(jobs,session)
        
