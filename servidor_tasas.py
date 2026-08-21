from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permite que Netlify lea los datos sin bloqueos

def obtener_tasa_ajustada(fiat, trade_type):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": fiat,
        "tradeType": trade_type, 
        "rows": 20,
        "page": 1,
        "payTypes": []
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("success") and data.get("data"):
            anuncios = data["data"]
            precios = [float(item["adv"]["price"]) for item in anuncios]
            
            if len(precios) > 2:
                precios_sanos = precios[2:]
                promedio_base = sum(precios_sanos) / len(precios_sanos)
            elif len(precios) > 0:
                promedio_base = precios[-1]
            else:
                return 0

            if trade_type == 'BUY':
                tasa_final = promedio_base * 1.005
            else:
                tasa_final = promedio_base * 0.995
                
            return tasa_final
            
    except Exception as e:
        print(f"Error para {fiat}: {e}")
    return 0

@app.route('/tasas', methods=['GET'])
def tasas():
    monedas = ['COP', 'PEN', 'CLP', 'VES']
    resultado = {}
    
    for fiat in monedas:
        tasa_compra = obtener_tasa_ajustada(fiat, 'BUY')
        tasa_venta = obtener_tasa_ajustada(fiat, 'SELL')
        
        resultado[fiat] = {
            "compraUSDT": tasa_compra,
            "ventaVES": tasa_venta,
            "margen": 0.005
        }
        
    return jsonify(resultado)

app = Flask(__name__)
# ... (todo tu código) ...

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
