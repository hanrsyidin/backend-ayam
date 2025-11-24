from django.db import models

# Create your models here.
from django.db import models

class PredictionHistory(models.Model):
    # Data Input
    amount_chicken = models.IntegerField()
    feed_intake = models.IntegerField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    light = models.FloatField()
    ammonia = models.FloatField()
    noise = models.FloatField()
    
    # Hasil Prediksi
    prediction_result = models.IntegerField()
    
    # Waktu Pencatatan (Otomatis terisi saat disimpan)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediksi {self.created_at} - Hasil: {self.prediction_result}"