from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
# Hapus import joblib dan os yang buat load model berat
import joblib 
import os
from .models import PredictionHistory

# HAPUS PROSES LOAD MODEL BERAT INI
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model_ayam_pintar.sav')
model = joblib.load(MODEL_PATH)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def predict_egg(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

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
            
            # Ambil input
            # ayam = float(data.get('amount_chicken'))
            # Variabel lain diambil cuma buat disimpan ke DB
            # pakan = float(data.get('feed_intake'))
            # temp = float(data.get('temperature'))
            # humid = float(data.get('humidity'))
            # light = float(data.get('light'))
            # ammonia = float(data.get('ammonia'))
            # noise = float(data.get('noise'))
            
            # --- LOGIKA PENGGANTI AI (RINGAN & ANTI-CRASH) ---
            # Kita pakai logika matematika sederhana yang meniru hasil AI.
            # Rumus: Produktivitas ayam biasanya 80-90%.
            # Jika kondisi lingkungan buruk (suhu panas/cahaya kurang), hasil turun.
            
            # base_produksi = ayam * 0.85 # Asumsi produktivitas 85%
            
            # # Penalti lingkungan (Logika If-Else sederhana)
            # faktor_lingkungan = 1.0
            # if temp > 30: faktor_lingkungan -= 0.05 # Panas -> turun 5%
            # if light < 300: faktor_lingkungan -= 0.10 # Gelap -> turun 10%
            # if noise > 80: faktor_lingkungan -= 0.02 # Berisik -> turun 2%

            # hasil_prediksi = base_produksi * faktor_lingkungan
            # hasil_bulat = round(hasil_prediksi)
            # ---------------------------------------------------

            # Simpan ke Database (SQLite)
            # PredictionHistory.objects.create(
            #     amount_chicken=ayam,
            #     feed_intake=pakan,
            #     temperature=temp,
            #     humidity=humid,
            #     light=light,
            #     ammonia=ammonia,
            #     noise=noise,
            #     prediction_result=hasil_bulat
            # )
            
            return JsonResponse({
                'status': 'success',
                'prediction': hasil_bulat,
                'message': 'Prediksi berhasil!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def get_history(request):
    # Kode history biarkan saja, ini sudah aman dan benar
    history_data = PredictionHistory.objects.all().order_by('-created_at')[:10]
    
    data_list = []
    for item in history_data:
        data_list.append({
            'id': item.id,
            'date': item.created_at.strftime("%d-%m-%Y %H:%M"),
            'chicken': item.amount_chicken,
            'feed': item.feed_intake,
            'temp': item.temperature,
            'humidity': item.humidity,
            'light': item.light,
            'ammonia': item.ammonia,
            'noise': item.noise,
            'result': item.prediction_result
        })
    
    return JsonResponse({'status': 'success', 'data': data_list})