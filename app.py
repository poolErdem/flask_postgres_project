from flask import Flask, jsonify
import psycopg2
from dotenv import load_dotenv
import os
from db import get_db_connection 

# load environment variables from .env file
load_dotenv()

app = Flask(__name__)


@app.route('/energy-prices', methods=['GET'])
def get_energy_prices():
    region = request.args.get('region')  # URL query parameter for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = "SELECT region, timestamp, price_per_mwh FROM energy_prices WHERE TRUE"
    params = []
    
    if region:
        query += " AND region = %s"
        params.append(region)
    
    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = [
        {"region": row[0], "timestamp": row[1].isoformat(), "price_per_mwh": float(row[2])}
        for row in rows
    ]
    return jsonify(results)


from flask import request

@app.route('/energy-prices', methods=['POST'])
def add_energy_price():
    new_data = request.get_json()  # Veriyi JSON formatında al
    region = new_data['region']
    timestamp = new_data['timestamp']
    price_per_mwh = new_data['price_per_mwh']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO energy_prices (region, timestamp, price_per_mwh) VALUES (%s, %s, %s)",
                (region, timestamp, price_per_mwh))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Data added successfully!"}), 201


if __name__ == '__main__':
    app.run(debug=True)
