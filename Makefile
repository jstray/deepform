TEST_PATH=$(CURDIR)/tests
CONTAINER=deepform/deepform_learner:latest

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help dialog
	@grep -E '^[a-zA-Z/\._-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: docker-build  ## Run all the unit tests for the project
	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	pytest --verbose --color=yes tests

.PHONY: clean-all
clean-all:
	-rm -r data/cache data/labeled data/tokenized data/training
	-rm data/training.parquet data/doc_index.parquet

.PHONY: docker-build
docker-build: ## Build the docker container
	docker build -t $(CONTAINER) .

.PHONY: docker-stop
docker-stop: ## Stop any running instances of the deepform docker container on this system
	-docker ps | grep $(CONTAINER) | cut -d' ' -f1 | xargs docker stop

.PHONY: docker-shell
docker-shell: docker-stop docker-build ## Launch a shell into a docker container containing the required dependencies and data
	docker run -ti --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

.PHONY: docker-background
docker-background: docker-stop docker-build ## Launch a docker container as a background process.
	docker run -td --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

# This was used by a previous version of our codebase.
# data/training.parquet:
# 	curl https://project-deepform.s3-us-west-1.amazonaws.com/training_data/training.parquet -o data/training.parquet

data/pdfs: data/fcc-data-2020-labeled-manifest.csv ## Downloads all PDFs to local storage. Not usually necessary.
	docker build -t $(CONTAINER) .
	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) python -c "import pandas as pd; print('\n'.join(pd.read_csv('data/fcc-data-2020-labeled-manifest.csv').URL))" | xargs wget -P data/pdfs

# This is the command we used to produce the tokenized data, but it is cached in S3
# data/tokenized: data/pdfs
# 	docker build -t $(CONTAINER) .
# 	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) python -m deepform.data.tokenize_pdfs

data/tokenized:  ## Get document tokens from S3
	curl https://project-deepform.s3-us-west-1.amazonaws.com/training_data/token_data.tar.gz -o data/tokenized.tar.gz
	mkdir -p data/tokenized
	tar xf data/tokenized.tar.gz -C data/tokenized

data/token_frequency.csv: data/tokenized ## Produce token frequency csv file
	docker build -t $(CONTAINER) .
	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -m deepform.data.create_vocabulary

data/doc_index.parquet: data/tokenized data/token_frequency.csv ## Create the training data from the token files and label manifest
	docker build -t $(CONTAINER) .
	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -m deepform.data.add_features data/fcc-data-2020-labeled-manifest.csv

.PHONY: train
train: data/doc_index.parquet data/token_frequency.csv .env docker-build ## Run full model training
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -um deepform.train

.PHONY: test-train
test-train: data/doc_index.parquet data/token_frequency.csv .env docker-build ## Run training on a small sample to test and validate code
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -um deepform.train --len-train=100 --steps-per-epoch=3 --epochs=2 --log-level=DEBUG --use-wandb=0 --use-data-cache=0 --save-model=0 --doc-acc-max-sample-size=20 --render-results-size=3

.PHONY: sweep
sweep: data/doc_index.parquet data/token_frequency.csv .env docker-build ## Run a weights and biases training sweep.
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	./init_sweep.sh

VERSION='stable'
download-model: ## Download a model for use with the inference script
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -m deepform.artifacts --version $(VERSION)
