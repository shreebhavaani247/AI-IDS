import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split

# ---------------------------
# Step 0: Load preprocessed data
# ---------------------------
TRAIN_FILE = "../data/UNSW_NB15_training_preprocessed.csv"
TEST_FILE = "../data/UNSW_NB15_testing_preprocessed.csv"

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Train columns: {train_df.columns.tolist()}")
print(f"Test columns: {test_df.columns.tolist()}")

# ---------------------------
# Step 1: Correlation analysis
# ---------------------------
label_col = 'binary_label'  # replace if your label column name differs
corr = train_df.corr()[label_col].sort_values(ascending=False)
print("\nTop 10 features positively correlated with label:\n", corr.head(10))
print("\nTop 10 features negatively correlated with label:\n", corr.tail(10))

# Identify suspicious features highly correlated with label (>0.95)
suspicious_features = corr[abs(corr) > 0.95].index.tolist()
print("\nSuspicious features (abs(corr) > 0.95):\n", suspicious_features)

# ---------------------------
# Step 2: Prepare data for modeling
# ---------------------------
X_train = train_df.drop(columns=[label_col])
y_train = train_df[label_col]
X_test = test_df.drop(columns=[label_col])
y_test = test_df[label_col]

# Remove suspicious features
if suspicious_features:
    print("\nDropping suspicious features from training/testing...")
    X_train = X_train.drop(columns=suspicious_features, errors='ignore')
    X_test = X_test.drop(columns=suspicious_features, errors='ignore')

# ---------------------------
# Step 3: Train XGBoost model
# ---------------------------
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='logloss'
)

print("\nTraining model...")
model.fit(X_train, y_train)

# ---------------------------
# Step 4: Evaluate model
# ---------------------------
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

roc_auc = roc_auc_score(y_test, y_proba)
print(f"ROC-AUC: {roc_auc:.4f}")

# ---------------------------
# Step 5: Feature importance (optional)
# ---------------------------
import matplotlib.pyplot as plt
xgb.plot_importance(model, max_num_features=20, importance_type='gain')
plt.title("Top 20 Feature Importances")
plt.show()
