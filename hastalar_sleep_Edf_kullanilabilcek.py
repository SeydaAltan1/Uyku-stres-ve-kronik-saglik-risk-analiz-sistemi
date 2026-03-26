import pyedflib
import pandas as pd
import os


def create_sleep_patient_list(folder_path):
    record_list = []
    # Klasördeki PSG (sinyal) dosyalarını tara
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for f in filenames:
            if f.endswith(".edf") and "PSG" in f:
                files.append(os.path.join(root, f))

    for f_path in files:
        try:
            f = pyedflib.EdfReader(f_path)
            labels = f.getSignalLabels()
            entry = {'Kayit_ID': os.path.basename(f_path).split('-')[0]}

            for i, label in enumerate(labels):
                if 'EEG' in label:
                    entry['EEG_Genlik_Ort'] = f.readSignal(i)[:50000].mean()
                if 'EOG' in label:
                    entry['Goz_Hareketi_Std'] = f.readSignal(i)[:50000].std()

            record_list.append(entry)
            f.close()
            print(f"{os.path.basename(f_path)} eklendi.")
        except Exception as e:
            print(f"Hata: {e}")

    if record_list:
        df = pd.DataFrame(record_list)
        df.to_excel("SLEEP_EDF_HASTALAR_LISTESI.xlsx", index=False)
        print("\n--> SLEEP_EDF_HASTALAR_LISTESI.xlsx oluşturuldu!")
    else:
        print("HATA: Uygun .edf dosyası bulunamadı.")


# ÇALIŞTIR
create_sleep_patient_list(r"D:\sleep-edf-database-expanded-1.0.0")