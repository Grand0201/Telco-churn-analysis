import sqlite3
import pandas as pd

df = pd.read_csv('Telco_Customer_Churn.csv')

pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df.dropna(inplace=True)
# print(df.columns)

conn = sqlite3.connect('Telco_Customer_Churn.db')

df.to_sql('Telco_Customer_Churn', conn, if_exists='replace', index=False)

# Проверка загрузки
query = '''
    SELECT *
    FROM Telco_Customer_Churn
    LIMIT 3'''

load_df = pd.read_sql(query, conn)
# print(load_df)

# Общее кол-во оттока(Churn)
query = '''
    SELECT 
        Churn,
        COUNT(*) AS Users
    FROM Telco_Customer_Churn
    GROUP BY Churn'''

total_churn_df = pd.read_sql(query, conn)
# print(total_churn_df)

# Запрос оттока в %
churn_percent_query = '''
    WITH churn_count AS (
        SELECT 
            Churn,
            COUNT(*) AS Users
        FROM Telco_Customer_Churn
        GROUP BY Churn
    ),
    total_churn AS (
        SELECT
            COUNT(*) AS total_churn
            FROM Telco_Customer_Churn
    )
    SELECT 
        cc.Churn,
        cc.Users,
        ROUND(cc.Users * 100 / t.total_churn, 2) AS churn_rate
    FROM churn_count cc, total_churn t;
'''
percent_churn_df = pd.read_sql(churn_percent_query, conn)
# print('Отток в процентах\n', percent_churn_df)

# Отток по контракту
contract_query = '''
    WITH contract_churn AS (
        SELECT 
            Contract,
            Churn,
            COUNT(*) AS Users
        FROM Telco_Customer_Churn
        GROUP BY Contract, Churn
        ),
        
        total_churn AS (
        SELECT
            COUNT(*) AS total_churn
            FROM Telco_Customer_Churn
        )
        
        SELECT 
            c.Contract,
            c.Churn,
            c.Users,
            ROUND(c.Users * 100 / t.total_churn, 2) AS churn_rate
        FROM contract_churn c, total_churn t
        ORDER BY churn_rate DESC;
'''

contract_df = pd.read_sql(contract_query, conn)
# print(contract_df)

# Отток по сроку использования (tenure)
tenure_query = '''
    WITH tenure_groups AS (
        SELECT 
            CASE
                WHEN tenure BETWEEN 1 AND 12 THEN '0-1 year'
                WHEN tenure BETWEEN 13 AND 24 THEN '1-2 years'
                WHEN tenure BETWEEN 25 AND 48 THEN '2-4 years'
                ELSE '4+ years'
            END AS tenure_group,
            Churn
        FROM Telco_Customer_Churn
        ),
        
        stats AS (
            SELECT 
                tenure_group,
                Churn,
                COUNT(*) AS Users
            FROM tenure_groups
            GROUP BY tenure_group, Churn
        ),
        
        totals AS (
            SELECT
                tenure_group,
                COUNT(*) AS total_count
            FROM tenure_groups
            GROUP BY tenure_group
        )
        SELECT
            s.tenure_group,
            s.Churn,
            s.Users,
            ROUND(s.Users * 100.0 / t.total_count, 2) AS churn_rate
        FROM stats s 
        JOIN totals t 
            ON s.tenure_group = t.tenure_group
        ORDER BY churn_rate DESC;
'''

tenure_groups_df = pd.read_sql(tenure_query, conn)
# print(tenure_groups_df)

# Какие группы клиентов приносят больше денег и чаще уходят
charge_churn_query = '''
    WITH contract_stats AS (
        SELECT
            Contract,
            COUNT(*) AS total_users,
            SUM(CASE 
                WHEN Churn = 'Yes' THEN 1 
                ELSE 0 
            END) AS churned_users,
            ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge
        FROM Telco_Customer_Churn
        GROUP BY Contract
    ),
    
    final_stats AS (
        SELECT
            Contract,
            total_users,
            churned_users,
            ROUND(churned_users * 100.0 / total_users, 2) AS churn_rate,
            avg_monthly_charge
        FROM contract_stats
    )
    
    SELECT *,
           ROW_NUMBER() OVER (
               ORDER BY churn_rate DESC
           ) AS churn_rank
        FROM final_stats;
'''

df = pd.read_sql(charge_churn_query, conn)
# print(df)

# risk group
top_segments_query = '''
WITH customer_segments AS (
    SELECT
        customerID,
        Contract,
        tenure,
        MonthlyCharges,
        Churn,
        
        CASE
            WHEN Contract = 'Month-to-month'
                 AND tenure < 12
                 AND MonthlyCharges > 70
            THEN 'High Risk'

            WHEN tenure BETWEEN 12 AND 24
            THEN 'Medium Risk'

            ELSE 'Low Risk'
        END AS risk_group
    FROM Telco_Customer_Churn
),

segment_stats AS (
    SELECT
        risk_group,
        COUNT(*) AS total_users,
        SUM(CASE
            WHEN Churn = 'Yes' THEN 1
            ELSE 0
        END) AS churned_users
    FROM customer_segments
    GROUP BY risk_group
)

SELECT
    risk_group,
    total_users,
    churned_users,
    ROUND(
        churned_users * 100.0 / total_users,
        2
    ) AS churn_rate,

    ROW_NUMBER() OVER (
        ORDER BY churned_users DESC
    ) AS risk_rank

FROM segment_stats
ORDER BY churn_rate DESC;
'''

risk_df = pd.read_sql(top_segments_query, conn)
# print(risk_df)


# Новая таблица для экспорта в power bi
final_query = '''
    CREATE TABLE churn_final AS
    
    SELECT
        customerID,
        gender,
    
        CASE
            WHEN SeniorCitizen = 1
            THEN 'Senior'
            ELSE 'Non-Senior'
        END AS is_senior,
    
        Partner,
        Dependents,
        tenure,
    
        CASE
            WHEN tenure BETWEEN 1 AND 12 THEN '0-1 year'
            WHEN tenure BETWEEN 13 AND 24 THEN '1-2 years'
            WHEN tenure BETWEEN 25 AND 48 THEN '2-4 years'
            ELSE '4+ years'
        END AS tenure_group,
    
        PhoneService,
        MultipleLines,
        InternetService,
        OnlineSecurity,
        OnlineBackup,
        DeviceProtection,
        TechSupport,
        StreamingTV,
        StreamingMovies,
    
        Contract,
    
        CASE
            WHEN Contract = 'Month-to-month'
            THEN 1
            WHEN Contract = 'One year'
            THEN 2
            ELSE 3
        END AS contract_rank,
    
        PaperlessBilling,
        PaymentMethod,
    
        MonthlyCharges,
    
        CASE
            WHEN MonthlyCharges < 35 THEN '1-35'
            WHEN MonthlyCharges BETWEEN 35 AND 70 THEN '35-70'
            ELSE '70+'
        END AS monthly_charge_group,
    
        TotalCharges,
    
        CASE
            WHEN Contract = 'Month-to-month'
                 AND tenure < 12
                 AND MonthlyCharges > 70
            THEN 'High Risk'
    
            WHEN tenure BETWEEN 12 AND 24
            THEN 'Medium Risk'
    
            ELSE 'Low Risk'
        END AS risk_group,
    
        Churn
    
    FROM Telco_Customer_Churn;
'''

conn.execute('DROP TABLE IF EXISTS churn_final')
conn.execute(final_query)
conn.commit()

# Проверка
test_query = '''SELECT * FROM churn_final;'''
test_df = pd.read_sql(test_query, conn)
# print(test_df.head())

# перевод в csv
final_df = pd.read_sql(test_query, conn)

final_df.to_csv('churn_final.csv', index=False)

# print(final_df.head())

