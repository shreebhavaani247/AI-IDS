import pandas as pd
from sklearn.model_selection import train_test_split

# 1. Load data
train_path = "../data/UNSW_NB15_training.csv"
test_path = "../data/UNSW_NB15_testing.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# 2. Map label to binary: 0=Normal, 1=Attack
# The UNSW dataset has a column 'label' or 'attack_cat' for categories
# We'll assume 'label' exists: 0 = normal, 1 = attack
train_df['binary_label'] = train_df['label'].apply(lambda x: 0 if x == 0 else 1)
test_df['binary_label'] = test_df['label'].apply(lambda x: 0 if x == 0 else 1)

# 3. Drop original label column if needed
train_df = train_df.drop(columns=['label'])
test_df = test_df.drop(columns=['label'])

# 4. Identify categorical columns
categorical_cols = train_df.select_dtypes(include=['object']).columns.tolist()

# 5. One-hot encode categorical columns
train_df = pd.get_dummies(train_df, columns=categorical_cols)
test_df = pd.get_dummies(test_df, columns=categorical_cols)

# 6. Align columns (train/test might have different dummy columns)
train_df, test_df = train_df.align(test_df, join='left', axis=1, fill_value=0)

# 7. Split features and labels
X_train = train_df.drop('binary_label', axis=1)
y_train = train_df['binary_label']
X_test = test_df.drop('binary_label', axis=1)
y_test = test_df['binary_label']

# 8. Optional: save preprocessed files for faster reload
train_df.to_csv("../data/UNSW_NB15_training_preprocessed.csv", index=False)
test_df.to_csv("../data/UNSW_NB15_testing_preprocessed.csv", index=False)

print("Step 1 completed: Data loaded and preprocessed successfully!")
print(f"Training samples: {X_train.shape[0]}, Testing samples: {X_test.shape[0]}")

def preprocess_line(df):
    """
    Accepts a DataFrame with a single log line and returns the processed feature vector
    aligned with training columns
    """
    # Identify categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # One-hot encode categorical columns
    df = pd.get_dummies(df, columns=categorical_cols)
    
    return df
