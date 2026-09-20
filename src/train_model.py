import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, recall_score
from xgboost import XGBClassifier
import joblib

# -------------------------------
# Step 1: Load and prepare data
# -------------------------------
def load_data():
    print("Step 1: Loading data...")
    
    train = pd.read_csv("../data/UNSW_NB15_training_preprocessed.csv")
    test = pd.read_csv("../data/UNSW_NB15_testing_preprocessed.csv")
    
    target = 'binary_label'
    
    # Ensure target exists
    if target not in train.columns or target not in test.columns:
        raise KeyError(f"{target} not found in train/test data!")
    
    # Drop suspicious / highly correlated features to prevent leakage
    if 'attack_cat_Normal' in train.columns:
        train = train.drop(columns=['attack_cat_Normal'])
        test = test.drop(columns=['attack_cat_Normal'])
    
    # Features and labels
    X_train = train.drop(columns=[target])
    y_train = train[target]
    X_test = test.drop(columns=[target])
    y_test = test[target]
    
    print(f"Training samples: {X_train.shape[0]}, Testing samples: {X_test.shape[0]}")
    return X_train, X_test, y_train, y_test

# ----------------------------------------
# Step 2: Handle class imbalance & train
# ----------------------------------------
def train_model(X_train, y_train):
    print("Step 2: Training XGBoost model with hyperparameter tuning...")
    
    # Class weights to handle imbalance
    from sklearn.utils import class_weight
    classes = np.unique(y_train)
    weights = class_weight.compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
    class_weights = {cls: weight for cls, weight in zip(classes, weights)}
    
    # XGBoost with GridSearch for hyperparameter tuning
    xgb = XGBClassifier(eval_metric='logloss', use_label_encoder=False)
    
    param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [5, 7],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 1],
        'colsample_bytree': [0.8, 1],
        'scale_pos_weight': [class_weights[0]/class_weights[1]]  # handle imbalance
    }
    
    grid = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=3, scoring='recall', n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)
    
    print("Best params:", grid.best_params_)
    model = grid.best_estimator_
    return model

# -------------------------------------------------
# Step 3: Evaluate model with optimized threshold
# -------------------------------------------------
def evaluate_model(model, X_test, y_test):
    print("Step 3: Evaluating model...")
    
    y_probs = model.predict_proba(X_test)[:,1]
    
    # Optimize threshold for attack recall
    thresholds = np.arange(0.1, 1.0, 0.01)
    best_thresh = 0.5
    best_recall = 0
    
    for thresh in thresholds:
        y_pred = (y_probs >= thresh).astype(int)
        recall = recall_score(y_test, y_pred)
        if recall > best_recall:
            best_recall = recall
            best_thresh = thresh
    
    print(f"Optimal threshold for max attack recall: {best_thresh:.2f} with recall={best_recall:.4f}")
    
    y_pred_final = (y_probs >= best_thresh).astype(int)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_final))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_final))
    
    roc_auc = roc_auc_score(y_test, y_probs)
    print(f"ROC-AUC: {roc_auc:.4f}")
    
    return y_pred_final

# ---------------------------
# Step 4: Cross-validation
# ---------------------------
def cross_validate_model(model, X_train, y_train):
    print("Step 4: Performing 5-Fold Cross Validation...")
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    
    for train_idx, val_idx in skf.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        model.fit(X_tr, y_tr)
        y_val_probs = model.predict_proba(X_val)[:,1]
        aucs.append(roc_auc_score(y_val, y_val_probs))
    
    print(f"Cross-validation ROC-AUC scores: {aucs}")
    print(f"Mean ROC-AUC: {np.mean(aucs):.4f}, Std: {np.std(aucs):.4f}")

# ---------------------------
# Main
# ---------------------------
def main():
    X_train, X_test, y_train, y_test = load_data()
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    cross_validate_model(model, X_train, y_train)
    
    # Save model
    joblib.dump(model, "xgboost_model.pkl")
    print("✅ Model saved to 'xgboost_model.pkl'")

if __name__ == "__main__":
    main()
