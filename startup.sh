export DATASET_PATH="dags/dataset"
export DUMMY_API_URL="http://host.docker.internal:80"
export DB_FILE="dags/database.db"
export SELENIUM_SERVER_URL="http://host.docker.internal:4444/wd/hub"
export YOURSTORY_SEARCH_URL="https://yourstory.com/search?q=KEYWORD&page=1"
export FINSHOTS_URL="https://finshots.in"
export TICKER_LIST="hyundai|tata motors"
export FIRST_PIPELINE_TIME="19:00" 
export SECOND_PIPELINE_TIME="20:00"
export MOVIE_ID="1" #Movie id for pipeline 2, task 4

docker compose up