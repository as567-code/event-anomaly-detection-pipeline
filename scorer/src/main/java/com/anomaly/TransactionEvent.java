package com.anomaly;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * POJO representing a transaction event from the Kafka producer.
 * Feature order must match the model's expected input.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class TransactionEvent {

    @JsonProperty("event_id")
    private long eventId;

    private long timestamp;
    private double amount;

    @JsonProperty("hour_of_day")
    private double hourOfDay;

    @JsonProperty("day_of_week")
    private double dayOfWeek;

    @JsonProperty("merchant_category")
    private double merchantCategory;

    @JsonProperty("distance_from_home")
    private double distanceFromHome;

    @JsonProperty("distance_from_last_txn")
    private double distanceFromLastTxn;

    @JsonProperty("transaction_frequency")
    private double transactionFrequency;

    @JsonProperty("avg_transaction_amount")
    private double avgTransactionAmount;

    @JsonProperty("time_since_last_txn")
    private double timeSinceLastTxn;

    @JsonProperty("is_online")
    private double isOnline;

    @JsonProperty("card_present")
    private double cardPresent;

    @JsonProperty("merchant_risk_score")
    private double merchantRiskScore;

    @JsonProperty("account_age_days")
    private double accountAgeDays;

    @JsonProperty("num_failed_txns_24h")
    private double numFailedTxns24h;

    @JsonProperty("credit_utilization")
    private double creditUtilization;

    @JsonProperty("amount_zscore")
    private double amountZscore;

    @JsonProperty("velocity_1h")
    private double velocity1h;

    @JsonProperty("is_foreign")
    private double isForeign;

    public TransactionEvent() {}

    /**
     * Returns feature values in the order expected by the model.
     */
    public double[] toFeatureArray(String[] featureNames) {
        double[] features = new double[featureNames.length];
        for (int i = 0; i < featureNames.length; i++) {
            features[i] = getFeatureByName(featureNames[i]);
        }
        return features;
    }

    private double getFeatureByName(String name) {
        return switch (name) {
            case "amount" -> amount;
            case "hour_of_day" -> hourOfDay;
            case "day_of_week" -> dayOfWeek;
            case "merchant_category" -> merchantCategory;
            case "distance_from_home" -> distanceFromHome;
            case "distance_from_last_txn" -> distanceFromLastTxn;
            case "transaction_frequency" -> transactionFrequency;
            case "avg_transaction_amount" -> avgTransactionAmount;
            case "time_since_last_txn" -> timeSinceLastTxn;
            case "is_online" -> isOnline;
            case "card_present" -> cardPresent;
            case "merchant_risk_score" -> merchantRiskScore;
            case "account_age_days" -> accountAgeDays;
            case "num_failed_txns_24h" -> numFailedTxns24h;
            case "credit_utilization" -> creditUtilization;
            case "amount_zscore" -> amountZscore;
            case "velocity_1h" -> velocity1h;
            case "is_foreign" -> isForeign;
            default -> 0.0;
        };
    }

    // Getters
    public long getEventId() { return eventId; }
    public long getTimestamp() { return timestamp; }
    public double getAmount() { return amount; }
    public double getHourOfDay() { return hourOfDay; }
    public double getDayOfWeek() { return dayOfWeek; }
    public double getMerchantCategory() { return merchantCategory; }
    public double getDistanceFromHome() { return distanceFromHome; }
    public double getDistanceFromLastTxn() { return distanceFromLastTxn; }
    public double getTransactionFrequency() { return transactionFrequency; }
    public double getAvgTransactionAmount() { return avgTransactionAmount; }
    public double getTimeSinceLastTxn() { return timeSinceLastTxn; }
    public double getIsOnline() { return isOnline; }
    public double getCardPresent() { return cardPresent; }
    public double getMerchantRiskScore() { return merchantRiskScore; }
    public double getAccountAgeDays() { return accountAgeDays; }
    public double getNumFailedTxns24h() { return numFailedTxns24h; }
    public double getCreditUtilization() { return creditUtilization; }
    public double getAmountZscore() { return amountZscore; }
    public double getVelocity1h() { return velocity1h; }
    public double getIsForeign() { return isForeign; }

    // Setters
    public void setEventId(long eventId) { this.eventId = eventId; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    public void setAmount(double amount) { this.amount = amount; }
    public void setHourOfDay(double hourOfDay) { this.hourOfDay = hourOfDay; }
    public void setDayOfWeek(double dayOfWeek) { this.dayOfWeek = dayOfWeek; }
    public void setMerchantCategory(double merchantCategory) { this.merchantCategory = merchantCategory; }
    public void setDistanceFromHome(double distanceFromHome) { this.distanceFromHome = distanceFromHome; }
    public void setDistanceFromLastTxn(double distanceFromLastTxn) { this.distanceFromLastTxn = distanceFromLastTxn; }
    public void setTransactionFrequency(double transactionFrequency) { this.transactionFrequency = transactionFrequency; }
    public void setAvgTransactionAmount(double avgTransactionAmount) { this.avgTransactionAmount = avgTransactionAmount; }
    public void setTimeSinceLastTxn(double timeSinceLastTxn) { this.timeSinceLastTxn = timeSinceLastTxn; }
    public void setIsOnline(double isOnline) { this.isOnline = isOnline; }
    public void setCardPresent(double cardPresent) { this.cardPresent = cardPresent; }
    public void setMerchantRiskScore(double merchantRiskScore) { this.merchantRiskScore = merchantRiskScore; }
    public void setAccountAgeDays(double accountAgeDays) { this.accountAgeDays = accountAgeDays; }
    public void setNumFailedTxns24h(double numFailedTxns24h) { this.numFailedTxns24h = numFailedTxns24h; }
    public void setCreditUtilization(double creditUtilization) { this.creditUtilization = creditUtilization; }
    public void setAmountZscore(double amountZscore) { this.amountZscore = amountZscore; }
    public void setVelocity1h(double velocity1h) { this.velocity1h = velocity1h; }
    public void setIsForeign(double isForeign) { this.isForeign = isForeign; }
}
