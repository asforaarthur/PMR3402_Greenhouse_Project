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
graph = st.selectbox("Selecione o Tipo de Gráfico:", ('Gráfico de Barras', 'Gráfico de Linhas'))

def fetch_data():
    """Buscar dados do Supabase."""
    response = supabase.table('maintable').select('*').execute()
    return response.data

def process_data(data):
    """Processar dados para análise."""
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])  # Converter para datetime
    df['date'] = df['created_at'].dt.date
    daily_data = df.groupby('date').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'moisture': 'mean'
    }).reset_index()
    return daily_data

def init_plot():
    """Inicializar o gráfico e rotular eixos."""
    plt.style.use('ggplot')
    plt.figure('Monitoramento de Plantas')
    plt.xlabel('Dia')
    plt.ylabel('Temperatura (°C)')
    plt.title(f"Previsão Semanal - {location}")
    plt.xticks(rotation=45)

def plot_temperature(daily_data):
    """Plotar gráfico de temperatura."""
    days = pd.to_datetime(daily_data['date'])  # Converter para Timestamp
    temp_min = daily_data['temperature'].min()  # Temperatura mínima diária
    temp_max = daily_data['temperature'].max()  # Temperatura máxima diária
    
    if graph == 'Gráfico de Barras':
        fig, ax = plt.subplots()
        bar_width = 0.35
        opacity = 0.8
        
        bar_x = ax.bar(days - pd.Timedelta(days=0.25), temp_min, bar_width, alpha=opacity, color='#5cb85c', label='Min')
        bar_y = ax.bar(days + pd.Timedelta(days=0.25), temp_max, bar_width, alpha=opacity, color='#ff5349', label='Max')
        
        ax.set_xlabel('Dia')
        ax.set_ylabel('Temperatura (°C)')
        ax.set_title(f'Previsão Semanal - {location}')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        return bar_x, bar_y
    
    elif graph == 'Gráfico de Linhas':
        plt.plot(days, daily_data['temperature'], label='Temperatura', color='#42bff4', marker='o')
        plt.title(f'Previsão Semanal - {location}')
        plt.legend(fontsize='x-small')
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot(plt.show())

def label_xaxis():
    """Rotular eixo X no formato 'mm/dd'."""
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

def show_temp_alerts(daily_data):
    """Mostrar alertas de temperatura."""
    for index, row in daily_data.iterrows():
        temp = row['temperature']
        date = row['date']
        if temp < min_temp:
            st.warning(f'Temperatura muito baixa em {date}: {temp:.2f}°C')
        elif temp > max_temp:
            st.error(f'Temperatura muito alta em {date}: {temp:.2f}°C')
        else:
            st.success(f'Temperatura adequada em {date}: {temp:.2f}°C')

if st.button('Buscar Dados'):
    if location == '':
        st.warning('Por favor, insira o nome da planta!')
    else:
        try:
            data = fetch_data()
            if data:
                daily_data = process_data(data)
                st.subheader('Dados Agregados Diários')
                st.write("Grandezas médias diárias para os dias.")
                st.write(daily_data)

                init_plot()
                plot_temperature(daily_data)
                label_xaxis()
                show_temp_alerts(daily_data)
            else:
                st.error('Nenhum dado encontrado.')
        except Exception as e:
            st.exception(f"Erro ao buscar dados: {e}")

st.text("© 2024 - Todos os direitos reservados - Grupo D")