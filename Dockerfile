FROM tensorflow/tensorflow:2.2.0-gpu

RUN apt-get update && apt-get install -y \
    libmagickwand-dev ghostscript libgs-dev \
    --no-install-recommends

# This is really stupid but apparently necessary for imagemagick to work correctly.
RUN sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/' /etc/ImageMagick-6/policy.xml

# Copy requirements, but filter out tensorflow (it's 500MB and it comes with our image alreaady).
COPY requirements.txt requirements.txt
RUN pip install $(grep -v tensorflow requirements.txt)

COPY *.py ./
COPY db /db
COPY *.yaml ./
COPY *.sh ./
CMD python train.py
