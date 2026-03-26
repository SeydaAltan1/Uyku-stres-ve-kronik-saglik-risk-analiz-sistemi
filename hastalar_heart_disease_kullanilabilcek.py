import pandas as pd
import numpy as np


def create_heart_total_patient_list(file_path):
    # UCI Cleveland veri setinin standart 14 sütun yapısı
    # Raporundaki analiz parametrelerine göre isimlendirme yapıyoruz
    cols = [
        'Yas', 'Cinsiyet', 'Gogus_Agrisi_Tipi', 'Dinlenme_Kan_Basinci',
        'Kolesterol', 'Aclik_Kan_Sekeri', 'EKG_Sonucu', 'Maks_Kalp_Hizi',
        'Egzersiz_Anjini', 'ST_Depresyonu', 'ST_Egrimi', 'Damar_Sayisi',
        'Talasemi_Durumu', 'Hedef_Risk'
    ]

    try:
        # Veri setindeki '?' işaretlerini NaN (boş) olarak kabul et [cite: 40]
        df = pd.read_csv(file_path, names=cols, na_values='?')

        # Ön İşleme: Eksik verileri sütun ortalaması ile doldur (Temiz Tasarım Kanıtı) [cite: 161, 162]
        df = df.fillna(df.mean())

        # Verileri yuvarlayalım (Görsel temizlik için)
        df = df.round(1)

        # Excel dosyası oluşturma
        output_name = "HEART_DISEASE_HASTALAR_LISTESI_OZET.xlsx"
        df.to_excel(output_name, index=False)

        print("\n" + "=" * 40)
        print(f"BAŞARIYLA OLUŞTURULDU: {output_name}")
        print(f"Toplam Hasta Sayısı: {len(df)}")
        print("=" * 40)

    except Exception as e:
        print(f"Hata oluştu: {e}")


# --- ÇALIŞTIRMA ---
create_heart_total_patient_list(r"D:\heart+disease\processed.cleveland.data")