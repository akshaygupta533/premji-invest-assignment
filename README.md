# premji-invest-assignment

This repo contains work for the take home assignment from premji invest. To start the Airflow DAG for running the pipelines, just modify the env variables in `startup.sh` and run:

```
$ bash startup.sh
```
## CI/CD

The repo has github workflows setup to check for linting errors in the code. The workflow runs on every PR to main branch.

## Mock APIs

I have implemented mock apis at `dummy_apis/` and set up a fastAPI server for them. There are 2 mock apis

* `get-senti-score/`: For getting sentiment value for a text
* `send-alert`: For sending alert messages on pipeline failures

## Evidence of working

This section includes screenshots/GIFs to demonstrate the working of the pipelines.

### Startup