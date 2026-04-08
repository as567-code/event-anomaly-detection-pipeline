package com.anomaly;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class ModelLoaderTest {

    private static ModelLoader modelNoScaler;
    private static ModelLoader modelWithScaler;
    private static Path tempDir;

    @BeforeAll
    static void setUp() throws IOException {
        tempDir = Files.createTempDirectory("model-test");

        // Model without scaler
        String noScalerJson = """
                {
                  "version": "v1",
                  "n_features": 3,
                  "feature_names": ["amount", "hour_of_day", "day_of_week"],
                  "coefficients": [0.5, -0.3, 0.2],
                  "intercept": -1.0,
                  "threshold": 0.5
                }
                """;
        File f1 = tempDir.resolve("model_no_scaler.json").toFile();
        try (FileWriter w = new FileWriter(f1)) { w.write(noScalerJson); }
        modelNoScaler = new ModelLoader(f1.getAbsolutePath());

        // Model with scaler
        String scalerJson = """
                {
                  "version": "v2",
                  "n_features": 3,
                  "feature_names": ["amount", "hour_of_day", "day_of_week"],
                  "coefficients": [1.0, -0.5, 0.3],
                  "intercept": 0.0,
                  "threshold": 0.5,
                  "scaler": {
                    "mean": [100.0, 12.0, 3.0],
                    "scale": [50.0, 6.0, 2.0]
                  }
                }
                """;
        File f2 = tempDir.resolve("model_with_scaler.json").toFile();
        try (FileWriter w = new FileWriter(f2)) { w.write(scalerJson); }
        modelWithScaler = new ModelLoader(f2.getAbsolutePath());
    }

    @Test
    void testSigmoid() {
        assertEquals(0.5, ModelLoader.sigmoid(0.0), 1e-10);
        assertTrue(ModelLoader.sigmoid(10.0) > 0.999);
        assertTrue(ModelLoader.sigmoid(-10.0) < 0.001);
    }

    @Test
    void testPredictNoScaler() {
        // z = -1.0 + 0.5*1.0 + (-0.3)*2.0 + 0.2*3.0 = -1.0 + 0.5 - 0.6 + 0.6 = -0.5
        double[] features = {1.0, 2.0, 3.0};
        double prob = modelNoScaler.predict(features);
        double expected = 1.0 / (1.0 + Math.exp(0.5));
        assertEquals(expected, prob, 1e-10);
    }

    @Test
    void testPredictWithScaler() {
        // Scaled: [(150-100)/50, (18-12)/6, (5-3)/2] = [1.0, 1.0, 1.0]
        // z = 0.0 + 1.0*1.0 + (-0.5)*1.0 + 0.3*1.0 = 0.8
        double[] features = {150.0, 18.0, 5.0};
        double prob = modelWithScaler.predict(features);
        double expected = 1.0 / (1.0 + Math.exp(-0.8));
        assertEquals(expected, prob, 1e-10);
    }

    @Test
    void testIsFraud() {
        // High values should produce fraud=true
        double[] highRisk = {10.0, 10.0, 10.0};
        // z = -1.0 + 0.5*10 + (-0.3)*10 + 0.2*10 = -1 + 5 - 3 + 2 = 3
        assertTrue(modelNoScaler.isFraud(highRisk));

        // Low values should produce fraud=false
        double[] lowRisk = {-10.0, 10.0, -10.0};
        // z = -1.0 + 0.5*(-10) + (-0.3)*10 + 0.2*(-10) = -1 - 5 - 3 - 2 = -11
        assertFalse(modelNoScaler.isFraud(lowRisk));
    }

    @Test
    void testModelMetadata() {
        assertEquals(3, modelNoScaler.getCoefficients().length);
        assertEquals(-1.0, modelNoScaler.getIntercept());
        assertEquals(0.5, modelNoScaler.getThreshold());
        assertFalse(modelNoScaler.hasScaler());
        assertTrue(modelWithScaler.hasScaler());
    }

    @Test
    void testFeatureNames() {
        String[] names = modelNoScaler.getFeatureNames();
        assertEquals(3, names.length);
        assertEquals("amount", names[0]);
        assertEquals("hour_of_day", names[1]);
        assertEquals("day_of_week", names[2]);
    }
}
