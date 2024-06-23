from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from src.analysis import DatasetAnalyzer
from src.logger import make_logger
from src.database import DataBase
from src.scraper import WebScraper

log = make_logger("pipeline")

def pipeline_1():
    # Create the WebDriver instance
    scraper = WebScraper()

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

def pipeline_2():
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
    for i, (similar_movie, similarity_score, co_occurrence_count) in enumerate(top_similar, 1):
        log.info(f"{i}. {similar_movie}\tscore: {similarity_score:.4f}\tstrength: {co_occurrence_count}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id ='daily_jobs',
    default_args=default_args,
    description='A simple DAG to run two jobs sequentially',
    schedule_interval='35 19 * * *',  # 7 PM daily
    is_paused_upon_creation=False
)

task1 = PythonOperator(
    task_id='pipeline_1',
    python_callable=pipeline_1,
    dag=dag,
)

task2 = PythonOperator(
    task_id='pipeline_2',
    python_callable=pipeline_2,
    dag=dag,
)

task1 >> task2  # Set task2 to run after task1