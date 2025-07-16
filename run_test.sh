#!/bin/bash
set -e
cd docker

# Build and start containers for testing
docker-compose -f docker-compose-tests.yaml up --build
#docker-compose -f docker-compose-tests.yaml up --build --abort-on-container-exit --exit-code-from test-runner

# Save the exit code
EXIT_CODE=$?

# Clean up containers regardless of test outcome
docker-compose -f docker-compose-tests.yaml down

# Exit with the same code as the tests
exit $EXIT_CODE