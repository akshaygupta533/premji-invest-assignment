from datetime import datetime, time, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.time_sensor import TimeSensor
from src.analysis import DatasetAnalyzer
from src.api import send_alert
from src.database import DataBase
from src.logger import make_logger
from src.scraper import WebScraper

log = make_logger("pipeline")


def pipeline_1():
    try:
        # Create the WebDriver instance
        scraper = WebScraper()
        tickers = ["tata motors", "hdfc"]
        scores = []
        for ticker in tickers:
            log.info("Fetching top 5 links from both sources")
            yourstory_links = scraper.get_yourstory_top_5(ticker)
            finshots_links = scraper.get_finshots_top_5(ticker)
            for link in yourstory_links:
                log.info(f"Getting score for {link}")
                score = scraper.get_yourstory_article_sentiment_score(
                    url=link
                )  # calls the mock api
                scores.append({"ticker": ticker, "url": link, "score": score})
            for link in finshots_links:
                log.info(f"Getting score for {link}")
                score = scraper.get_finshots_article_sentiment_score(
                    url=link
                )  # calls the mock api
                scores.append({"ticker": ticker, "url": link, "score": score})

        # Close the WebDriver instance
        scraper.close_driver()

        log.info("Writing scores to sqlite database")
        # Write the sentiment score to a local sqlite database
        db = DataBase()
        db.insert_data(scores)
        db.close_conn()
    except Exception as e:
        log.error("Pipeline 1 failed")
        send_alert("Pipeline 1 failed\nError: " + str(e))
        raise e


def pipeline_2():
    try:
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
        log.info("Running task 4")
        movie_id = 1
        title, top_similar = analyzer.find_similar_movies(movie_id)

        log.info(f"Top {len(top_similar)} similar movies for movie {title}:")
        for i, (similar_movie, similarity_score, co_occurrence_count) in enumerate(
            top_similar, 1
        ):
            log.info(
                f"{i}. {similar_movie}\tscore: {similarity_score:.4f}\tstrength: {co_occurrence_count}"
            )
    except Exception as e:
        log.error("Pipeline 2 failed")
        send_alert("Pipeline 2 failed\nError: " + str(e))
        raise e


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 6, 22),
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}

dag = DAG(
    dag_id="daily_jobs",
    default_args=default_args,
    description="A simple DAG to run two jobs sequentially",
    schedule_interval="19 14 * * *",  # 7 PM daily
    is_paused_upon_creation=False,
)

task1 = PythonOperator(
    task_id="pipeline_1",
    python_callable=pipeline_1,
    dag=dag,
)

wait_until_8pm = TimeSensor(
    task_id="wait_until_8pm",
    target_time=time(14, 17),  # 8PM
    poke_interval=60,  # Check every 60 seconds
)

task2 = PythonOperator(
    task_id="pipeline_2",
    python_callable=pipeline_2,
    dag=dag,
)

task1 >> wait_until_8pm >> task2  # Set task2 to run after task1
