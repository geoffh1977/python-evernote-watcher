# Generate Base Python 2 Image
FROM alpine:3 as base

RUN apk --no-cache -U add python2

# Use Base To Generate Builder Image
FROM base as builder

RUN mkdir /install
WORKDIR /install
COPY app/requirements.txt /requirements.txt
RUN python2 -m ensurepip && \
  pip install --prefix=/install -r /requirements.txt

# Build Final Application Image
FROM base

LABEL maintainer="Geoffrey Harrison <geoffh1977@gmail.com>"
COPY --from=builder /install /usr
COPY app /app/
WORKDIR /app
VOLUME /watch
CMD ["python", "./run.py"]
