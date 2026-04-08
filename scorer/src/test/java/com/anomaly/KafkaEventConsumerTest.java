package com.anomaly;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.FileWriter;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class KafkaEventConsumerTest {

    /**
     * Tests that the model correctly scores a known-fraud event.
     * This is a unit test of the scoring logic, not Kafka connectivity.
     */
    @Test
    void testScoringLogicFraudEvent() throws Exception {
        Path tempDir = Files.createTempDirectory("consumer-test");
        String modelJson = """
                {
                  "version": "test",
                  "n_features": 3,
                  "feature_names": ["amount", "hour_of_day", "day_of_week"],
                  "coefficients": [2.0, 0.5, 0.1],
                  "intercept": -1.0,
                  "threshold": 0.5
                }
                """;
        File modelFile = tempDir.resolve("test_model.json").toFile();
        try (FileWriter w = new FileWriter(modelFile)) { w.write(modelJson); }

        ModelLoader model = new ModelLoader(modelFile.getAbsolutePath());

        // Event with high amount → high fraud score
        String eventJson = """
                {
                  "event_id": 42,
                  "timestamp": 1700000000000,
                  "amount": 5.0,
                  "hour_of_day": 2.0,
                  "day_of_week": 1.0
                }
                """;

        ObjectMapper mapper = new ObjectMapper();
        TransactionEvent event = mapper.readValue(eventJson, TransactionEvent.class);

        double score = model.score(event);
        // z = -1.0 + 2.0*5.0 + 0.5*2.0 + 0.1*1.0 = -1 + 10 + 1 + 0.1 = 10.1
        // sigmoid(10.1) ≈ 0.99996
        assertTrue(score > 0.99);
        assertTrue(model.isFraud(event));
    }

    @Test
    void testScoringLogicLegitEvent() throws Exception {
        Path tempDir = Files.createTempDirectory("consumer-test");
        String modelJson = """
                {
                  "version": "test",
                  "n_features": 3,
                  "feature_names": ["amount", "hour_of_day", "day_of_week"],
                  "coefficients": [2.0, 0.5, 0.1],
                  "intercept": -1.0,
                  "threshold": 0.5
                }
                """;
        File modelFile = tempDir.resolve("test_model.json").toFile();
        try (FileWriter w = new FileWriter(modelFile)) { w.write(modelJson); }

        ModelLoader model = new ModelLoader(modelFile.getAbsolutePath());

        // Event with very negative amount → low fraud score
        String eventJson = """
                {
                  "event_id": 99,
                  "timestamp": 1700000000000,
                  "amount": -5.0,
                  "hour_of_day": -2.0,
                  "day_of_week": -1.0
                }
                """;

        ObjectMapper mapper = new ObjectMapper();
        TransactionEvent event = mapper.readValue(eventJson, TransactionEvent.class);

        double score = model.score(event);
        // z = -1.0 + 2.0*(-5) + 0.5*(-2) + 0.1*(-1) = -1 -10 -1 -0.1 = -12.1
        // sigmoid(-12.1) ≈ 0.00001
        assertTrue(score < 0.01);
        assertFalse(model.isFraud(event));
    }
}
