import yaml

def load_yaml(path):
    with open(path,"r") as f:
        return yaml.safe_load(f)
    

def expand_categories(scrapper_config_dict,search_terms_dict):
    for site in scrapper_config_dict.get("sites",[]):
        if "categories" in site:
            terms = []

            for cat in site["categories"]:
                terms.extend(
                    search_terms_dict["categories"].get(cat,[])
                )
            site["search_terms"] = list(set(terms))
            
    return scrapper_config_dict