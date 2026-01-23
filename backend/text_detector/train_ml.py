"""
ML Model Training Script
Trains a Random Forest classifier on TF-IDF + extra features
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy.sparse import hstack
from utils_ml import preprocess, extra_features


def train_model(dataset_path, output_dir='models'):
    """
    Train AI text detection model
    
    Args:
        dataset_path: Path to CSV file with columns: 'text' and 'label'
                     label: 0 = human, 1 = AI
        output_dir: Directory to save trained model and vectorizer
    """
    
    print("[INFO] Loading dataset...")
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at {dataset_path}")
        print("Please provide a CSV with 'text' and 'label' columns")
        return False
    
    data = pd.read_csv(dataset_path)
    
    if 'text' not in data.columns or 'label' not in data.columns:
        print("[ERROR] CSV must contain 'text' and 'label' columns")
        return False
    
    print(f"[INFO] Dataset loaded: {len(data)} samples")
    print(f"[INFO] Label distribution:\n{data['label'].value_counts()}")
    
    # Preprocess texts
    print("[INFO] Preprocessing texts...")
    data['text'] = data['text'].apply(preprocess)
    
    X = data['text']
    y = data['label']
    
    # Create TF-IDF features
    print("[INFO] Creating TF-IDF features (max 3000 features, 1-2 grams)...")
    tfidf = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        stop_words='english'
    )
    X_tfidf = tfidf.fit_transform(X)
    print(f"[INFO] TF-IDF shape: {X_tfidf.shape}")
    
    # Extract extra features
    print("[INFO] Extracting extra features (length, vocabulary diversity)...")
    X_extra = np.array([extra_features(t) for t in X])
    
    # Combine features
    print("[INFO] Combining TF-IDF and extra features...")
    X_final = hstack([X_tfidf, X_extra])
    print(f"[INFO] Final feature matrix shape: {X_final.shape}")
    
    # Train-test split
    print("[INFO] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y, test_size=0.2, random_state=42
    )
    
    # Train Random Forest
    print("[INFO] Training Random Forest (300 trees)...")
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=20
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    print("[INFO] Evaluating model...")
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    precision = precision_score(y_test, y_test_pred, average='weighted')
    recall = recall_score(y_test, y_test_pred, average='weighted')
    f1 = f1_score(y_test, y_test_pred, average='weighted')
    
    print("\n" + "="*50)
    print("MODEL PERFORMANCE")
    print("="*50)
    print(f"Train Accuracy: {train_acc:.4f}")
    print(f"Test Accuracy:  {test_acc:.4f}")
    print(f"Precision:      {precision:.4f}")
    print(f"Recall:         {recall:.4f}")
    print(f"F1-Score:       {f1:.4f}")
    print("="*50 + "\n")
    
    # Save model and vectorizer
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'ai_text_model.pkl')
    tfidf_path = os.path.join(output_dir, 'tfidf_vectorizer.pkl')
    
    print(f"[INFO] Saving model to {model_path}...")
    joblib.dump(model, model_path)
    
    print(f"[INFO] Saving TF-IDF vectorizer to {tfidf_path}...")
    joblib.dump(tfidf, tfidf_path)
    
    print("\n✅ Model training complete!")
    print(f"   Model: {model_path}")
    print(f"   Vectorizer: {tfidf_path}")
    
    return True


if __name__ == '__main__':
    import sys
    
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else 'dataset.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'models'
    
    train_model(dataset_path, output_dir)
