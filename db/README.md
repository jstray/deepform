# Database

Tokenized data is stored in a Mariadb database. To run Mariadb locally:

## Setup

Although we're running Mariadb in a Docker container, you'll probably want the MySQL command line utilities. If you don't already have these, you can install them with `brew install mysql` in OS X.

To run the Docker container, run the following command optionally changing the password set in `.env`.

```
docker run --name mariadb -v data:/var/lib/mysql -v conf:/etc/mysql/conf.d --env-file .env -p=3306:3306 -d mariadb:10.5.1
```

The data loading scripts are useful for loading the example data into the database and assume execution from this directory. The scripts also assume the existence of the files `source/ftf-all-filings.tsv` and `data/training.csv` in this repository.

```
mysql -uroot -p --protocol tcp < scripts/create_schema.sql
mysql -uroot -p --protocol tcp deepform < scripts/load_document_data.sql
mysql -uroot -p --protocol tcp deepform < scripts/load_token_data.sql
```

## Further notes

When running a Mariadb database in Docker, you'll need to specify the protocol to use when interacting with the database like so:

```
mysql -uroot -p -e "SHOW CREATE DATABASE deepform;" --protocol tcp deepform
```

The `mysql` command defaults to using unix file sockets if no protocol is specified, and won't connect to the database.
