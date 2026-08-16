# DeliverAI ML Predictions Analysis Report

Generated automatically from `test.txt` containing **100** prediction logs.

## 1. Global Performance Metrics

| Metric | Value |
| --- | --- |
| **Total Test Samples** | 100 |
| **Mean Accuracy** | **83.25%** |
| **Median Accuracy** | **92.30%** |
| **Mean Absolute Error (MAE)** | 8.76 hours |
| **Root Mean Squared Error (RMSE)** | 14.13 hours |

## 2. Model Selection Share
Percentage of runs where each model yielded the prediction closest to the actual time:

| Model | Best Selection Count | Share (%) |
| --- | --- | --- |
| **xgboost** | 43 | 43.00% |
| **linear_regression** | 39 | 39.00% |
| **random_forest** | 18 | 18.00% |

## 3. Geospatial Performance Breakdown

| Distance Tier | Sample Count | Mean Accuracy | Median Accuracy | MAE | Dominant Model |
| --- | --- | --- | --- | --- | --- |
| Local / Urban (<50 km) | 12 | 35.63% | 23.30% | 0.69h | linear_regression (41.7%) |
| Medium-Haul (250-1000 km) | 32 | 87.81% | 90.15% | 4.55h | xgboost (56.2%) |
| Long-Haul (>1000 km) | 56 | 90.85% | 93.50% | 12.90h | linear_regression (48.2%) |

## 4. Overall Model Error Comparison (Across all valid rows)

| Model | MAE | RMSE |
| --- | --- | --- |
| XGBoost | 14.33h | 20.77h |
| Random Forest | 21.81h | 29.20h |
| Linear Regression | 14.61h | 19.49h |

## 5. Diagnostic Insights

* **Underperforming Runs (<70% Acc)**: 14 of 100 (14.00%)
* **Mean Distance of Underperforming Runs**: 461.67 km
* **Local Deliveries (<50 km) Concentration**: 10 runs (71.43% of all underperforming runs)
  > [!TIP]
  > High error concentration in local deliveries (< 50 km) is common since small traffic anomalies or dispatch delays represent a large relative percentage error for short trips. Enhancing local traffic features can improve short-haul accuracy.

## 6. Detailed 1 km Range Performance Breakdown

Here is the best performing model (dominant model with the most wins) for every 1 km distance tier:

| Distance Tier (km) | Sample Count | Mean Accuracy | MAE (hours) | Dominant Model | Model Win Share (%) |
| --- | --- | --- | --- | --- | --- |
| 12-13 | 3 | 14.20% | 0.65h | linear_regression | 100.00% |
| 13-14 | 1 | 10.00% | 0.90h | linear_regression | 100.00% |
| 19-20 | 2 | 41.05% | 0.81h | random_forest | 100.00% |
| 20-21 | 5 | 40.06% | 0.74h | xgboost | 40.00% |
| 31-32 | 1 | 92.60% | 0.14h | random_forest | 100.00% |
| 269-270 | 1 | 82.00% | 4.03h | random_forest | 100.00% |
| 309-310 | 1 | 97.50% | 0.70h | xgboost | 100.00% |
| 316-317 | 1 | 94.10% | 1.76h | xgboost | 100.00% |
| 323-324 | 1 | 99.80% | 0.05h | xgboost | 100.00% |
| 324-325 | 1 | 89.70% | 2.52h | random_forest | 100.00% |
| 362-363 | 1 | 98.90% | 0.31h | xgboost | 100.00% |
| 371-372 | 1 | 96.40% | 1.01h | xgboost | 100.00% |
| 382-383 | 1 | 85.40% | 3.83h | xgboost | 100.00% |
| 425-426 | 1 | 92.30% | 2.23h | xgboost | 100.00% |
| 442-443 | 1 | 91.20% | 2.57h | xgboost | 100.00% |
| 453-454 | 1 | 91.70% | 2.41h | xgboost | 100.00% |
| 457-458 | 1 | 89.20% | 3.12h | random_forest | 100.00% |
| 459-460 | 1 | 95.50% | 1.55h | xgboost | 100.00% |
| 461-462 | 1 | 90.60% | 2.75h | random_forest | 100.00% |
| 476-477 | 1 | 91.30% | 2.47h | xgboost | 100.00% |
| 497-498 | 1 | 96.80% | 0.90h | xgboost | 100.00% |
| 502-503 | 1 | 93.80% | 1.92h | xgboost | 100.00% |
| 520-521 | 1 | 67.10% | 15.67h | xgboost | 100.00% |
| 524-525 | 1 | 86.70% | 4.66h | xgboost | 100.00% |
| 530-531 | 1 | 73.50% | 13.14h | linear_regression | 100.00% |
| 537-538 | 1 | 70.90% | 14.82h | linear_regression | 100.00% |
| 545-546 | 1 | 94.80% | 1.50h | xgboost | 100.00% |
| 551-552 | 1 | 70.10% | 16.42h | linear_regression | 100.00% |
| 597-598 | 1 | 85.70% | 4.07h | xgboost | 100.00% |
| 660-661 | 1 | 98.30% | 0.70h | linear_regression | 100.00% |
| 729-730 | 1 | 97.80% | 0.87h | random_forest | 100.00% |
| 746-747 | 1 | 89.70% | 3.71h | random_forest | 100.00% |
| 790-791 | 1 | 80.80% | 6.01h | linear_regression | 100.00% |
| 799-800 | 1 | 87.40% | 2.59h | linear_regression | 100.00% |
| 809-810 | 1 | 80.80% | 12.95h | xgboost | 100.00% |
| 823-824 | 1 | 63.80% | 6.44h | linear_regression | 100.00% |
| 971-972 | 1 | 86.20% | 7.81h | random_forest | 100.00% |
| 1004-1005 | 1 | 88.00% | 5.75h | linear_regression | 100.00% |
| 1057-1058 | 1 | 83.80% | 13.78h | xgboost | 100.00% |
| 1096-1097 | 1 | 78.10% | 11.18h | linear_regression | 100.00% |
| 1119-1120 | 1 | 97.90% | 1.50h | xgboost | 100.00% |
| 1128-1129 | 1 | 93.00% | 3.53h | random_forest | 100.00% |
| 1211-1212 | 1 | 96.20% | 2.80h | linear_regression | 100.00% |
| 1250-1251 | 1 | 99.10% | 0.64h | random_forest | 100.00% |
| 1353-1354 | 1 | 94.10% | 3.87h | random_forest | 100.00% |
| 1601-1602 | 1 | 73.00% | 34.54h | xgboost | 100.00% |
| 1623-1624 | 1 | 94.40% | 4.01h | linear_regression | 100.00% |
| 1646-1647 | 1 | 98.40% | 1.23h | linear_regression | 100.00% |
| 1687-1688 | 1 | 97.30% | 2.54h | random_forest | 100.00% |
| 2083-2084 | 1 | 92.60% | 9.63h | xgboost | 100.00% |
| 2226-2227 | 1 | 68.80% | 52.36h | xgboost | 100.00% |
| 2314-2315 | 1 | 97.50% | 3.24h | xgboost | 100.00% |
| 2328-2329 | 1 | 77.30% | 38.11h | linear_regression | 100.00% |
| 2395-2396 | 1 | 90.70% | 14.28h | xgboost | 100.00% |
| 2546-2547 | 1 | 98.30% | 2.29h | xgboost | 100.00% |
| 2584-2585 | 1 | 83.90% | 27.07h | xgboost | 100.00% |
| 2593-2594 | 1 | 92.40% | 11.98h | xgboost | 100.00% |
| 2709-2710 | 1 | 86.40% | 17.88h | linear_regression | 100.00% |
| 2722-2723 | 1 | 69.70% | 50.83h | linear_regression | 100.00% |
| 2781-2782 | 1 | 94.00% | 7.46h | random_forest | 100.00% |
| 2811-2812 | 1 | 95.30% | 5.41h | linear_regression | 100.00% |
| 2848-2849 | 1 | 96.10% | 5.01h | linear_regression | 100.00% |
| 2854-2855 | 1 | 98.40% | 1.98h | linear_regression | 100.00% |
| 2866-2867 | 1 | 79.80% | 30.37h | linear_regression | 100.00% |
| 2873-2874 | 1 | 80.10% | 31.63h | linear_regression | 100.00% |
| 2880-2881 | 1 | 94.20% | 9.72h | linear_regression | 100.00% |
| 2920-2921 | 1 | 94.10% | 7.01h | linear_regression | 100.00% |
| 2921-2922 | 1 | 80.70% | 32.47h | linear_regression | 100.00% |
| 2931-2932 | 1 | 98.90% | 1.32h | linear_regression | 100.00% |
| 2955-2956 | 1 | 98.50% | 1.93h | linear_regression | 100.00% |
| 2965-2966 | 1 | 83.50% | 25.42h | linear_regression | 100.00% |
| 2987-2988 | 1 | 99.80% | 0.25h | linear_regression | 100.00% |
| 3000-3001 | 21 | 92.54% | 11.87h | xgboost | 61.90% |

