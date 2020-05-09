FROM tensorflow/tensorflow:2.1.0-py3
COPY source /source
COPY db /db
COPY *.py ./
COPY *.yaml ./
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD python train.py
