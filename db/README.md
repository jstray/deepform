# Database

Tokenized data is stored in a Mariadb database. To run Mariadb locally:

## Setup

Although we're running Mariadb in a Docker container, you'll probably want the MySQL command line utilities. If you don't already have these, you can install them with `brew install mysql` in OS X.

To run the Docker container, run the following command optionally changing the password set in `.env`.

```
docker run --name mariadb -v conf:/etc/mysql/conf.d --env-file .env -p=3306:3306 -d mariadb:10.5.1
```

You may want to change the root password in `.env`.

The data loading scripts are useful for loading the example data into the database and assume execution from this directory. The scripts also assume the existence of the files `source/ftf-all-filings.tsv` and `data/training.csv` in this repository.
