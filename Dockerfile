FROM python:3.10-slim as builder

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt --no-cache-dir

FROM python:3.10-slim AS runner
WORKDIR /opt/webapp
RUN groupadd djangoGroup \
    && useradd -g djangoGroup -m -d /opt/webapp djangoUser \
    && chown djangoUser:djangoGroup -R /opt/webapp
USER djangoUser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=djangoUser:djangoGroup . /opt/webapp