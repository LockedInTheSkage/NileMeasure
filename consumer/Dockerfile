FROM golang:1.21-alpine as builder

WORKDIR /app

# Copy source code and module files
COPY *.go .
COPY go.mod .
COPY go.sum* ./ 

# Initialize modules and fetch dependencies
RUN go mod tidy && go mod download -x

# Build the application
RUN go build -o consumer .

# Use a small alpine image for the final container
FROM alpine:3.19

WORKDIR /app

# Create a data directory for alert state storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy the binary from the builder stage
COPY --from=builder /app/consumer .

# Run the application
CMD ["./consumer"]
