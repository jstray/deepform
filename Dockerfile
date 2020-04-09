FROM tensorflow/tensorflow:2.1.0-py3
COPY s2s /s2s
COPY source /source
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /s2s
CMD python s2s_model1.py
