import yaml 
import re
from pathlib import Path
from pydantic import List,Tuple,Any,Dict
from .schemas import CategorizerConfig,ScrapedJob

def load_categorizer_config(path:str ="config/categories.yaml")->CategorizerConfig:
   base_dir = Path(__file__).resolve().parent.parent
   full_path = base_dir /path

   with open(full_path,"r") as f:
      data = yaml.safe_load(f)

      return CategorizerConfig(**data)
   
class JobCategorizer():
   def __init__(self,config:CategorizerConfig):
      self.config = config
      self.settings = config.settings

      #Slug
      self.category_patterns : Dict[str,List[Tuple[re.Pattern,float]]] = {}

      for category in config.categories:
         patterns = []

         for kw in category.keywords:
            pattern = re.compile(
               r"\b" + re.escape(kw.term.lower()) + r"\b"
            )
            patterns.append((pattern,kw.weight))
         self.category_patterns[category.slug] = patterns

   def categorize(self,job:ScrapedJob)->str:
      title_lower = (job.title or "").lower()
      description_lower = (job.description or "").lower()

      scores: Dict[str ,float] = {}

      for slug,patterns in self.category_patterns.items():
         score = 0.0

      for pattern,weight in patterns:
         #Titel match 
         if pattern.search(title_lower):
            score+=weight * self.settings.title_weight_multiplier

        #Description match
         if pattern.search(description_lower):
            score+=weight 

         scores[slug] = score

         #Find best category
         best_slug = None
         best_score = 0.0

         for slug,score in scores.items():
            if score > best_score:
               best_score = score
               best_slug = slug
         #Apply threshold
         if best_slug and best_score >= self.settings.min_score_threshold:
            return best_slug
         
         return self.settings.default_category
      
   def categorize_batch(self,jobs:List[ScrapedJob]) ->List[ScrapedJob]:
      for job in jobs:
         job.category_slug = self.categorize(job)

      return jobs 
