package com.anomaly;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

public class KafkaEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(KafkaEventConsumer.class);

    private final KafkaConsumer<String, String> consumer;
    private final KafkaProducer<String, String> producer;
    private final ModelLoader model;
    private final ObjectMapper mapper;
    private final String inputTopic;
    private final String outputTopic;
    private volatile boolean running = true;

    public KafkaEventConsumer(String bootstrapServers, String inputTopic, String outputTopic, ModelLoader model) {
        this.inputTopic = inputTopic;
        this.outputTopic = outputTopic;
        this.model = model;
        this.mapper = new ObjectMapper();

        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "anomaly-scorer");
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        consumerProps.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
        consumerProps.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 50000);
        consumerProps.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 200);

        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        producerProps.put(ProducerConfig.LINGER_MS_CONFIG, 5);

        this.consumer = new KafkaConsumer<>(consumerProps);
        this.producer = new KafkaProducer<>(producerProps);
    }

    public void start() {
        consumer.subscribe(Collections.singletonList(inputTopic));
        log.info("Subscribed to topic '{}', publishing anomalies to '{}'", inputTopic, outputTopic);

        long totalProcessed = 0;
        long totalFlagged = 0;
        long startTime = System.currentTimeMillis();
        long lastLogTime = startTime;

        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

            for (ConsumerRecord<String, String> record : records) {
                try {
                    TransactionEvent event = mapper.readValue(record.value(), TransactionEvent.class);
                    double fraudScore = model.score(event);

                    if (model.isFraud(event)) {
                        Map<String, Object> flagged = new HashMap<>();
                        flagged.put("event_id", event.getEventId());
                        flagged.put("timestamp", event.getTimestamp());
                        flagged.put("fraud_score", fraudScore);
                        flagged.put("amount", event.getAmount());

                        String json = mapper.writeValueAsString(flagged);
                        producer.send(new ProducerRecord<>(outputTopic, json));
                        totalFlagged++;
                    }

                    totalProcessed++;
                } catch (Exception e) {
                    log.warn("Failed to process record: {}", e.getMessage());
                }
            }

            long now = System.currentTimeMillis();
            if (now - lastLogTime >= 10000 && totalProcessed > 0) {
                double elapsed = (now - startTime) / 1000.0;
                double rate = totalProcessed / elapsed;
                log.info("Processed {} events ({} events/sec), flagged {} anomalies",
                        totalProcessed, String.format("%.0f", rate), totalFlagged);
                lastLogTime = now;
            }
        }
    }

    public void stop() {
        running = false;
        consumer.close();
        producer.close();
    }

    // Visible for testing
    long processRecord(String json) throws Exception {
        TransactionEvent event = mapper.readValue(json, TransactionEvent.class);
        double fraudScore = model.score(event);
        if (model.isFraud(event)) {
            Map<String, Object> flagged = new HashMap<>();
            flagged.put("event_id", event.getEventId());
            flagged.put("fraud_score", fraudScore);
            String out = mapper.writeValueAsString(flagged);
            producer.send(new ProducerRecord<>(outputTopic, out));
            return event.getEventId();
        }
        return -1;
    }
}
