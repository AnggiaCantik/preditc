from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline
import re
import io
import base64

app = Flask(__name__)

# Load data
file_path = 'median.csv'
data = pd.read_csv(file_path, sep=';')
data.dropna(subset=['Volume', 'Tabel Harga'], inplace=True)

def linear_regression_plot(komoditas, negara):
    komoditas = re.sub(r'\s+', ' ', komoditas.strip())
    negara = re.sub(r'\s+', ' ', negara.strip())

    filtered_data = data[(data['Komoditas'].str.upper() == komoditas.upper()) & (data['Negara'].str.upper() == negara.upper())]

    if not filtered_data.empty:
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(filtered_data[['Volume']])
        y = filtered_data['Tabel Harga']

        model = make_pipeline(LinearRegression())
        model.fit(X_scaled, y)

        beta_0 = model.named_steps['linearregression'].intercept_
        beta_1 = model.named_steps['linearregression'].coef_[0]

        equation = f"Y = {beta_0:.2f} + {beta_1:.2f}X"

        plt.figure(figsize=(10, 6))
        plt.scatter(X_scaled, y, color='blue', label='Data')
        plt.plot(X_scaled, model.predict(X_scaled), color='red', label='Regresi Linear')
        plt.title(f'Regresi Linear: Volume vs Harga ({komoditas} di {negara})')
        plt.xlabel('Volume (Scaled)')
        plt.ylabel('Harga')
        plt.legend()
        plt.grid(True)

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return equation, graph_url
    else:
        return None, None

@app.route('/header.html')
def header():
    return render_template('header.html')

@app.route('/footer.html')
def footer():
    return render_template('footer.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        komoditas = request.form['komoditas']
        negara = request.form['negara']

        equation, graph_url = linear_regression_plot(komoditas, negara)

        if equation:
            return jsonify({'equation': equation, 'graph_url': graph_url})
        else:
            return jsonify({'error': f"Tidak ada data yang cocok untuk komoditas {komoditas} di {negara}."})

    return render_template('linear_regression.html')

if __name__ == '__main__':
    app.run(debug=True)
