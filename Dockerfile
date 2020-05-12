FROM tensorflow/tensorflow:2.2.0-gpu
COPY docker-requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY db/source.py db/source.py
COPY *.py ./
COPY config-defaults.yaml .
CMD python train.py
