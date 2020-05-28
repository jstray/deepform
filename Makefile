TEST_PATH=$(CURDIR)/tests
CONTAINER=deepform/deepform_learner:latest

# 'make test' is the default target for make.
.PHONY: test
test: docker-background
	docker exec -ti $$(docker ps | grep $(CONTAINER) | cut -d' ' -f1 | head -1) \
	pytest --verbose --color=yes tests/*

.PHONY: docker-build
docker-build:
	docker build -t $(CONTAINER) .

.PHONY: docker-stop
docker-stop:
	-docker ps | grep $(CONTAINER) | cut -d' ' -f1 | xargs docker stop

.PHONY: docker-shell
docker-shell: docker-stop docker-build
	docker run -ti --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

.PHONY: docker-background
docker-background: docker-stop docker-build
	docker run -td --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

data/training.csv.gz:
	curl https://project-deepform.s3-us-west-1.amazonaws.com/training_data/training-2012.csv.gz -o data/training.csv.gz

data/training.csv: data/training.csv.gz
	gunzip -c data/training.csv.gz > data/training.csv

# Generates data/doc_index.parquet, but we don't want to run it automatically.
.PHONY: data
data: data/training.csv docker-background
	docker exec -ti $$(docker ps | grep $(CONTAINER) | cut -d' ' -f1 | head -1) \
	python -um deepform.convert_to_parquet data/training.csv data/parquet

.PHONY: train
train: data/doc_index.parquet docker-background
	docker exec -ti $$(docker ps | grep $(CONTAINER) | cut -d' ' -f1 | head -1) \
	python -um deepform.train

.PHONY: sweep
sweep: data/doc_index.parquet docker-background
	docker exec -ti $$(docker ps | grep $(CONTAINER) | cut -d' ' -f1 | head -1) \
	./init_sweep.sh
