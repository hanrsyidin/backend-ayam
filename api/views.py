from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import joblib
import pandas as pd
import os
from .models import PredictionHistory  # <--- Import Model History

# Load model SATU KALI SAJA saat server nyala (biar cepat)
# Pastikan path file .sav benar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model_ayam_pintar.sav')
model = joblib.load(MODEL_PATH)

@csrf_exempt
def predict_egg(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 1. Proses Prediksi (Sama kayak tadi)
            input_data = pd.DataFrame([{
                'Amount_of_chicken': float(data.get('amount_chicken')),
                'Amount_of_Feeding': float(data.get('feed_intake')),
                'Temperature': float(data.get('temperature')),
                'Humidity': float(data.get('humidity')),
                'Light_Intensity': float(data.get('light')),
                'Ammonia': float(data.get('ammonia')),
                'Noise': float(data.get('noise')),
            }])
            prediction = model.predict(input_data)[0]
            hasil_bulat = round(prediction)

            # 2. SIMPAN KE DATABASE (BARU!)
            PredictionHistory.objects.create(
                amount_chicken=data.get('amount_chicken'),
                feed_intake=data.get('feed_intake'),
                temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                light=data.get('light'),
                ammonia=data.get('ammonia'),
                noise=data.get('noise'),
                prediction_result=hasil_bulat
            )
            
            return JsonResponse({
                'status': 'success',
                'prediction': hasil_bulat,
                'message': 'Prediksi berhasil dan tersimpan!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# 3. Fungsi Baru: Ambil Data History
def get_history(request):
    # Ambil 10 data terbaru
    history_data = PredictionHistory.objects.all().order_by('-created_at')[:10]
    
    data_list = []
    for item in history_data:
        data_list.append({
            'id': item.id,
            'date': item.created_at.strftime("%d-%m-%Y %H:%M"),
            # --- UPDATE: Masukkan semua kolom input ---
            'chicken': item.amount_chicken,
            'feed': item.feed_intake,
            'temp': item.temperature,
            'humidity': item.humidity,
            'light': item.light,
            'ammonia': item.ammonia,
            'noise': item.noise,
            # ----------------------------------------
            'result': item.prediction_result
        })
    
    return JsonResponse({'status': 'success', 'data': data_list})