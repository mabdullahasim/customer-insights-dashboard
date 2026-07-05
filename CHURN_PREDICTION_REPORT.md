# Churn Prediction Model Report
## Customer Insights Dashboard
### ML Experiment Summary | April 2026

---

## 1. Project Overview

This report documents the machine learning experiments conducted during development of the Customer Insights Dashboard. The goal was to build a churn prediction pipeline that trains on a user's own uploaded customer data and produces actionable churn risk signals for every customer.

The pipeline runs in three sequential stages. Each stage builds on the previous one and all three must run in order before churn prediction results are available.

Pipeline stages:
- Stage 1: Sentiment scoring using DistilBERT and star ratings
- Stage 2: Rule-based churn risk scoring from purchase recency
- Stage 3: Random Forest churn prediction trained on the user's own customers

---

## 2. Datasets Used in Experimentation

### 2.1 Amazon Reviews Dataset

The first dataset used was a 2000-row Amazon reviews dataset built for sentiment analysis experimentation. After filtering for rows with review text, 618 usable rows remained.

| Field | Value |
|---|---|
| Total rows | 2000 (618 after filtering for review text) |
| Columns used | full_name, email, country, total_spent, last_purchase_date, review_score, review_text |
| Review score distribution | 1 star: 189, 2 star: 113, 3 star: 75, 4 star: 52, 5 star: 189 |
| Purpose | Sentiment scoring and satisfaction label experimentation |
| Churn suitability | Not suitable. All 590 labeled rows showed churn_label = 1 due to reference date mismatch |

The churn label problem with this dataset occurred because the reference date was set to April 2026 and all purchase dates were from 2024 and 2025. Every customer exceeded the 90 day ceiling, making the label useless for model training. This led to switching to the IBM Telco dataset for churn model experimentation.

### 2.2 IBM Telco Customer Churn Dataset

The IBM Telco dataset was used for all churn prediction model experiments. It contains real subscription behavior with genuine observed churn events.

| Field | Value |
|---|---|
| Total rows | 7043 |
| Total columns | 50 |
| Churn label | Churn Label: Yes (1869) / No (5174) |
| Class balance | 73% retained, 27% churned |
| Nulls | Offer: 3877 nulls, Internet Type: 1526 nulls, all other features complete |
| Churn label type | Real observed cancel events, not inferred from recency |

Columns excluded from features due to leakage risk:
- Churn Score (IBM pre-computed probability, direct leakage)
- CLTV (derived from churn outcome)
- Customer Status (directly encodes the outcome)
- Churn Category and Churn Reason (post-churn information only available after the customer left)

---

## 3. Stage 1: Satisfaction Scoring

### 3.1 Method

Each customer receives a satisfaction score computed from two sources: the DistilBERT transformer model fine-tuned on SST-2 for sentiment classification, and a normalized star rating.

- DistilBERT produces a signed confidence score between -1.0 and +1.0
- Star rating is normalized using: (review_score - 3) / 2, mapping 1-5 to -1 to +1
- Both scores are blended at 50% each: satisfaction = 0.5 x distilbert_score + 0.5 x rating_score

Confidence labels are assigned based on data availability:
- Both review text and star rating present: confidence_label = high, confidence_score = 1.0
- Star rating only, no review text: confidence_label = low, confidence_score = 0.25
- Neither present: null, no score stored

### 3.2 Satisfaction Model Results

A Logistic Regression classifier using TF-IDF on review text combined with the satisfaction score was evaluated using 5-fold cross validation on 618 rows from the Amazon dataset.

| Metric | Value |
|---|---|
| Model | Logistic Regression with TF-IDF + satisfaction score |
| Dataset | Amazon reviews, 618 rows after filtering |
| Cross-validation folds | 5 |
| Mean CV accuracy | 92.23% |
| CV scores per fold | 83.1%, 98.4%, 96.8%, 98.4%, 84.6% |
| Class 0 precision / recall | 94% / 93% |
| Class 1 precision / recall | 90% / 90% |
| Confusion matrix | TP: 218, TN: 352, FP: 25, FN: 23 |

The high variance across folds (83% to 98%) reflects the small dataset size and imbalanced class distribution. Class 0 (negative) had 377 samples versus 241 for Class 1 (positive), requiring class_weight=balanced in the model.

---

## 4. Stage 2: Rule-Based Churn Risk Scoring

### 4.1 Design

The rule-based churn score converts days of silence since last_purchase_date into a risk score between 0.0 and 1.0 using a linear ramp between two thresholds chosen based on business judgment.

| Parameter | Value |
|---|---|
| Floor | 60 days. Risk is 0.0 for customers silent fewer than 60 days |
| Ceiling | 90 days. Risk is 1.0 for customers silent 90 or more days |
| Formula between floor and ceiling | churn_risk = (recency_days - 60) / 30 |
| Clipping | Result clipped to range 0.0 to 1.0 |
| Missing dates | Customers with no last_purchase_date receive null |
| Churn label threshold | churn_label = Yes if churn_risk > 0.5, else No |

### 4.2 Purpose

This rule serves two roles simultaneously. First, it is a working analytics metric visible on the dashboard that tells a business which customers have gone quiet. Second, the churn_label it stamps on each customer becomes the training label for the Stage 3 machine learning model.

Because the label is derived from recency, recency itself is excluded as a feature in Stage 3 to avoid leakage. The model must learn from other signals rather than rediscovering the recency threshold.

---

## 5. Stage 3: Machine Learning Churn Prediction

### 5.1 Experimental Datasets Evaluated

#### 5.1.1 Synthetic Online Retail Dataset

A synthetic retail churn dataset with 1000 rows and a Target_Churn column was evaluated first. The results showed no predictive signal.

| Metric | Value |
|---|---|
| Model | Random Forest Classifier, 100 estimators |
| Accuracy | 49.5% |
| Result | Essentially random, no better than a coin flip |
| Root cause | Target_Churn had near-zero correlation with all features. Dataset was synthetically generated with no real relationship between label and features. |
| Feature correlations | Total_Spend: 0.028, Satisfaction_Score: 0.022, Last_Purchase_Days_Ago: -0.013, Years_as_Customer: -0.029 |

This confirmed that synthetic datasets with randomly assigned labels produce no meaningful model regardless of model complexity. The dataset was discarded.

#### 5.1.2 IBM Telco Dataset (Final)

The IBM Telco dataset was used for all final model experiments. Four features were selected that aligned with the signals available in the Customer Insights Dashboard.

| Field | Value |
|---|---|
| Features used | Tenure in Months, Monthly Charge, Total Charges, Satisfaction Score |
| Label | Churn Label (Yes/No converted to 1/0 via LabelEncoder) |
| Train/test split | 80% train, 20% test, random_state=42 |
| Training rows | 5634 |
| Test rows | 1409 |

### 5.2 Random Forest Results

| Metric | Value |
|---|---|
| Model | Random Forest Classifier, 100 estimators, random_state=42 |
| Test accuracy | 93.97% |
| True negatives (correctly called retained) | 989 |
| True positives (correctly called churned) | 335 |
| False positives (predicted churned, actually retained) | 20 |
| False negatives (predicted retained, actually churned) | 65 |
| Class 0 precision / recall / F1 | 94% / 98% / 96% |
| Class 1 precision / recall / F1 | 94% / 84% / 89% |

### 5.3 Logistic Regression Results

Logistic Regression was also evaluated on the same train/test split as a comparison to Random Forest.

| Metric | Value |
|---|---|
| Model | Logistic Regression, random_state=42 |
| Test accuracy | 93.90% |
| True negatives | 1005 |
| True positives | 318 |
| False positives | 4 |
| False negatives | 82 |
| Class 0 precision / recall / F1 | 92% / 100% / 96% |
| Class 1 precision / recall / F1 | 99% / 80% / 88% |

### 5.4 Model Comparison

Both models achieved nearly identical overall accuracy. The key difference was in their error profiles.

- Random Forest caught more churners: 335 vs 318 true positives. Higher recall on the churn class.
- Logistic Regression made fewer false positive errors: 4 vs 20. When it flagged someone as churned it was almost always right.
- For churn prevention, catching more real churners (Random Forest) is more valuable than avoiding false alarms.

Random Forest was selected for integration into the backend churn_prediction endpoint.

### 5.5 Feature Correlations with Churn Label

Pearson correlations between each feature and the churn label confirmed all four features carried real signal.

| Feature | Correlation |
|---|---|
| Satisfaction Score | -0.755 (strongest signal, low satisfaction strongly predicts churn) |
| Tenure in Months | -0.353 (longer tenure means lower churn risk) |
| Total Charges | -0.199 (higher total spend correlates with lower churn) |
| Monthly Charge | +0.193 (higher monthly cost slightly increases churn risk) |

Satisfaction Score was the single most predictive feature. This validates the decision to invest in sentiment scoring as a leading churn signal.

---

## 6. Backend Integration

### 6.1 Pipeline Architecture

The churn prediction pipeline is implemented as three sequential FastAPI endpoints. Each endpoint must be called in order.

| Endpoint | Action |
|---|---|
| POST /analytics/run-sentiment | Computes sentiment_score, confidence_label, confidence_score for all customers |
| POST /analytics/run-churn | Computes churn_risk and churn_label from recency rule for all customers |
| POST /analytics/run-churn-prediction | Trains Random Forest on user's customers, writes churn_prediction probabilities |

### 6.2 Churn Prediction Feature Set

The backend churn_prediction function uses seven features built from the customer table columns.

| Feature | Description |
|---|---|
| total_spent | Customer cumulative spend, value signal |
| sentiment_score | DistilBERT satisfaction score, leading churn signal |
| review_score | Raw star rating 1 to 5 |
| confidence_score | Reliability weight of sentiment signal, 1.0 or 0.25 |
| confidence_label encoded | high = 1.0, low = 0.5, unknown = 0.0 |
| recency_days | Days since last_purchase_date, computed at runtime |
| account_age_days | Days since account_created_at, currently 0 for most customers |

### 6.3 Per-User Model Design

Each user who uploads their own customer CSV gets their own model trained on their own data. There is no shared global model across users. The model retrains on every call to run-churn-prediction.

A minimum of 50 labeled customers is required before the model runs. Below that threshold the endpoint returns a message asking the user to upload more data.

---

## 7. Known Limitations

- Recency leakage risk: recency_days is included as a feature but was also used to build churn_label via the 60 to 90 day rule. The model partially learns the recency threshold back rather than discovering new patterns from satisfaction and spending alone.

- account_age_days is currently zero for all customers because account_created_at is not captured in the CSV upload schema. This feature contributes no predictive value until signup dates are collected.

- Small dataset risk: the 50 customer minimum is a soft guard. Models trained on fewer than 200 customers produce unreliable results.

- The model retrains from scratch on every call. For large customer bases this adds latency to the endpoint.

- No production accuracy benchmark exists yet. The 93.97% figure comes from IBM Telco data, not from the live application running against real uploaded customer data.

- The Telco training domain is subscription-based telecom. The production model trains on non-subscription retail data with different churn dynamics. Feature importance rankings may differ in production.

---

## 8. Recommended Future Work

- Capture account_created_at from the CSV upload schema so tenure becomes a real feature with predictive value.

- Remove recency_days from the feature set and rely on satisfaction, spending, and confidence signals alone to reduce the leakage risk from the recency-derived label.

- Add a frontend warning when a user has fewer than 200 customers so they understand model accuracy may be limited.

- Cache the trained model per user so it does not retrain on every call unless new data has been uploaded since the last run.

- Log accuracy scores per user per run to a separate table so accuracy trends are trackable over time.

- Evaluate adding order count as a frequency feature by introducing an orders table to the schema, which would unlock purchase frequency and trend signals currently missing from the pipeline.

---

Author: Muhammad Abdullah Asim
Computer Science, Western University (Class of 2028)
