import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    mean_squared_error, 
    mean_absolute_error, 
    r2_score, 
    accuracy_score, 
    classification_report, 
    roc_auc_score
)

def train_and_evaluate():
    # 1. Load the compiled Phase 2 data matrix
    MATRIX_PATH = os.path.join("data", "processed", "modeling_matrix.csv")
    
    print(" Loading Phase 2 modeling matrix...")
    if not os.path.exists(MATRIX_PATH):
        raise FileNotFoundError(f"Missing modeling matrix at {MATRIX_PATH}. Please run Phase 2 first.")
        
    df = pd.read_csv(MATRIX_PATH)
    
    # 2. Sort chronologically by match date to prevent lookahead data leakage
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 3. Explicitly define our analytical feature features from your 13-column schema
    # feature_cols = [
    #     'temperature', 
    #     'humidity', 
    #     'stadium_avg_runs', 
    #     'team1_roster_index', 
    #     'team2_roster_index', 
    #     'index_differential'
    # ]

    # 2. Map features explicitly from your 13-column schema
    feature_cols = [
        'temperature', 
        'humidity', 
        'stadium_avg_runs', 
        'index_differential'  # Removed individual team indices to kill multicollinearity!
    ]
    
    print(f" Extracting {len(feature_cols)} features for training: {feature_cols}")
    X = df[feature_cols]
    y_reg = df['innings1_runs']  # Continuous target for score forecasting
    y_clf = df['team1_won']      # Binary target for match outcome prediction

    # Ensure no NaN fields slip through into scikit-learn
    valid_idx = X.notna().all(axis=1) & y_reg.notna() & y_clf.notna()
    X = X[valid_idx]
    y_reg = y_reg[valid_idx]
    y_clf = y_clf[valid_idx]
    
    # 4. Chronological Split (80% historical training pool, 20% future testing pool)
    # Crucial: shuffle=False isolates our evaluation to the most recent season matches
    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, shuffle=False
    )
    
    print(f" Temporal Split Complete. Train size: {len(X_train)} | Test size: {len(X_test)}")
    
    # 5. Standardize Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # =========================================================================
    # TASK 1: OLS Linear Regression (Predicting Innings 1 Runs Magnitude)
    # =========================================================================
    print("\n Training OLS Linear Regression Model...")
    reg_model = LinearRegression()
    reg_model.fit(X_train_scaled, y_reg_train)
    
    # Generate continuous predictions
    y_reg_pred = reg_model.predict(X_test_scaled)
    
    print("---  LINEAR REGRESSION METRICS (Score Prediction) ---")
    print(f"Mean Absolute Error (MAE) : {mean_absolute_error(y_reg_test, y_reg_pred):.2f} runs")
    print(f"Root Mean Squared Error (RMSE): {np.sqrt(mean_squared_error(y_reg_test, y_reg_pred)):.2f} runs")
    print(f"R-squared (R2) Score          : {r2_score(y_reg_test, y_reg_pred):.4f}")
    
    print("\n💡 Feature Coefficients (Impact on 1st Innings Runs):")
    for feat, coef in zip(feature_cols, reg_model.coef_):
        print(f"   -> {feat}: {coef:+.4f}")
    print(f"   -> Intercept: {reg_model.intercept_:.2f}")
        
    # =========================================================================
    # TASK 2: Logistic Regression (Predicting Match Win Probabilities)
    # =========================================================================
    print("\n Training Logistic Regression Model...")
    clf_model = LogisticRegression(random_state=42, max_iter=1000)
    clf_model.fit(X_train_scaled, y_clf_train)
    
    # Generate binary predictions and continuous classification probability distributions
    y_clf_pred = clf_model.predict(X_test_scaled)
    y_clf_proba = clf_model.predict_proba(X_test_scaled)[:, 1]
    
    print("--- 🔮 LOGISTIC REGRESSION METRICS (Win Probability) ---")
    print(f"Accuracy Score: {accuracy_score(y_clf_test, y_clf_pred) * 100:.2f}%")
    print(f"ROC-AUC Score : {roc_auc_score(y_clf_test, y_clf_proba):.4f}")
    print("\n Classification Report:")
    print(classification_report(y_clf_test, y_clf_pred, target_names=['Team 2 Wins', 'Team 1 Wins']))
    
    print("\n Feature Odds Ratios (Impact on Win Probability):")
    for feat, coef in zip(feature_cols, clf_model.coef_[0]):
        odds_ratio = np.exp(coef)
        print(f"   -> {feat}: Coef = {coef:+.4f} | Odds Ratio = {odds_ratio:.4f}")

if __name__ == "__main__":
    train_and_evaluate()