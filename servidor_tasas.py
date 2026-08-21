from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(_name_)
CORS(app)  # Esto permite que tu página de Netlify consulte la API sin bloqueos de seguridad

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
def obtener_tasas():
    monedas = ['COP', 'PEN', 'CLP', 'VES']
    tasas_resultado = {}
    
    for fiat in monedas:
        tasa_compra = obtener_tasa_ajustada(fiat, 'BUY')
        tasa_venta = obtener_tasa_ajustada(fiat, 'SELL')
        
        tasas_resultado[fiat] = {
            "compraUSDT": tasa_compra,
            "ventaVES": tasa_venta # O la referencia que estés usando para el cálculo cruzado
        }
        
    return jsonify(tasas_resultado)

if _name_ == "_main_":
    app.run(host='0.0.0.0', port=5000)
