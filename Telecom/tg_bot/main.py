import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score


df = pd.read_csv('Telco_Customer_Churn.csv')

# print(df.head())
# print(df.info())
# print(df.dtypes) # проверка типов данных, чтоб категориальные перевести на числовые (encode)
# print(df.shape)

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'] , errors='coerce')
df.dropna(inplace=True) # удалить пустые
# print(df.shape) # минус 11 строк из 7к

# Разделить X/y
X = df.drop(columns=['customerID', 'Churn']) # ид не нужен для модели
y = df['Churn'].map({'Yes': 1, 'No': 0}) # map заменяет данные

# перевод буквы в 0/1
X_encoded = pd.get_dummies(X, drop_first=True)
# print(X_encoded.shape) # +9 колонок

# train/test
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2,
                                                    random_state=42, stratify=y)
# scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# log/reg
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

# pred/proba
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

log_accuracy = accuracy_score(y_test, y_pred)
log_roc_auc = roc_auc_score(y_test, y_proba)

# print('Logistic Regression:')
# print(f"Accuracy: {log_accuracy * 100:.2f}%")
# print(f"ROC-AUC: {log_roc_auc * 100:.2f}%")

# Random forest
# model_rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=20,
#                                   min_samples_split=8, min_samples_leaf=3, n_jobs=-1)
# # n_jobs = -1 использовать все ядра сразу (параллельно)
# model_rf.fit(X_train, y_train)
#
# # pred/proba
# y_pred_rf = model_rf.predict(X_test)
# y_proba_rf = model_rf.predict_proba(X_test)[:, 1]
#
# print('\nRandom Forest:')
# print(f"Accuracy: {accuracy_score(y_test, y_pred_rf) * 100:.2f}%")
# print(f"ROC-AUC: {roc_auc_score(y_test, y_proba_rf) * 100:.2f}%")

# Logistic Regression:
# Accuracy: 80.38%
# ROC-AUC: 83.57%
# Random Forest:
# Accuracy: 79.18%
# ROC-AUC: 83.38%

# Log reg wins!

# коэффициент влияния признаков (coef_)
coef_table = pd.DataFrame()
coef_table['Columns'] = X_train.columns
coef_table['Coefficients'] = model.coef_[0]
coef_table = coef_table.sort_values(by='Coefficients', key=abs, ascending=False) # key=abs - значение |в модуле|
# print(coef_table)

# график
positive = coef_table[coef_table['Coefficients'] > 0].head(10)
negative = coef_table[coef_table['Coefficients'] < 0].head(10)
#
plt.figure(figsize=(12, 6))
sns.set_style('whitegrid')
plt.subplot(1, 2, 1)
sns.barplot(x='Coefficients', y='Columns', data=negative)
plt.title('Топ-10 признаков снижения оттока')
plt.subplot(1, 2, 2)
sns.barplot(x='Coefficients', y='Columns', data=positive)
plt.title('Топ-10 признаков повышения оттока')
plt.tight_layout()
plt.show()

import joblib

joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(X_train.columns.tolist(), 'columns_list.pkl') # список колонок после encode

m = joblib.load('model.pkl')
scal = joblib.load('scaler.pkl')
col = joblib.load('columns_list.pkl')

# print(col)