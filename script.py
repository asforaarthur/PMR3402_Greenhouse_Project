import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime
import matplotlib.dates as mdates

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da Supabase
url = "https://puhilvgiiyeqyorktlpx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB1aGlsdmdpaXllcXlvcmt0bHB4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxODMyODU0MywiZXhwIjoyMDMzOTA0NTQzfQ.OzJk5YcP9fiiLHRdaacloNa-pBRgQ2RX80-dIgsidKY"

# Criação do cliente Supabase
supabase: Client = create_client(url, key)

st.title("🌿 PMR3402 - Monitoramento de Plantas 🌱")
st.write("## Feito pelo Grupo D")
st.write("##")

st.write("### Insira os detalhes da planta e escolha o tipo de gráfico:")

location = st.text_input("Nome da Planta:", "")
min_temp = st.number_input("Temperatura Mínima Suportada (°C)", value=10)
max_temp = st.number_input("Temperatura Máxima Suportada (°C)", value=30)
min_humidity_ar = st.number_input("Umidade do Mínima Suportada (%)", value=30)
max_humidity_ar = st.number_input("Umidade do Máxima Suportada (%)", value=70)
graph = st.selectbox("Selecione o Tipo de Gráfico:", ('Gráfico de Barras', 'Gráfico de Linhas'))

# Seleção do intervalo de datas
start_date = st.date_input("Data de Início", value=pd.to_datetime("2023-01-01"))
end_date = st.date_input("Data de Fim", value=pd.to_datetime("2023-12-31"))

def fetch_data():
    """Buscar dados do Supabase."""
    response = supabase.table('maintable').select('*').execute()
    return response.data

def process_data(data):
    """Processar dados para análise, filtrando dados errôneos."""
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])  # Converter para datetime
    df['date'] = df['created_at'].dt.date
    
    # Filtrar dados errôneos
    df = df[(df['temperature'] >= min_temp) & (df['temperature'] <= max_temp) & (df['humidity'] >= min_humidity_ar) & (df['humidity'] <= max_humidity_ar)]
    
    # Filtrar valores de umidade do solo e do ar
    df['moisture'] = df['moisture'] / 100  # Converter a umidade do solo para a mesma escala que a umidade do ar
    df = df[(df['moisture'] >= 30) & (df['moisture'] <= max_humidity_ar)]
    
    daily_data = df.groupby('date').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'moisture': 'mean'
    }).reset_index()
    
    return daily_data

def init_plot(title):
    """Inicializar o gráfico e rotular eixos."""
    plt.style.use('ggplot')
    plt.figure('Monitoramento de Plantas')
    plt.xlabel('Dia')
    plt.ylabel('Valor')
    plt.title(title)
    plt.xticks(rotation=45)

def plot_bars(daily_data, value_column, min_value, max_value, y_label, title):
    """Plotar gráfico de barras."""
    days = pd.to_datetime(daily_data['date'])  # Converter para Timestamp
    values = daily_data[value_column]
    
    fig, ax = plt.subplots()
    bar_width = 0.35
    opacity = 0.8
    
    bar_x = ax.bar(days - pd.Timedelta(days=0.25), values, bar_width, alpha=opacity, color='#5cb85c', label='Min')
    bar_y = ax.bar(days + pd.Timedelta(days=0.25), values, bar_width, alpha=opacity, color='#ff5349', label='Max')
    
    ax.set_xlabel('Dia')
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.legend()
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    return bar_x, bar_y

def plot_temperature(daily_data):
    """Plotar gráfico de temperatura."""
    days = pd.to_datetime(daily_data['date'])  # Converter para Timestamp
    
    if graph == 'Gráfico de Barras':
        plot_bars(daily_data, 'temperature', min_temp, max_temp, 'Temperatura (°C)', f'Previsão Semanal - {location} - Temperatura')
    
    elif graph == 'Gráfico de Linhas':
        plt.plot(days, daily_data['temperature'], label='Temperatura Média', color='#42bff4', marker='o')
        plt.title(f'Previsão Semanal - {location} - Temperatura')
        plt.xlabel('Dia')
        plt.ylabel('Temperatura (°C)')
        plt.legend(fontsize='x-small')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

def plot_humidity_ar(daily_data):
    """Plotar gráfico de umidade do ar."""
    days = pd.to_datetime(daily_data['date'])  # Converter para Timestamp
    
    if graph == 'Gráfico de Barras':
        plot_bars(daily_data, 'humidity', min_humidity_ar, max_humidity_ar, 'Umidade do Ar (%)', f'Previsão Semanal - {location} - Umidade do Ar')
    
    elif graph == 'Gráfico de Linhas':
        plt.plot(days, daily_data['humidity'], label='Umidade do Ar Média', color='#ffb347', marker='o')
        plt.title(f'Previsão Semanal - {location} - Umidade do Ar')
        plt.xlabel('Dia')
        plt.ylabel('Umidade do Ar (%)')
        plt.legend(fontsize='x-small')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

def plot_moisture(daily_data):
    """Plotar gráfico de umidade do solo."""
    days = pd.to_datetime(daily_data['date'])  # Converter para Timestamp
    
    if graph == 'Gráfico de Barras':
        plot_bars(daily_data, 'moisture', 0.3, max_humidity_ar / 100, 'Umidade do Solo (%)', f'Previsão Semanal - {location} - Umidade do Solo')
    
    elif graph == 'Gráfico de Linhas':
        plt.plot(days, daily_data['moisture'], label='Umidade do Solo Média', color='#ff6347', marker='o')
        plt.title(f'Previsão Semanal - {location} - Umidade do Solo')
        plt.xlabel('Dia')
        plt.ylabel('Umidade do Solo (%)')
        plt.legend(fontsize='x-small')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

def label_xaxis():
    """Rotular eixo X no formato 'mm/dd'."""
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

def show_temp_alerts(daily_data):
    """Mostrar alertas de temperatura."""
    for index, row in daily_data.iterrows():
        temp = row['temperature']
        date = row['date'].strftime('%Y-%m-%d')  # Formatando a data para 'YYYY-MM-DD'
        if temp < min_temp:
            st.warning(f'Temperatura muito baixa em {date}: {temp:.2f}°C')
        elif temp > max_temp:
            st.error(f'Temperatura muito alta em {date}: {temp:.2f}°C')
        else:
            st.success(f'Temperatura adequada em {date}: {temp:.2f}°C')

def show_humidity_ar_alerts(daily_data):
    """Mostrar alertas de umidade do ar."""
    for index, row in daily_data.iterrows():
        humidity_ar = row['humidity']
        date = row['date'].strftime('%Y-%m-%d')  # Formatando a data para 'YYYY-MM-DD'
        if humidity_ar < min_humidity_ar:
            st.warning(f'Umidade do ar muito baixa em {date}: {humidity_ar:.2f}%')
        elif humidity_ar > max_humidity_ar:
            st.error(f'Umidade do ar muito alta em {date}: {humidity_ar:.2f}%')
        else:
            st.success(f'Umidade do ar adequada em {date}: {humidity_ar:.2f}%')

def show_moisture_alerts(daily_data):
    """Mostrar alertas de umidade do solo."""
    for index, row in daily_data.iterrows():
        moisture = row['moisture']
        date = row['date'].strftime('%Y-%m-%d')  # Formatando a data para 'YYYY-MM-DD'
        if moisture < 0.3:
            st.warning(f'Umidade do solo muito baixa em {date}: {moisture:.2f}')
        elif moisture > max_humidity_ar / 100:
            st.error(f'Umidade do solo muito alta em {date}: {moisture:.2f}')
        else:
            st.success(f'Umidade do solo adequada em {date}: {moisture:.2f}')

if st.button('Buscar Dados'):
    if location == '':
        st.warning('Por favor, insira o nome da planta!')
    elif start_date > end_date:
        st.error('Data de início não pode ser maior que a data de fim!')
    else:
        try:
            data = fetch_data()
            if data:
                daily_data = process_data(data)
                
                # Converter as datas do dataframe para o tipo correto
                daily_data['date'] = pd.to_datetime(daily_data['date'])
                
                # Filtrar dados pelo intervalo de datas
                daily_data = daily_data[(daily_data['date'] >= pd.to_datetime(start_date)) & (daily_data['date'] <= pd.to_datetime(end_date))]

                if daily_data.empty:
                    st.error('Nenhum dado encontrado no intervalo de datas selecionado.')
                else:
                    st.subheader('Dados Agregados Diários')
                    st.write("Grandezas médias diárias para os dias selecionados.")
                    st.write(daily_data)

                    plot_temperature(daily_data)
                    plot_humidity_ar(daily_data)
                    plot_moisture(daily_data)
                    label_xaxis()
                    show_temp_alerts(daily_data)
                    show_humidity_ar_alerts(daily_data)
                    show_moisture_alerts(daily_data)
            else:
                st.error('Nenhum dado encontrado.')
        except Exception as e:
            st.exception(f"Erro ao buscar dados: {e}")

st.text("© 2024 - Todos os direitos reservados - Grupo D")
