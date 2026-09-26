FROM python:3.12.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       latexmk \
       texlive-fonts-recommended \
       texlive-latex-recommended \
       texlive-publishers \
       texlive-science \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
CMD ["python", "pipeline.py", "all"]
