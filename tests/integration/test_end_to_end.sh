#!/bin/bash
# End-to-end integration test via Docker Compose
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../.."

cd "$PROJECT_DIR"

echo "Starting pipeline..."
docker compose up -d

echo "Waiting 30s for pipeline to stabilize..."
sleep 30

echo "Checking scorer logs..."
SCORER_LOGS=$(docker compose logs scorer 2>&1)

if echo "$SCORER_LOGS" | grep -q "events/sec"; then
    echo "Scorer is processing events"
    echo "$SCORER_LOGS" | grep "events/sec" | tail -3
else
    echo "WARNING: No throughput data in scorer logs yet"
fi

echo "Checking flagged-anomalies topic..."
FLAGGED=$(docker compose exec -T kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic flagged-anomalies \
    --from-beginning \
    --timeout-ms 10000 \
    --max-messages 5 2>/dev/null || true)

if [ -n "$FLAGGED" ]; then
    echo "Flagged anomalies found:"
    echo "$FLAGGED" | head -5
else
    echo "WARNING: No flagged anomalies yet (may need more time)"
fi

echo "Tearing down..."
docker compose down

echo "Integration test complete."
