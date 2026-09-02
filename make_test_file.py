import pandas as pd
import numpy as np

# Synthetic corporate financial dataset with intentional outliers
data = {
    "Department": [
        "Marketing", "Sales", "Engineering", "Customer Support", 
        "Operations", "HR", "Finance", "Legal", "Product", "IT"
    ],
    "Monthly_Budget_USD": [
        45000, 120000, 350000, 60000, 
        85000, 40000, 50000, 42000, 210000, 95000
    ],
    "Actual_Spend_USD": [
        48000, 115000, 890000, 62000,  # 890,000 is a massive spend outlier
        82000, 41000, 51000, 43000, 215000, 98000
    ],
    "Variance_Pct": [
        0.06, -0.04, 1.54, 0.03,  # 1.54 (154% over) is a variance outlier
        -0.03, 0.02, 0.02, 0.02, 0.02, 0.03
    ],
    "Headcount": [
        12, 25, 45, 18, 
        15, 8, 9, 6, 22, 14
    ]
}

df = pd.DataFrame(data)

# Save to Excel
output_filename = "Test_KPI_Data.xlsx"
df.to_excel(output_filename, index=False)
print(f"Successfully generated '{output_filename}' with sample financial outliers!")