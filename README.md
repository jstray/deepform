# Deepform

![Python build](https://github.com/project-deepform/deepform/workflows/Python%20application/badge.svg)
![Docker image](https://github.com/project-deepform/deepform/workflows/Docker%20Image%20CI/badge.svg)

An project to extract information from TV and cable political advertising disclosure forms using deep learning, and a challenging journalism-relevant dataset for NLP/AI researchers. This public data is valuable to journalists but locked in PDFs. This work uses models fthat are able to generalize over form types and "learn" how to find four fields:

- Contract number (multipe documents can have the same number as a contract for future air dates is revised)
- Advertiser name (offen the name of a political [comittee](https://www.fec.gov/data/browse-data/?tab=committees) but not always)
- Start and end air dates dates (often known as "flight dates")
- Total amount paid for the ads

This model achieves 90% accuracy extracting total spending from the PDFs in the (held out) test set, which shows that deep learning can generalize surprisingly well to previously unseen form types.

For a discussion of how the 2019 prototype works, see [this post](http://jonathanstray.com/extracting-campaign-finance-data-from-gnarly-pdfs-using-deep-learning).

## Why?

TV stations are required to disclose their sale of political advertising, but there is no requirement that this disclosure is machine readable. Every election, tens of thousands of PDFs are posted to the FCC Public File, available at [https://publicfiles.fcc.gov/](https://publicfiles.fcc.gov/) in hundreds of different formats.

In 2012, ProPublica ran the Free The Files project (you can [read how it worked](https://www.niemanlab.org/2012/12/crowdsourcing-campaign-spending-what-propublica-learned-from-free-the-files/)) and hundreds of volunteers hand-entered information for over 17,000 of these forms. That data drove a bunch of campaign finance [coverage](https://www.propublica.org/series/free-the-files) and is now [available](https://www.propublica.org/datastore/dataset/free-the-files-filing-data) from their data store.

In 2014 Alex Byrnes [automated](https://github.com/alexbyrnes/FCC-Political-Ads) this extraction by hand-coding form layouts. This works for the dozen or so most common form types, but there are hundreds of different PDF layouts in the long tail. Also, we would like a solution that doesn't require so much hand tuning for each election.

This project replicate this data extraction using modern deep learning techniques.

## Running

The project is primarily intended to be run with [Docker](https://www.docker.com/products/docker-desktop), which eases issues with Python virtual environments, but it can also be run locally -- this is easiest to do with [Poetry](https://python-poetry.org/).

### Docker

To use Docker, you'll have to be running the daemon, which you can find and install from https://www.docker.com/products/docker-desktop. Fortunately, that's _all_ you need.

The project has a `Makefile` that covers most of the things you might want to do with the project. Run:

- `make test` to run all the unit tests for the project
- `make docker-shell` will spin up a container and drop you into a bash shell after mounting the `deepform` folder of code so that commands that you run there reflect the code as you are editing it.
- `make train` runs `deepform/train.py` with the default configuration. If it needs to it will download and preprocess the data it needs to train on.
- `make test-train` runs the same training loop on the same data, but with very strongly reduced settings (just a few documents for a few steps) so that it can be used to check that it actually works.
- `make sweep` runs a hyperparameter sweep with Weights & Biases, using the configuration in `sweep.yaml`

Some of these commands require an `.env` file located at the root of the project directory. It will need to have an API key you can get from your [settings](https://app.wandb.ai/settings) page at Weights & Biases. The file should look like:

```
WANDB_API_KEY=MY_API_KEY
```

If you don't want to use Weights & Biases, you can turn it off by setting `use_wandb=0`. You'll still need an `.env` file, but it can be empty.

#### Caveats

Training the model brings all the training data into memory and is quite RAM-intensive. On my 16GB machine, Docker will terminate with an out-of-memory exception if I train on more than ~6000 documents. If I train locally, it uses all my ram but will keep going after it exceeds it, slowing down and paging as it needs to. So with Docker, either train on a subset of the data (use a smaller `len_train`) or use a machine with a lot of RAM.

### Poetry - dependency management and running locally

Deepform manages its dependencies with `Poetry`, which you only need if you want to run it locally or alter the project dependencies.

You can install Poetry using any of the methods listed in their [documentation](https://python-poetry.org/docs/#installation).

If you want to run Deepform locally:

- run `poetry install` to install the deepform package and all of it's dependencies into a fresh virtual environment
- enter this environment with `poetry shell`
- or run a one-off command with `poetry run <command>`

Since deepform is an installed package inside the virtual environment Poetry creates, run the code as modules, e.g. `python -m deepform.train` instead of `python deepform/train.py` -- this insures that imports and relative paths work the way they should.

To update project dependencies:

- `poetry add <package>` adds a new python package as a requirement
- `poetry remove <package>` removes a package that's no longer needed
- `poetry update` updates all the dependencies to their latest non-conflicting versions

These three commands alter `pyproject.toml` and `poetry.lock`, which should be committed to git. Using them ensures that our project has reproducible builds.

## How it works

The easiest fields are contract number and total. This uses a fully connected three-layer network trained on a window of tokens from the data, typically 20-30 tokens. Each token is hashed to an integer mod 1000, then converted to 1-hot representation and embedded into 64 dimensions. This embedding is combined with geometry information (bounding box and page number) and also some hand-crafted "hint" features, such as whether the token matches a regular expression for dollar amounts. For details, see [the talk](https://www.youtube.com/watch?v=uNN59kJQ7CA).

We also incorporate custom "hint" features. For example, the total extractor uses an "amount" feature that is the log of the token value, if the token string is a number.

## Creating the training data

The training data is a combination of the raw PDFs from 2012 and 2014, and [ProPublica data from 2012](https://www.propublica.org/datastore/dataset/free-the-files-filing-data) and [Alex Byrne's data from 2014](https://github.com/alexbyrnes/FCC-Political-Ads). There are multple steps in the data preparation:

- The raw data is in `source/ftf-all-filings.tsv`. This file contains the crowdsourced answers and the PDF url.
- `download-pdfs.py` will read this file and download all the (currently 2012 only) PDFs from DocumentCloud. It takes hours to days. Also, perhaps 10% of these PDFs are no longer on DocumentCloud. In theory they could be re-collected from the FCC.
- `tokenize-pdfs.py` will read each PDF and output a list of tokens and their geometry. Also takes several days to run.
- `create-training-data.py` reads the PDF tokens and matches them against the original data, outputting only documents where the training data is available. Edit this to control which extracted fields appear in the training data.
- `train.py` loads this data, trains a network that extracts the total, and logs the results using [Weights & Biases](https://www.wandb.com/)
- `baseline.py` is a hand coded total extractor for comparison, which achieves 61% accuracy.

## Training data for 2020
Pdfs for the 2020 political ads and associated metadata were uploaded to [Overview](https://www.overviewdocs.com/) and a sample of 1000 were randomly chosen for training. To collect the pdfs, the file names were pulled from the [FCC API OPIF file search](https://publicfiles.fcc.gov/developer/) using the search terms: order, contract, invoice, and receipt. The search was run with filters for campaign year set to 2020 and source service code set to TV. 

The FCC API search also returns the source service code (entity type, i.e. TV, cable), entity id, callsign, political file type (political ad or non-candidate issue ad), office type (presidential, senate, etc), nielsen dma rank (tv market area), network affiliation, and the time stamps for when the ad was created and last modified were pulled. These were added to the overview document set along with the search term, URL for the FCC download, and the date of the search.

To process the pdfs, the text was first extracted and if there were less than 10 words present OCR was performed using the following steps:

 - Convert pdf to a series of images
 - Determine angle of each page and rotate if needed
 - Use tesseract to OCR each image
 - Upload processed pdf to an S3 bucket and add URL to overview
 - Upload additional metadata on whether OCR was needed, the original angle of each page, and any errors that occurred during the OCR process

## Training data format

The main training data file is `data/training.csv` but it's too big to post in github.
You can find the prototype version of the 2012 data (does not include any PDFS that needed OCR), and also the 25gb of raw PDFs from 2012, in this [folder](https://drive.google.com/drive/folders/1bsV4A-8A9B7KZkzdbsBnCGKLMZftV2fQ?usp=sharing).

It's formatted as "tokens plus geometry" like this:

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

The code is currently automatically formatted with [black](https://black.readthedocs.io/en/stable/), uses [autoflake](https://pypi.org/project/autoflake/) to remove unused imports, [isort](https://timothycrosley.github.io/isort/) to sort them, and [flake8](https://flake8.pycqa.org/en/latest/) to check for PEP8 violations. These tools are configured in `pyproject.toml` and should Just Work&trade; -- you shouldn't have to worry about them at all once you install them.

To make this as painless as possible, `.pre-commit-config.yaml` contains rules for automatically running these tools as part of `git commit`. To turn these git pre-commit hook on, you need run `pre-commit install` (after installing it and the above libraries with Poetry or pip). After that, whenever you run `git commit`, these tools will run and clean up your code so that "dirty" code never gets committed in the first place.

GitHub runs a "python build" Action whenever you push new code to a branch (configured in [python-app.yml](https://github.com/project-deepform/deepform/blob/master/.github/workflows/python-app.yml)). This also runs `black`, `flake8`, and `pytest`, so it's best to just make sure things pass locally before pushing to GitHub.

## A research data set

This is a difficult data set that is very relevant to journalism, and improvements in technique will be immediately useful to campaign finance reporting.

The general problem is known as "knowledge base construction" in the research community, and the current state of the art is achieved by multimodal systems such as [Fonduer](https://fonduer.readthedocs.io/en/latest/).

We would love to hear from you! Contact jstray on [twitter](https://twitter.com/jonathanstray) or through his [blog](http://jonathanstray.com).
