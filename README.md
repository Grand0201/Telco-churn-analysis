# Telecom Customer Churn Analysis and ML Churn Prediction

## Project Overview
This project analyzes customer churn behavior in a telecom company using SQL, Python, and Power BI.

The analysis identifies key churn drivers, customer risk segments, and business insights related to customer retention.

---

## Tools Used
- SQL (SQLite)
- Python (Pandas)
- Power BI

---

## Project Workflow
1. Cleaned and transformed telecom customer dataset using Python and Pandas
2. Loaded data into SQLite database
3. Performed churn analysis using SQL queries, CTEs, and window functions
4. Exported transformed dataset for Power BI visualization
5. Built interactive dashboard with churn insights and risk segmentation

---

## Key Metrics
- Customer Churn Rate
- Average Monthly Charges
- Customer Tenure
- Contract-based churn analysis
- Customer Risk Segmentation

---

## Dashboard Pages

### Customer Overview
[Overview](Telecom/Power%20BI/1_Total_Page.png)

### Churn Analysis
[Churn](Telecom/Power%20BI/2_Churn_Page.png)

### Risk Segmentation & Insights
[Risk](Telecom/Power%20BI/3_Risk_Page.png)

---

## Key Insights
- Month-to-month contracts demonstrate the highest churn behavior
- Customers with short tenure are significantly more likely to leave
- Fiber optic users show elevated churn rates
- High monthly charges correlate with increased churn risk
- Rule-based segmentation successfully identified high-risk customer groups

---
## Machine Learning Churn Prediction

Additionally, a machine learning model was developed to predict customer churn probability.

### ML Workflow
- Data cleaning and preprocessing using Pandas
- Feature encoding using One-Hot Encoding
- Train/Test split with stratification
- Feature scaling using StandardScaler
- Logistic Regression model training
- Model evaluation using Accuracy and ROC-AUC metrics

### Models Tested
- Logistic Regression
- Random Forest Classifier

### Best Model
Logistic Regression demonstrated the best overall performance:

- Accuracy: 80.38%
- ROC-AUC: 83.57%

### Additional Analysis
- Feature importance analysis using Logistic Regression coefficients
- Visualization of top churn-driving factors
- Exported trained model and scaler using Joblib
