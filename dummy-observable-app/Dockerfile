FROM golang:1.26 AS builder

WORKDIR /build-app

COPY go.mod go.sum ./

RUN go mod download

COPY . ./

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build ./cmd/dummy-observable-app/

FROM alpine:latest

COPY --from=builder /build-app/dummy-observable-app /dummy-observable-app

ENTRYPOINT ["/dummy-observable-app"]
