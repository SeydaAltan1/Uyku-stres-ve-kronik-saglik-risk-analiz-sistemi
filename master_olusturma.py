import pandas as pd
import pickle
import os
import numpy as np
import pyedflib


def wesad_kurtar(ana_yol):
    print("\n--- WESAD İşlemi Başladı ---")
    veriler = []
    # S2'den S17'ye kadar tüm denekleri tara
    for i in range(2, 18):
        sub = f"S{i}"
        yol = os.path.join(ana_yol, sub, f"{sub}.pkl")

        if os.path.exists(yol):
            try:
                with open(yol, 'rb') as f:
                    data = pickle.load(f, encoding='latin1')

                c = data['signal']['chest']
                # Master Özellikler (Ortalama, Max, Standart Sapma)
                ozet = {
                    'Hasta_ID': sub,
                    'EKG_Ort': np.mean(c['ECG']),
                    'EDA_Ort': np.mean(c['EDA']),
                    'Sicaklik_Ort': np.mean(c.get('Temp', c.get('temp', c.get('TEMP')))),
                    'Ivme_X_Ort': np.mean(c['ACC'][:, 0]),
                    'Stres_Durumu_Yuzde': (data['label'] == 2).mean() * 100
                }
                veriler.append(ozet)
                print(f"✅ {sub} verisi okundu.")
            except Exception as e:
                print(f"❌ {sub} okunurken hata: {e}")
        else:
            print(f"⚠️ {sub} bulunamadı (Yol: {yol})")

    if veriler:
        df = pd.DataFrame(veriler)
        df.to_excel("WESAD_MASTER_LISTESI.xlsx", index=False)
        print("🎉 BAŞARI: WESAD_MASTER_LISTESI.xlsx oluşturuldu!")
    else:
        print("🚨 HATA: Hiçbir WESAD dosyası işlenemedi!")


def sleep_edf_kurtar(ana_yol):
    print("\n--- Sleep-EDF İşlemi Başladı ---")
    veriler = []
    # Tüm alt klasörleri tara ve PSG dosyalarını bul
    edf_dosyalari = []
    for kok, dizin, dosyalar in os.walk(ana_yol):
        for dosya in dosyalar:
            if dosya.endswith(".edf") and "PSG" in dosya:
                edf_dosyalari.append(os.path.join(kok, dosya))

    print(f"Bulunan EDF sayısı: {len(edf_dosyalari)}")

    for yol in edf_dosyalari:
        try:
            f = pyedflib.EdfReader(yol)
            etiketler = f.getSignalLabels()
            satir = {'Kayit_Adi': os.path.basename(yol)}

            for i, etiket in enumerate(etiketler):
                if any(x in etiket for x in ['EEG', 'EOG', 'EMG']):
                    sinyal = f.readSignal(i)[:10000]  # Hız için ilk bölüm
                    satir[f"{etiket}_Ort"] = np.mean(sinyal)
                    satir[f"{etiket}_Std"] = np.std(sinyal)

            veriler.append(satir)
            f.close()
            print(f"✅ {os.path.basename(yol)} işlendi.")
        except Exception as e:
            print(f"❌ {os.path.basename(yol)} hatası: {e}")

    if veriler:
        df = pd.DataFrame(veriler)
        df.to_excel("SLEEP_EDF_MASTER_LISTESI.xlsx", index=False)
        print("🎉 BAŞARI: SLEEP_EDF_MASTER_LISTESI.xlsx oluşturuldu!")
    else:
        print("🚨 HATA: Hiçbir Sleep-EDF dosyası bulunamadı!")


#bulunurken sorun çıkaranlar
wesad_yolu = r"D:\WESAD\WESAD"
sleep_yolu = r"D:\sleep-edf-database-expanded-1.0.0"

wesad_kurtar(wesad_yolu)
sleep_edf_kurtar(sleep_yolu)