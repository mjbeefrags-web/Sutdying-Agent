FROM golang:1.24.8-alpine AS build
RUN go install -v github.com/minio/minio@RELEASE.2025-10-15T17-29-55Z

FROM alpine:3.22
RUN apk add --no-cache ca-certificates \
    && addgroup -S minio \
    && adduser -S -G minio -u 10001 minio \
    && mkdir /data \
    && chown minio:minio /data
COPY --from=build /go/bin/minio /usr/local/bin/minio
USER 10001:100
ENTRYPOINT ["/usr/local/bin/minio"]
