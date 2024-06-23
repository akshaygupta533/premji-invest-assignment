import time

import schedule
from analysis import DatasetAnalyzer
from database import DataBase
from logger import make_logger
from scraper import WebScraper

log = make_logger("pipeline")
# Global variable to track if first pipeline has completed successfully
first_pipeline_completed = False


def scrape_data_and_get_scores():
    global first_pipeline_completed
    # Create the WebDriver instance
    scraper = WebScraper()
    first_pipeline_completed = False

    log.info("Fetching top 5 links from both sources")
    yourstory_links = scraper.get_yourstory_top_5("tata motors")
    finshots_links = scraper.get_finshots_top_5("tata motors")
    scores_1 = []
    for link in yourstory_links:
        log.info(f"Getting score for {link}")
        score = scraper.get_yourstory_article_sentiment_score(url=link)
        scores_1.append({"url": link, "score": score})
    scores_2 = []
    for link in finshots_links:
        log.info(f"Getting score for {link}")
        score = scraper.get_finshots_article_sentiment_score(url=link)
        scores_2.append({"url": link, "score": score})

    # Close the WebDriver instance
    scraper.close_driver()
    log.info("Writing scores to sqlite database")
    # Write the sentiment score to a local sqlite database
    db = DataBase()
    db.insert_data(scores_1 + scores_2)
    db.close_conn()

    first_pipeline_completed = True


def analyse_100k_dataset():

    global first_pipeline_completed
    if first_pipeline_completed:
        log.info("Starting second pipeline")
        analyzer = DatasetAnalyzer()
        # Task 1
        log.info("Doing task 1")
        mean_occupation_age = analyzer.get_occupation_mean_age()  # noqa: F841
        # Task 2
        log.info("Doing task 2")
        top_20_movies = analyzer.get_top_n_movies(20, 35)  # noqa: F841
        # Task 3
        log.info("Doing task 3")
        top_genres_occupation_and_age_group = (  # noqa: F841
            analyzer.get_top_genres_occupation_and_age_group()
        )
        # Task 4
    else:
        log.info(
            "Skipping second pipeline because the first failed or did not complete."
        )


# Schedule the first method to run at 7PM
schedule.every().day.at("10:02").do(scrape_data_and_get_scores)  # pipeline 1
schedule.every().day.at("10:04").do(analyse_100k_dataset)  # pipeline 2

if __name__ == "__main__":
    # Main loop to run the scheduler
    log.info("Scheduling pipelines to run")
    while True:
        schedule.run_pending()
        time.sleep(5)
