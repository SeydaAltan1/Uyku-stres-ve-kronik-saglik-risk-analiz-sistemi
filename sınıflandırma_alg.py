import pandas as pd
import numpy as np
import os
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Gereksiz uyarıları kapat
warnings.filterwarnings('ignore')


def run_model_task(df, target_col, dataset_name, scenario):
    # Veri Hazırlığı
    df.columns = [c.strip() for c in df.columns]
    target_col = target_col.strip()

    drop_cols = [target_col, 'Hasta_ID', 'Kayit_Adi', 'Kayit_ID', 'Kayit_id', 'Denek_ID', 'DenekID']
    X_base = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # Senaryo Seçimi
    if scenario == "Kullanilabilir":
        if dataset_name == 'heart':
            cols = ['Yas', 'Tansiyon_Kan_Basinci', 'Kolesterol_Degeri', 'Maksimum_Kalp_Hizi']
            X = X_base[[c for c in cols if c in X_base.columns]]
        elif dataset_name == 'wesad':
            cols = ['EKG_Ort', 'EDA_Ort', 'Sicaklik_Ort']
            X = X_base[[c for c in cols if c in X_base.columns]]
        else:  # sleep
            X = X_base.iloc[:, :3]
    else:
        X = X_base

    y = df[target_col]
    if y.dtype != 'int64' and len(y.unique()) > 5:
        y = (y > y.median()).astype(int)
    if y.dtype == 'object':
        y = LabelEncoder().fit_transform(y)

    X_scaled = StandardScaler().fit_transform(X.fillna(0))

    # Dinamik K-Fold
    min_class = np.bincount(y).min() if len(np.bincount(y)) > 1 else 1
    k_val = min(10, min_class) if min_class > 1 else 2

    # Modeller
    models = {
        'RF': RandomForestClassifier(n_estimators=100, random_state=42),
        'MLP': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=2000, random_state=42),
        'YSA': MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', max_iter=2000, random_state=42)
    }

    results = {}
    for m_name, model in models.items():
        cv = cross_validate(model, X_scaled, y, cv=StratifiedKFold(k_val, shuffle=True),
                            scoring=['accuracy', 'recall_macro', 'precision_macro', 'f1_macro'])
        results[m_name] = {
            'Veri_Seti': dataset_name,
            'Accuracy': cv['test_accuracy'].mean(),
            'Recall': cv['test_recall_macro'].mean(),
            'Precision': cv['test_precision_macro'].mean(),
            'F1_Score': cv['test_f1_macro'].mean()
        }
    return results


# Dosya yolları
files = {
    'heart': ('HEART_DISEASE_MASTER_LISTESI.xlsx', 'Kalp_Hastaligi_Riski'),
    'wesad': ('WESAD_MASTER_LISTESI.xlsx', 'Stres_Durumu_Yuzde'),
    'sleep': ('SLEEP_EDF_MASTER_LISTESI.xlsx', 'EEG Fpz-Cz_Std')
}

# 6 Dosya için depo (3 model x 2 senaryo)
outputs = {
    'RF_ORIJINAL': [], 'RF_KULLANILABILIR': [],
    'MLP_ORIJINAL': [], 'MLP_KULLANILABILIR': [],
    'YSA_ORIJINAL': [], 'YSA_KULLANILABILIR': []
}

print(" 6 dosya hazırlanıyor...")

for d_name, (f_path, target) in files.items():
    if os.path.exists(f_path):
        df = pd.read_excel(f_path)

        # Orijinal Senaryo Çalıştır
        res_ori = run_model_task(df, target, d_name, "Orijinal")
        for m in ['RF', 'MLP', 'YSA']:
            outputs[f"{m}_ORIJINAL"].append(res_ori[m])

        # Kullanılabilir Senaryo Çalıştır
        res_kul = run_model_task(df, target, d_name, "Kullanilabilir")
        for m in ['RF', 'MLP', 'YSA']:
            outputs[f"{m}_KULLANILABILIR"].append(res_kul[m])

        print(f"✅ {d_name.upper()} bitti.")

# 6 Excel Dosyasını Kaydet
for file_key, data in outputs.items():
    pd.DataFrame(data).to_excel(f"{file_key}_SONUCLAR.xlsx", index=False)
    print(f"📁 {file_key}_SONUCLAR.xlsx kaydedildi.")

print("\n🚀 Toplam 6 dosya başarıyla oluşturuldu!")