FROM python:3.11-alpine as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.11-alpine as runtime



# Installing geckodriver
# Get all the prereqs
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub &&\
    wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk &&\
    apk add glibc-2.35-r1.apk
    # wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-bin-2.35-r1.apk &&\
    # apk add glibc-bin-2.35-r1.apk

# And of course we need Firefox if we actually want to *use* GeckoDriver
RUN apk add firefox xvfb
# Then install GeckoDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz &&\
    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz &&\
    rm geckodriver-v0.34.0-linux64.tar.gz &&\
    chmod +x geckodriver &&\
    mv geckodriver /usr/bin/ 
    

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY mondossierweb ./mondossierweb

ENTRYPOINT ["python", "-m", "mondossierweb"]