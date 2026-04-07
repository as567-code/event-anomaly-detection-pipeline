package com.anomaly;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ScorerApplication {

    private static final Logger log = LoggerFactory.getLogger(ScorerApplication.class);

    public static void main(String[] args) {
        String bootstrapServers = env("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092");
        String inputTopic = env("INPUT_TOPIC", "raw-events");
        String outputTopic = env("OUTPUT_TOPIC", "flagged-anomalies");
        String modelPath = env("MODEL_PATH", "artifacts/model_weights.json");

        log.info("Starting Anomaly Scorer");
        log.info("  Kafka: {}", bootstrapServers);
        log.info("  Input topic: {}", inputTopic);
        log.info("  Output topic: {}", outputTopic);
        log.info("  Model: {}", modelPath);

        try {
            ModelLoader model = new ModelLoader(modelPath);
            KafkaEventConsumer consumer = new KafkaEventConsumer(
                    bootstrapServers, inputTopic, outputTopic, model);

            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                log.info("Shutting down...");
                consumer.stop();
            }));

            consumer.start();
        } catch (Exception e) {
            log.error("Failed to start scorer: {}", e.getMessage(), e);
            System.exit(1);
        }
    }

    private static String env(String key, String defaultValue) {
        String value = System.getenv(key);
        return value != null ? value : defaultValue;
    }
}
