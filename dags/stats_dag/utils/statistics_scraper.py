import requests
import logging
import json
import os
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class StatsScraper():

    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1/event/{}/statistics"
        with open(os.environ.get("PROXIES_PATH"), "r") as f: 
            self.proxies = f.read().split("\n")

    def get_match_stats(self, match_id):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.url = self.base_url.format(match_id)
        while True:
            try:
                proxy = random.choice(self.proxies)
                response = requests.get(self.url, headers=headers, proxies={'http': f"http://{proxy}="})
                if response.status_code == 200:
                    logger.info(f"scraped data using proxy: {proxy}")
                    break
                if response.status_code == 404:
                    logger.error(f"Page not found, maybe the match doesn't start yet")
                    break
            except Exception as e:
                logger.error(f"the following proxy failed: {proxy}")
                response = None 
        return response

    def extract_desired_stats(self, stats_data):
        stats = {}
        if not stats_data:
            logger.error("No data to extract statistics from")
            return {}
        for period_data in stats_data:
            # period_data contains stats of first half, second half, or the entire match
            try:
                groups = period_data["groups"]
            except KeyError as e:
                logger.error(f"KeyError: {e}")
                logger.error(f"while processing statistics: {stats_data}")
            else:
                period_stats = {}
                for stat_group in groups:
                    # group of statistics (possession, shots...)
                    group_stats = {}
                    for stat in stat_group["statisticsItems"]:
                        # in a single group there is divers statistics
                        # for instance, shots group include (shots on target, expected goals, etc)
                        try:
                            stat_name = stat["name"].lower().replace(" ", "_")
                            group_stats[stat_name] = {
                                "home": int(stat["homeValue"]),
                                "away": int(stat["awayValue"])
                            }
                            period_stats[stat_group["groupName"].lower()] = group_stats
                        except KeyError as e:
                            logger.error(f"KeyError: {e}")
                            logger.error(f"while processing statistics: {stats_data}")
                        except Exception as e:
                            logger.error(f"Unexpected error: {e}")
                
                stats[period_data["period"]] = period_stats
        return stats 
    
    def get_stats(self, match_id):
        stats_response = self.get_match_stats(match_id)
        if stats_response.status_code != 200:
            return None
        stats_json = stats_response.json()["statistics"]
        extracted_stats = self.extract_desired_stats(stats_json)
        return extracted_stats
        
        



if __name__ == "__main__":

    os.environ["PROXIES_PATH"] = r"proxies\valid_proxies.txt"
    stats_scraper = StatsScraper()
    stats_json = response = json.loads(open(r"dags\test_stats_dag\statistics.json").read())["statistics"]
    json_data = stats_scraper.extract_stats(stats_json)
