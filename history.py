from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Fungsi untuk membaca dan memproses data
def process_data():
    # Mengimpor file CSV dari Google Drive
    file_path = 'mean.csv'

    # Menentukan delimiter titik koma
    data = pd.read_csv(file_path, sep=';')

    # Mendapatkan daftar unik negara dan komoditas
    negara_komoditas = data.groupby(['Negara', 'Komoditas']).size().reset_index(name='count')

    # Mengelompokkan komoditas berdasarkan negara
    negara_komoditas_grouped = negara_komoditas.groupby('Negara')['Komoditas'].apply(', '.join).reset_index()

    return negara_komoditas_grouped

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/header.html')
def header():
    return render_template('header.html')

@app.route('/footer.html')
def footer():
    return render_template('footer.html')
@app.route('/history')
def history():
    # Memproses data
    negara_komoditas_grouped = process_data()
    
    # Menyimpan data ke dalam dictionary untuk dilewatkan ke template
    data_dict = {'countries': []}
    for _, row in negara_komoditas_grouped.iterrows():
        data_dict['countries'].append({'negara': row['Negara'], 'komoditas': row['Komoditas']})

    return render_template('history.html', data=data_dict)

if __name__ == '__main__':
    app.run(debug=True)
