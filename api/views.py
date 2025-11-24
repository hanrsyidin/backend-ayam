from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import joblib
import os
from .models import PredictionHistory

# HAPUS IMPORT INI: import pandas as pd 

# Load model ... (kode load model tetap sama) ...
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model_ayam_pintar.sav')
model = joblib.load(MODEL_PATH)

@csrf_exempt
def predict_egg(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- BAGIAN YANG DIUBAH (DIET PANDAS) ---
            # Model menerima input berupa Array 2 Dimensi [[nilai1, nilai2, ...]]
            # PENTING: Urutannya WAJIB SAMA PERSIS dengan saat training tadi!
            # Urutan: Ayam, Pakan, Suhu, Lembab, Cahaya, Amonia, Bising
            
            input_list = [[
                float(data.get('amount_chicken')),
                float(data.get('feed_intake')),
                float(data.get('temperature')),
                float(data.get('humidity')),
                float(data.get('light')),
                float(data.get('ammonia')),
                float(data.get('noise'))
            ]]
            
            # Prediksi langsung pakai list (gak perlu DataFrame)
            prediction = model.predict(input_list)[0]
            hasil_bulat = round(prediction)
            # ----------------------------------------

            # Simpan ke DB (Tetap sama)
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
                'message': 'Prediksi berhasil!'
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