FROM python:3.8.3

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.5

# Install dependencies for pdfplumber.
RUN apt-get update && apt-get install -y \
    libmagickwand-dev ghostscript \
    --no-install-recommends

# Allow imagemagick to read and write PDFs.
RUN sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/' \
    /etc/ImageMagick-6/policy.xml

# Get this out of the way early, because it takes so damn long -- we really want to cache it.
RUN pip install "tensorflow==2.2.0"

# Install Poetry and project dependencies.
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry export --dev -f requirements.txt | pip install -r /dev/stdin

COPY . .
RUN poetry install --no-interaction --no-ansi

CMD ["/bin/bash"]
