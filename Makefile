TEST_PATH=$(CURDIR)/tests
CONTAINER=deepform/deepform_learner:latest

# 'make test' is the default target for make.
.PHONY: test
test: docker-build
	docker run --rm $(CONTAINER) pytest --verbose --color=yes tests

.PHONY: docker-build
docker-build:
	docker build -t $(CONTAINER) .

.PHONY: docker-stop
docker-stop:
	-docker ps | grep $(CONTAINER) | cut -d' ' -f1 | xargs docker stop

.PHONY: docker-shell
docker-shell: docker-stop docker-build
	docker run -ti --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

.PHONY: docker-background
docker-background: docker-stop docker-build
	docker run -td --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/data,target=/data \
	$(CONTAINER)

data/training.parquet:
	curl https://project-deepform.s3-us-west-1.amazonaws.com/training_data/training.parquet -o data/training.parquet

data/doc_index.parquet: data/training.parquet
	docker build -t $(CONTAINER) .
	docker run --rm --mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) python -m deepform.data.add_features

.PHONY: train
train: data/doc_index.parquet .env docker-build
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -um deepform.train

.PHONY: test-train
test-train: data/doc_index.parquet .env docker-build
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	python -um deepform.train --len-train=100 --steps-per-epoch=3 --epochs=2 --log-level=DEBUG --use-wandb=0 --use-data-cache=0 

.PHONY: sweep
sweep: data/doc_index.parquet .env docker-build
	docker run --rm --env-file=.env \
	--mount type=bind,source=$(CURDIR)/data,target=/data $(CONTAINER) \
	./init_sweep.sh
