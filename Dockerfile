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

# Install Poetry and project dependencies.
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY deepform ./
COPY *.yaml ./
COPY init_sweep.sh .
ENTRYPOINT ["/bin/bash"]
