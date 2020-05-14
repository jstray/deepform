FROM tensorflow/tensorflow:2.2.0-gpu

RUN apt-get update && apt-get install -y \
    libmagickwand-dev imagemagick --no-install-recommends

COPY docker-requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY *.py ./
COPY db /db
COPY *.yaml ./
CMD python train.py
