# Base Image
FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm as base

RUN pip install --no-cache "poetry>1.7,<1.8" 
RUN poetry config virtualenvs.create false

WORKDIR /code

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry install --no-dev --no-interaction --no-ansi --no-root -vv \
    && rm -rf /root/.cache/pypoetry

# Dev Container
FROM base as devcontainer

RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    vim \
    wget \
    ffmpeg \
    gcc \
    python3-dev \
    poppler-utils  # ✅ Fixed: Removed extra `\` after last package

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils

# ✅ Clean up to reduce image size
RUN rm -rf /var/lib/apt/lists/* && apt-get clean

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install --update \
    && echo 'complete -C '/usr/local/bin/aws_completer' aws' >> ~/.bashrc \
    && rm -rf awscliv2.zip ./aws

RUN poetry install --all-extras --no-interaction --no-ansi --no-root -vv \
    && rm -rf /root/.cache/pypoetry

WORKDIR /workspace

CMD ["tail", "-f", "/dev/null"]
