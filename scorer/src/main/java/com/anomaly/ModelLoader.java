package com.anomaly;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;

/**
 * Loads logistic regression model weights from a JSON file exported by sklearn.
 * Computes sigmoid(w·x + b) natively in Java — no PMML dependency.
 */
public class ModelLoader {

    private static final Logger log = LoggerFactory.getLogger(ModelLoader.class);

    private final double[] coefficients;
    private final double intercept;
    private final double threshold;
    private final String[] featureNames;
    private final double[] scalerMean;
    private final double[] scalerScale;
    private final boolean hasScaler;

    public ModelLoader(String modelPath) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(new File(modelPath));

        int nFeatures = root.get("n_features").asInt();
        this.intercept = root.get("intercept").asDouble();
        this.threshold = root.get("threshold").asDouble();

        JsonNode coefNode = root.get("coefficients");
        this.coefficients = new double[nFeatures];
        for (int i = 0; i < nFeatures; i++) {
            this.coefficients[i] = coefNode.get(i).asDouble();
        }

        JsonNode namesNode = root.get("feature_names");
        this.featureNames = new String[nFeatures];
        for (int i = 0; i < nFeatures; i++) {
            this.featureNames[i] = namesNode.get(i).asText();
        }

        if (root.has("scaler")) {
            this.hasScaler = true;
            JsonNode scalerNode = root.get("scaler");
            JsonNode meanNode = scalerNode.get("mean");
            JsonNode scaleNode = scalerNode.get("scale");
            this.scalerMean = new double[nFeatures];
            this.scalerScale = new double[nFeatures];
            for (int i = 0; i < nFeatures; i++) {
                this.scalerMean[i] = meanNode.get(i).asDouble();
                this.scalerScale[i] = scaleNode.get(i).asDouble();
            }
        } else {
            this.hasScaler = false;
            this.scalerMean = null;
            this.scalerScale = null;
        }

        log.info("Model loaded: {} features, threshold={}, scaler={}", nFeatures, threshold, hasScaler);
    }

    /**
     * Computes the fraud probability using sigmoid(w·x + b).
     */
    public double predict(double[] features) {
        double[] input = features;
        if (hasScaler) {
            input = scale(features);
        }

        double z = intercept;
        for (int i = 0; i < coefficients.length; i++) {
            z += coefficients[i] * input[i];
        }
        return sigmoid(z);
    }

    public boolean isFraud(double[] features) {
        return predict(features) >= threshold;
    }

    public boolean isFraud(TransactionEvent event) {
        double[] features = event.toFeatureArray(featureNames);
        return isFraud(features);
    }

    public double score(TransactionEvent event) {
        double[] features = event.toFeatureArray(featureNames);
        return predict(features);
    }

    private double[] scale(double[] features) {
        double[] scaled = new double[features.length];
        for (int i = 0; i < features.length; i++) {
            scaled[i] = (features[i] - scalerMean[i]) / scalerScale[i];
        }
        return scaled;
    }

    static double sigmoid(double z) {
        return 1.0 / (1.0 + Math.exp(-z));
    }

    public double[] getCoefficients() { return coefficients; }
    public double getIntercept() { return intercept; }
    public double getThreshold() { return threshold; }
    public String[] getFeatureNames() { return featureNames; }
    public boolean hasScaler() { return hasScaler; }
}
