# Sentiment Analysis Experiment Report
## Customer Insights Dashboard — ML Experiment Log

Author: Muhammad Abdullah Asim
Date: May 2026
Project: Customer Insights Dashboard

---

## Objective

Design and validate a satisfaction score formula for customer reviews that produces a continuous score between -1 and 1. The score should reflect how satisfied a customer is based on their written review text and star rating.

Secondary objective: identify the most accurate classification model for predicting whether a review is positive or negative on real customer data.

---

## Data Used

Three AI-generated CSV files used for initial experimentation:

- Customers.csv: 98 rows
- Customers2.csv: 253 rows
- Customers500.csv: 503 rows

One real-world dataset used for final honest validation:

- Amazon Reviews Dataset (Kaggle): 2000 rows loaded, balanced to 618 rows across all star ratings

The AI-generated files produced inflated accuracy scores (97-98%) because the text and star ratings were too clean and consistent. Real Amazon data produced honest and meaningful accuracy numbers.

---

## Confidence Case Logic

Every customer row was categorized into one of three cases before scoring:

| Case | Condition | Confidence Label | Confidence Score |
|------|-----------|-----------------|-----------------|
| 1 | Has both review text and star rating | high | 1.0 |
| 2 | Has star rating only, no text | low | 0.25 |
| 3 | Has neither | null | null |

Distribution across files:
- Roughly 85-90% of customers fall into the high confidence case
- Roughly 7-9% fall into the low confidence case
- Roughly 4-5% have no scoreable data

---

## Text Scoring Models Evaluated

### VADER
- Dictionary-based sentiment scorer
- Produces continuous scores between -1 and 1
- Strength: gradual output, handles neutral and mildly positive text well
- Weakness: misreads sarcasm, reads isolated positive words in negative reviews as positive
- Example failure: "Customer service is a joke they will actively try to help you" scored positive because of the word "help"

### DistilBert (distilbert-base-uncased-finetuned-sst-2-english)
- Transformer-based model fine-tuned on real review text
- Understands language context and sentence meaning
- Strength: catches sarcasm, understands full sentence negativity
- Weakness: binary output, nearly always returns scores near 1.0 or -1.0, no middle ground
- Requires truncation=True, max_length=512 for long reviews

### Dual Model
- Combines VADER and DistilBert
- When both models agree on direction: text weighted 70%, rating weighted 30%
- When models disagree: text weighted 40%, rating weighted 60%
- Handles edge cases where one model overreacts

---

## Satisfaction Score Formulas Tested

All formulas normalize the star rating using: (review_score - 3) / 2
This maps 1 star to -1, 3 star to 0, 5 star to 1.

| Formula | Text Weight | Rating Weight | Text Model |
|---------|-------------|---------------|------------|
| VADER 70/30 | 70% | 30% | VADER |
| VADER 50/50 | 50% | 50% | VADER |
| DistilBert 70/30 | 70% | 30% | DistilBert |
| DistilBert 50/50 | 50% | 50% | DistilBert |
| Dual model | 70% or 40% | 30% or 60% | VADER + DistilBert |

Key finding on formula behavior:

- VADER 70/30 scores some 1-star negative reviews as positive because VADER misreads mixed language
- DistilBert 70/30 scores some 4-star positive reviews as negative because DistilBert overreacts to minor complaints
- VADER 50/50 fixes most VADER 70/30 problems by giving more weight to the star rating
- DistilBert 50/50 fixes most DistilBert 70/30 problems similarly
- Dual model handles edge cases best in visual inspection but does not outperform DistilBert 50/50 in classification accuracy

---

## Classification Model Results on Real Amazon Data

All tests used Random Forest (n_estimators=100) or Logistic Regression with class_weight=balanced unless noted. TF-IDF max_features=2000 on review text.

### Top 10 results ranked by accuracy

| Rank | Model | Feature | Mean Accuracy |
|------|-------|---------|---------------|
| 1 | Logistic Regression | DistilBert 50/50 | 92.23% |
| 2 | Logistic Regression | VADER 50/50 | 91.08% |
| 3 | Logistic Regression | Dual satisfaction | 89.29% |
| 4 | RF ngram (1,2) | DistilBert 70/30 | 89.79% |
| 5 | RF + length | DistilBert 70/30 | 89.47% |
| 6 | RF ngram (1,2) | DistilBert 50/50 | 89.46% |
| 7 | RF 300 estimators | DistilBert 70/30 | 89.30% |
| 8 | RF 300 estimators | DistilBert 50/50 | 89.30% |
| 9 | RF 100 estimators | DistilBert 70/30 | 88.50% |
| 10 | RF 100 estimators | DistilBert 50/50 | 88.17% |

### Original notebook baseline on real data

| Version | Model | Feature | Mean Accuracy |
|---------|-------|---------|---------------|
| A (3 stars removed) | LR no class weight | VADER raw | 83.97% |
| B (all stars kept) | LR no class weight | VADER raw | 81.53% |

Starting point on original AI-generated data: 68%
Best result on real Amazon data: 92.23%

---

## Winner: Logistic Regression + DistilBert 50/50

### Why it wins

- Highest accuracy at 92.23% on real messy Amazon data
- Most consistent fold scores: 83%, 98%, 96%, 98%, 84%
- Best confusion matrix: only 25 false positives and 23 false negatives
- Balanced errors, not heavily biased toward one class
- Simple model that works well because the DistilBert 50/50 feature is already strong

### Why Logistic Regression beats Random Forest here

The DistilBert 50/50 feature already captures most of the signal cleanly. Logistic Regression learns a simple decision boundary on a clean feature. Random Forest adds complexity that does not help when the feature is already strong.

---

## Production Decision

### Satisfaction score formula chosen for backend

DistilBert 50/50 with confidence tracking.

Logic:

- If both review text and star rating exist: satisfaction = (0.5 x distilbert_score) + (0.5 x rating_score), confidence = high, confidence_score = 1.0
- If rating only, no text: satisfaction = rating_score, confidence = low, confidence_score = 0.25
- If neither: satisfaction = null, confidence = null, confidence_score = null

### Why not the dual model

The dual model performed better in visual spot checks on ambiguous reviews but did not improve classification accuracy over DistilBert 50/50 alone. Added complexity without measurable gain on real data.

### Why not VADER

VADER misreads sarcasm and mixed language reviews. On real Amazon data DistilBert consistently outperforms VADER, especially on negative reviews that contain some positive-sounding words.

---

## Database Changes Required

Two new columns added to the Customer model:

- confidence_label: String, nullable, stores high or low
- confidence_score: Numeric(3,2), nullable, stores 1.0 or 0.25

---

## Key Lessons Learned

1. AI-generated test data produces inflated accuracy scores. Always validate on real data before drawing conclusions.

2. Label leakage is a real danger. Using a satisfaction score that includes the star rating as a feature to predict a label derived from the star rating produces artificially perfect accuracy. Always keep the feature and the label source separate.

3. More complex models do not always win. Logistic Regression beat Random Forest with 300 estimators when the feature was strong enough.

4. Binary classifiers like DistilBert are not directly suitable for producing continuous satisfaction scores. They work best as a feature input into another model or as part of a blended formula.

5. Class imbalance matters. Adding class_weight=balanced consistently improved results across all models on imbalanced datasets.

6. The 3 star problem is real but removing 3 star reviews does not help. The model needs to handle ambiguous reviews naturally through the formula weighting.

---

## Next Steps

- Integrate satisfaction score formula into FastAPI backend
- Add database migration for confidence_label and confidence_score columns
- Build churn risk model using behavioural signals: last_purchase_date, total_spent, recency
- Build customer segmentation model
- Expose all ML scores through analytics dashboard endpoints