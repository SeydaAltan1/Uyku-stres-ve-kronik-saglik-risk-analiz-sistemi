import pandas as pd
import pickle
import os


def create_wesad_patient_list(base_path):
    patient_list = []
    # S2'den S17'ye kadar olan klasörleri kontrol et
    subjects = [f'S{i}' for i in range(2, 18)]

    for sub in subjects:
        file_path = os.path.join(base_path, sub, f"{sub}.pkl")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f, encoding='latin1')

                chest = data['signal']['chest']
                # Milyonlarca satırdan tek bir özet satırı oluşturma (Feature Extraction)
                patient_list.append({
                    'Hasta_ID': sub,
                    'Ort_Nabiz': chest['ECG'].mean(),
                    'Ort_Deri_Iletkenligi': chest['EDA'].mean(),
                    'Ort_Vucut_Sicakligi': chest.get('Temp', chest.get('temp', chest.get('TEMP'))).mean(),
                    'Stres_Tespit_Yuzdesi': (data['label'] == 2).mean() * 100
                })
                print(f"{sub} başarıyla eklendi.")
            except Exception as e:
                print(f"{sub} işlenirken hata oluştu: {e}")

    if patient_list:
        df = pd.DataFrame(patient_list)
        df.to_excel("WESAD_HASTALAR_LISTESI.xlsx", index=False)
        print("\n--> WESAD_HASTALAR_LISTESI.xlsx oluşturuldu!")
    else:
        print("HATA: Hiçbir WESAD verisi işlenemedi. Klasör yolunu kontrol et.")


# ÇALIŞTIR
create_wesad_patient_list(r"D:\WESAD\WESAD")