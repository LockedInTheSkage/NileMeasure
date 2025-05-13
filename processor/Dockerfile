FROM golang:1.21-alpine as builder

WORKDIR /app

# Copy source code and module files
COPY *.go .
COPY go.mod .
COPY go.sum* ./ 

# Initialize modules and fetch dependencies
RUN go mod tidy && go mod download -x

# Build the application
RUN go build -o processor .

# Use a small alpine image for the final container
FROM alpine:3.19

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/processor .

# Run the application
CMD ["./processor"]
