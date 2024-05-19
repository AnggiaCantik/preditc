import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import calendar
from flask import Flask, render_template, request

app = Flask(__name__)

# Fungsi utama untuk membuat grafik
def generate_graph(komoditas, negara, data_path):
    # Mengimpor file CSV dari Google Drive
    data = pd.read_csv(data_path, sep=';')

    # Membuat objek MinMaxScaler
    scaler = MinMaxScaler()

    # Fungsi untuk menghitung regresi linear dan mencetak hasilnya
    def linear_regression(group):
        model = LinearRegression()
        X = group['Volume'].values.reshape(-1, 1)
        y = group['Tabel Harga']
        X_scaled = scaler.fit_transform(X)
        model.fit(X_scaled, y)
        return model

    regression_models = data.groupby(['Komoditas', 'Negara']).apply(linear_regression)

    def predict_price(model, additional_data, min_price):
        additional_data_scaled = scaler.transform([[additional_data]])
        predicted_price = model.predict(additional_data_scaled)
        return max(round(predicted_price[0], 1), min_price)

    MIN_PREDICTED_PRICE = 0.01
    for key, model in regression_models.items():
        if key[0].lower() == komoditas and key[1].lower() == negara:
            additional_data = 0
            predicted_prices = []
            current_year, current_month = 2024, 1
            months = []
            prices = []

            for _ in range(36):
                predicted_price = predict_price(model, additional_data, MIN_PREDICTED_PRICE)
                predicted_prices.append(predicted_price)
                additional_data = predicted_price
                months.append(f"{calendar.month_name[current_month]} {current_year}")
                prices.append(predicted_price)
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1

            plt.figure(figsize=(10, 6))
            plt.plot(months, prices, marker='o')
            plt.xticks(rotation=45, ha='right')
            plt.xlabel('Bulan Tahun')
            plt.ylabel('Harga Prediksi')
            plt.title(f'Prediksi Harga {komoditas.title()} di {negara.title()}')
            plt.tight_layout()
            plt.grid(True)
            plt.savefig('static/graph.png')
            plt.close()
            return True
    return False

@app.route('/header.html')
def header():
    return render_template('header.html')

@app.route('/footer.html')
def footer():
    return render_template('footer.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        komoditas = request.form['komoditas'].lower()
        negara = request.form['negara'].lower()
        data_path = 'mean.csv'
        if generate_graph(komoditas, negara, data_path):
            return render_template('grafikharga.html', graph=True)
        else:
            return render_template('grafikharga.html', graph=False, error="Data tidak ditemukan.")
    return render_template('grafikharga.html', graph=False)

if __name__ == '__main__':
    app.run(debug=True)
