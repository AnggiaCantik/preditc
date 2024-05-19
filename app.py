from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# Mengimpor file CSV
file_path = 'median.csv'
data = pd.read_csv(file_path, sep=';')

# Inisialisasi MinMaxScaler
scaler = MinMaxScaler()

# Fungsi prediksi harga
def linear_regression(group):
    # Buat model regresi linear
    model = LinearRegression()

    # Ubah bentuk data
    X = group['Volume'].values.reshape(-1, 1)
    y = group['Tabel Harga']

    # Normalisasi data
    X_scaled = scaler.fit_transform(X)

    # Fitting model
    model.fit(X_scaled, y)

    return model

regression_models = data.groupby(['Komoditas', 'Negara']).apply(linear_regression)

def predict_price(model, additional_data, min_price):
    additional_data_scaled = scaler.transform([[additional_data]])
    predicted_price = model.predict(additional_data_scaled)
    return max(round(predicted_price[0], 2), min_price)

@app.route('/header.html')
def header():
    return render_template('header.html')

@app.route('/footer.html')
def footer():
    return render_template('footer.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    komoditas_input = request.form['komoditas'].lower()
    volume_input = float(request.form['volume'])
    tahun = int(request.form['tahun'])
    bulan = int(request.form['bulan'])

    table_data = []
    MIN_PREDICTED_PRICE = 0.01
    for key, model in regression_models.items():
        additional_data = 0
        predicted_prices = []
        current_year, current_month = 2024, 1
        for _ in range(36):  # Loop through 36 months (3 years)
            predicted_price = predict_price(model, additional_data, MIN_PREDICTED_PRICE)
            predicted_prices.append(predicted_price)
            additional_data = predicted_price
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        table_data.append([key[0], key[1], *predicted_prices])

    filtered_table_data = []
    for data_row in table_data:
        komoditas, negara, *predicted_prices = data_row
        if komoditas.lower() == komoditas_input:
            if tahun == 2024:
                filtered_price = predicted_prices[bulan - 1]
            elif tahun == 2025:
                filtered_price = predicted_prices[12 + bulan - 1]
            elif tahun == 2026:
                filtered_price = predicted_prices[24 + bulan - 1]
            else:
                continue
            harga_jual = round(filtered_price * volume_input, 2)
            filtered_table_data.append([negara, filtered_price, harga_jual])

    return render_template('result.html', filtered_table_data=filtered_table_data, komoditas_input=komoditas_input, volume_input=volume_input, bulan=bulan, tahun=tahun)

if __name__ == "__main__":
    app.run(debug=True)
