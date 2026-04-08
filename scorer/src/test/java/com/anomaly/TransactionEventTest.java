package com.anomaly;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class TransactionEventTest {

    private final ObjectMapper mapper = new ObjectMapper();

    @Test
    void testDeserializeFullPayload() throws Exception {
        String json = """
                {
                  "event_id": 12345,
                  "timestamp": 1700000000000,
                  "amount": 150.5,
                  "hour_of_day": 14.0,
                  "day_of_week": 3.0,
                  "merchant_category": 5.0,
                  "distance_from_home": 12.3,
                  "distance_from_last_txn": 8.1,
                  "transaction_frequency": 2.5,
                  "avg_transaction_amount": 75.0,
                  "time_since_last_txn": 3600.0,
                  "is_online": 1.0,
                  "card_present": 0.0,
                  "merchant_risk_score": 0.7,
                  "account_age_days": 365.0,
                  "num_failed_txns_24h": 0.0,
                  "credit_utilization": 0.45,
                  "amount_zscore": 1.2,
                  "velocity_1h": 5.0,
                  "is_foreign": 0.0
                }
                """;

        TransactionEvent event = mapper.readValue(json, TransactionEvent.class);

        assertEquals(12345, event.getEventId());
        assertEquals(1700000000000L, event.getTimestamp());
        assertEquals(150.5, event.getAmount(), 1e-10);
        assertEquals(14.0, event.getHourOfDay(), 1e-10);
        assertEquals(0.45, event.getCreditUtilization(), 1e-10);
        assertEquals(1.2, event.getAmountZscore(), 1e-10);
    }

    @Test
    void testDeserializeMissingFields() throws Exception {
        String json = """
                {
                  "event_id": 99,
                  "amount": 50.0
                }
                """;

        TransactionEvent event = mapper.readValue(json, TransactionEvent.class);
        assertEquals(99, event.getEventId());
        assertEquals(50.0, event.getAmount(), 1e-10);
        assertEquals(0.0, event.getHourOfDay(), 1e-10);  // default
    }

    @Test
    void testDeserializeUnknownFields() throws Exception {
        String json = """
                {
                  "event_id": 1,
                  "amount": 10.0,
                  "unknown_field": "should_be_ignored"
                }
                """;

        TransactionEvent event = mapper.readValue(json, TransactionEvent.class);
        assertEquals(1, event.getEventId());
        assertEquals(10.0, event.getAmount(), 1e-10);
    }

    @Test
    void testToFeatureArray() throws Exception {
        String json = """
                {
                  "event_id": 1,
                  "amount": 100.0,
                  "hour_of_day": 12.0,
                  "day_of_week": 5.0
                }
                """;

        TransactionEvent event = mapper.readValue(json, TransactionEvent.class);
        String[] featureNames = {"amount", "day_of_week", "hour_of_day"};
        double[] features = event.toFeatureArray(featureNames);

        assertEquals(3, features.length);
        assertEquals(100.0, features[0], 1e-10);
        assertEquals(5.0, features[1], 1e-10);
        assertEquals(12.0, features[2], 1e-10);
    }
}
