import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# 1. DOSYA YOLLARI VE TANIMLAMALAR
base_path = r"C:\Users\pc\PycharmProjects\BMUTproje\\"

# Master (Orijinal) dosyaları
master_files = {
    "HEART": base_path + "HEART_DISEASE_MASTER_LISTESI.xlsx",
    "SLEEP": base_path + "SLEEP_EDF_MASTER_LISTESI.xlsx",
    "WESAD": base_path + "WESAD_MASTER_LISTESI.xlsx"
}

# Kullanılabilir Özellikler dosyaları
kullanilabilir_files = {
    "HEART": base_path + "HEART_DISEASE_HASTALAR_LISTESI_OZET.xlsx",
    "SLEEP": base_path + "SLEEP_EDF_HASTALAR_LISTESI.xlsx",
    "WESAD": base_path + "WESAD_HASTALAR_LISTESI.xlsx"
}


def veri_on_isleme_yap(file_path, prefix):
    """5 adımlı ön işleme sürecini uygular ve dosyaları kaydeder."""
    print(f"\n--- İşleniyor: {file_path} ---")

    try:
        # Dosyayı oku
        df = pd.read_excel(file_path)
        # Sadece sayısal sütunları seç (ID veya isim gibi metinleri işlememek için)
        numeric_df = df.select_dtypes(include=[np.number])
        non_numeric_df = df.select_dtypes(exclude=[np.number])

        # ADIM 5: MEDYAN TAMAMLAMA (Eksik verileri doldurma - Genelde ilk yapılır)
        df_step5 = numeric_df.fillna(numeric_df.median())
        df_step5 = pd.concat([non_numeric_df, df_step5], axis=1)
        df_step5.to_excel(f"{prefix}_ADIM5_MEDYAN_TAMAMLAMA.xlsx", index=False)
        print("Adım 5 Tamamlandı.")

        # ADIM 1: NORMALİZASYON (Min-Max 0-1)
        scaler_minmax = MinMaxScaler()
        normalized_data = scaler_minmax.fit_transform(numeric_df.fillna(numeric_df.median()))
        df_step1 = pd.concat([non_numeric_df, pd.DataFrame(normalized_data, columns=numeric_df.columns)], axis=1)
        df_step1.to_excel(f"{prefix}_ADIM1_NORMALIZASYON.xlsx", index=False)
        print("Adım 1 Tamamlandı.")

        # ADIM 2: STANDARTLAŞTIRMA (Z-Score)
        scaler_std = StandardScaler()
        standardized_data = scaler_std.fit_transform(numeric_df.fillna(numeric_df.median()))
        df_step2 = pd.concat([non_numeric_df, pd.DataFrame(standardized_data, columns=numeric_df.columns)], axis=1)
        df_step2.to_excel(f"{prefix}_ADIM2_STANDARTLASTIRMA.xlsx", index=False)
        print("Adım 2 Tamamlandı.")

        # ADIM 3: AYKIRI DEĞER TEMİZLİĞİ (IQR Yöntemi ile Baskılama)
        df_step3_num = numeric_df.copy()
        for col in df_step3_num.columns:
            Q1 = df_step3_num[col].quantile(0.25)
            Q3 = df_step3_num[col].quantile(0.75)
            IQR = Q3 - Q1
            alt_sinir = Q1 - 1.5 * IQR
            ust_sinir = Q3 + 1.5 * IQR
            df_step3_num[col] = np.where(df_step3_num[col] < alt_sinir, alt_sinir, df_step3_num[col])
            df_step3_num[col] = np.where(df_step3_num[col] > ust_sinir, ust_sinir, df_step3_num[col])
        df_step3 = pd.concat([non_numeric_df, df_step3_num], axis=1)
        df_step3.to_excel(f"{prefix}_ADIM3_AYKIRI_DEGER_TEMIZLIGI.xlsx", index=False)
        print("Adım 3 Tamamlandı.")

        # ADIM 4: AYRIKLAŞTIRMA (Sayısal verileri 3 kategoriye bölme: Dusuk, Orta, Yuksek)
        df_step4 = df_step5.copy()  # Medyan dolmuş veri üzerinden
        # Örnek olarak ilk sayısal sütunu ayrıklaştırıyoruz
        target_col = numeric_df.columns[0]
        df_step4[f'{target_col}_Kategori'] = pd.qcut(df_step4[target_col], q=3, labels=["Dusuk", "Orta", "Yuksek"],
                                                     duplicates='drop')
        df_step4.to_excel(f"{prefix}_ADIM4_AYRIKLASTIRMA.xlsx", index=False)
        print("Adım 4 Tamamlandı.")

    except Exception as e:
        print(f"Hata oluştu ({prefix}): {e}")


# --- ÇALIŞTIRMA ---

# 1. Master (Orijinal) Dosyalar İçin İşlemler
for key, path in master_files.items():
    veri_on_isleme_yap(path, f"{base_path}{key}_MASTER")

# 2. Kullanılabilir Özellikler İçin İşlemler
for key, path in kullanilabilir_files.items():
    veri_on_isleme_yap(path, f"{base_path}{key}_KULLANILABILIR")

print("\n!!! Tüm işlemler başarıyla tamamlandı. Dosyalar klasörünüze kaydedildi.")