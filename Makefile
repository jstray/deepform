TEST_PATH=$(CURDIR)/tests
CONTAINER=deepform/deepform_learner:latest

.PHONY: test
test:
	pytest --verbose --color=yes $(TEST_PATH)/*

.PHONY: docker-build
docker-build:
	docker build -t $(CONTAINER) .

.PHONY: docker-stop
docker-stop:
	docker ps | grep $(CONTAINER) | cut -d' ' -f1 | xargs docker stop

.PHONY: docker-shell
docker-shell: docker-stop docker-build
	docker run -ti -m 7g --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/pdfs,target=/pdfs \
	--mount type=bind,source=$(CURDIR)/source,target=/source \
	$(CONTAINER)

.PHONY: docker-background
docker-background: docker-stop docker-build
	docker run -td -m 7g --env-file=.env \
	--mount type=bind,source=$(CURDIR)/deepform,target=/deepform \
	--mount type=bind,source=$(CURDIR)/pdfs,target=/pdfs \
	--mount type=bind,source=$(CURDIR)/source,target=/source \
	$(CONTAINER)

.PHONY: sweep
sweep: docker-background
	docker exec -ti $$(docker ps | grep $(CONTAINER) | cut -d' ' -f1 | head -1) ./init_sweep.sh
