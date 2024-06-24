import os
from datetime import datetime, time, timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator
# fmt: off
from airflow.operators.python_operator import (BranchPythonOperator,
                                               PythonOperator)
# fmt: on
from airflow.sensors.time_sensor import TimeSensor
from pytz import timezone
from src.analysis import DatasetAnalyzer
from src.api import send_alert
from src.database import DataBase
from src.logger import make_logger
from src.scraper import WebScraper

log = make_logger("pipeline")

TICKER_LIST = os.environ["TICKER_LIST"]
FIRST_PIPELINE_TIME = os.environ["FIRST_PIPELINE_TIME"]
SECOND_PIPELINE_TIME = os.environ["SECOND_PIPELINE_TIME"]
MOVIE_ID = int(os.environ["MOVIE_ID"])


def pipeline_1():
    try:
        # Create the WebDriver instance
        scraper = WebScraper()
        tickers = TICKER_LIST.split("|")
        scores = []
        for ticker in tickers:
            log.info("Fetching top 5 links from both sources")
            # Get article links from both sources for the ticker
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
        send_alert("Pipeline 1 failed\nError: " + str(e))  # call the mock alert api
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
        title, top_similar = analyzer.find_similar_movies(MOVIE_ID)

        log.info(f"Top {len(top_similar)} similar movies for movie {title}:")
        for i, (similar_movie, similarity_score, co_occurrence_count) in enumerate(
            top_similar, 1
        ):
            log.info(
                f"{i}. {similar_movie}\tscore: {similarity_score:.4f}\tstrength: {co_occurrence_count}"
            )
    except Exception as e:
        log.error("Pipeline 2 failed")
        send_alert("Pipeline 2 failed\nError: " + str(e))  # call the mock alert api
        raise e


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 6, 22),
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}
hour, minute = FIRST_PIPELINE_TIME.split(":")
dag = DAG(
    dag_id="daily_jobs",
    default_args=default_args,
    description="Pipelines DAG",
    schedule_interval=f"{minute} {hour} * * *",  # Run schedule for the first pipeline
    is_paused_upon_creation=False,
)

task1 = PythonOperator(
    task_id="pipeline_1",
    python_callable=pipeline_1,
    dag=dag,
)


def branch_method(**context):
    task1_end_time = datetime.now(timezone("Asia/Kolkata"))

    # Define the cutoff time
    hour, minute = SECOND_PIPELINE_TIME.split(":")
    # Decide to skip pipeline 2 if pipeline 1 finishes after cutoff
    if task1_end_time.time() < time(int(hour), int(minute)):
        return "wait_until"
    else:
        return "skip_task2"


branch_task = BranchPythonOperator(
    task_id="check_task1_completion_time",
    python_callable=branch_method,
    provide_context=True,
    dag=dag,
)

hour, minute = SECOND_PIPELINE_TIME.split(":")

wait_until = TimeSensor(
    task_id="wait_until",
    target_time=time(int(hour), int(minute)),
    poke_interval=60,  # Check every 60 seconds
    dag=dag,
)  # dag task which suspends following tasks until the target time

skip_task2 = DummyOperator(task_id="skip_task2", dag=dag)

task2 = PythonOperator(
    task_id="pipeline_2",
    python_callable=pipeline_2,
    dag=dag,
)

# Set DAG dependencies
task1 >> branch_task
branch_task >> [wait_until, skip_task2]
wait_until >> task2
