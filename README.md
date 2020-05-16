# Deepform

An project to extract information from TV and cable political advertising disclosure forms using deep learning, and a challenging journalism-relevant dataset for NLP/AI researchers. This public data is valuable to journalists but locked in PDFs. This work uses models fthat are able to generalize over form types and "learn" how to find four fields:

- Contract number (multipe documents can have the same number as a contract for future air dates is revised)
- Advertiser name (offen the name of a political [comittee](https://www.fec.gov/data/browse-data/?tab=committees) but not always)
- Start and end air dates dates (often known as "flight dates")
- Total amount paid for the ads

This model achieves 90% accuracy extracting total spending from the PDFs in the (held out) test set, which shows that deep learning can generalize surprisingly well to previously unseen form types. 

For a discussion of how the 2019 prototype works, see [this talk](https://www.youtube.com/watch?v=uNN59kJQ7CA).

## Why?

TV stations are required to disclose their sale of political advertising, but there is no requirement that this disclosure is machine readable. Every election, tens of thousands of PDFs are posted to the FCC Public File, available at [https://publicfiles.fcc.gov/](https://publicfiles.fcc.gov/) in hundreds of different formats.

In 2012, ProPublica ran the Free The Files project (you can [read how it worked](https://www.niemanlab.org/2012/12/crowdsourcing-campaign-spending-what-propublica-learned-from-free-the-files/)) and hundreds of volunteers hand-entered information for over 17,000 of these forms. That data drove a bunch of campaign finance [coverage](https://www.propublica.org/series/free-the-files) and is now [available](https://www.propublica.org/datastore/dataset/free-the-files-filing-data) from their data store.

In 2014 Alex Byrnes [automated](https://github.com/alexbyrnes/FCC-Political-Ads) this extraction by hand-coding form layouts. This works for the dozen or so most common form types, but there are hundreds of different PDF layouts in the long tail. Also, we would like a solution that doesn't require so much hand tuning for each election.

This project replicate this data extraction using modern deep learning techniques.

## Running with Docker

The docker container expects access to `source/training.csv`, which needs to be mounted (see command below). It also expects you to have a Weights and Biases API key in a `.env` file at the root of your repo, with the format:

```
WANDB_API_KEY=MY_API_KEY
```

You can find your key through your wanddb.com account. Click your face in the upper right and select `Settings` then scroll down.

To run a sweep, use `docker-compose up --build`. To run something else (e.g., `python train.py`, or even just `bash`), you can use `docker-compose run deepform-learner <command>`.

Note that the training script currently brings all of the training set into memory, and therefore has significant RAM requirements.


## How it works

The easiest fields are contract number and total. This uses a fully connected three-layer network trained on a window of tokens from the data, typically 20-30 tokens. Each token is hashed to an integer mod 1000, then converted to 1-hot representation and embedded into 64 dimensions. This embedding is combined with geometry information (bounding box and page number) and also some hand-crafted "hint" features, such as whether the token matches a regular expression for dollar amounts. For details, see [the talk](https://www.youtube.com/watch?v=uNN59kJQ7CA).

We also incorporate custom "hint" features. For example, the total extractor uses an "amount" feature that is the log of the token value, if the token string is a number.

## Creating the training data

There are multple steps in the data preparation:

- The raw data is in `source/ftf-all-filings.tsv`. This file contains the crowdsourced answers and the PDF url.
- `download-pdfs.py` will read this file and download all the PDFs from DocumentCloud. It takes hours to days. Also, perhaps 10% of these PDFs are no longer on DocumentCloud. In theory they could be re-collected from the FCC.
- `tokenize-pdfs.py` will read each PDF and output a list of tokens and their geometry. Also takes several days to run.
- `create-training-data.py` reads the PDF tokens and matches them against the original data, outputting only documents where the training data is available. Edit this to control which extracted fields appear in the training data.
- `train.py` loads this data, trains a network, and logs the results using [Weights & Biases](https://www.wandb.com/)
- `baseline.py` is a hand coded total extractor for comparison, which achieves 61% accuracy.

## Training data format

The main training data file is `data/training.csv` but it's too big to post in github, so you can download it [here](https://drive.google.com/drive/folders/1bsV4A-8A9B7KZkzdbsBnCGKLMZftV2fQ?usp=sharing).

There is data from 9018 labelled documents. It's formatted as "tokens plus geometry" like this:

```
slug,page,x0,y0,x1,y1,token,gross_amount
473630-116252-0-13442821773323-_-pdf,0,272.613,438.395,301.525,438.439,$275.00,0.62
473630-116252-0-13442821773323-_-pdf,0,410.146,455.811,437.376,455.865,Totals,0.0
473630-116252-0-13442821773323-_-pdf,0,525.84,454.145,530.288,454.189,6,0.0
473630-116252-0-13442821773323-_-pdf,0,556.892,454.145,592.476,454.189,"$1,170.00",1.0
473630-116252-0-13442821773323-_-pdf,0,18.0,480.478,37.998,480.527,Time,0.0
473630-116252-0-13442821773323-_-pdf,0,40.5,480.478,66.51,480.527,Period,0.0
```

The `slug` is a unique document identifier, ultimately from the source TSV. The page number runs from 0 to 1, and the bounding box is in the original PDF coordinate system. The actual token text is reproduced as `token`. The `gross_amount` represents string similarity to the correct answer in the original `gross_amount` column, from 0 to 1. To add other ground-truth fields, edit `create-training-data.py`.

## Code quality and pre-commit hooks

The code is currently automatically formatted with [black](https://black.readthedocs.io/en/stable/), and using [autoflake](https://pypi.org/project/autoflake/) to remove unused imports and [isort](https://timothycrosley.github.io/isort/) to sort them predictably. These tools are configured in `pyproject.toml` and should Just Work&trade; -- you shouldn't have to worry about them at all!

To make this as painless as possible, `.pre-commit-config.yaml` contains rules for automatically running these tools as part of `git commit`. To turn these git pre-commit hook on, you need run `pre-commit install` (after `pip install`ing `black`, `autoflake`, `isort[pyproject]`, and `pre-commit` itself). After that, whenever you run `git commit`, these tools will run and clean up your code so that "dirty" code never gets committed in the first place.

## A research data set

This is a difficult data set that is very relevant to journalism, and improvements in technique will be immediately useful to campaign finance reporting.

The general problem is known as "knowledge base construction" in the research community, and the current state of the art is achieved by multimodal systems such as [Fonduer](https://fonduer.readthedocs.io/en/latest/).

We would love to hear from you! Contact jstray on [twitter](https://twitter.com/jonathanstray) or through his [blog](http://jonathanstray.com).
