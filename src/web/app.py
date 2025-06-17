import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

DATA_FILE = 'data/rabbitmq_log.csv'

app = dash.Dash(__name__)

# Функция для чтения и подготовки данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['timestamp', 'key', 'value'])
    df = pd.read_csv(DATA_FILE)
    # Преобразуем timestamp в datetime, если это возможно
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    except Exception:
        pass
    return df

def get_key_options(df):
    keys = df['key'].unique()
    return [{'label': str(k), 'value': k} for k in sorted(keys) if pd.notna(k) and str(k).lower() != 'nan' and str(k).strip() != '']

app.layout = html.Div([
    html.H1('Визуализация данных из RabbitMQ'),
    dcc.Dropdown(id='key-dropdown', placeholder='Выберите key'),
    dcc.Graph(id='main-graph'),
    dcc.Interval(id='interval', interval=10*1000, n_intervals=0),
])

@app.callback(
    Output('key-dropdown', 'options'),
    Output('key-dropdown', 'value'),
    Input('interval', 'n_intervals')
)
def update_dropdown(n):
    df = load_data()
    options = get_key_options(df)
    value = options[0]['value'] if options else None
    return options, value

@app.callback(
    Output('main-graph', 'figure'),
    Input('key-dropdown', 'value'),
    Input('interval', 'n_intervals')
)
def update_graph(selected_key, n):
    df = load_data()
    if selected_key is None or df.empty:
        return px.line(title='Нет данных для отображения')
    df = df[df['key'] == selected_key]
    # Попробуем преобразовать value в число
    try:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
    except Exception:
        pass
    fig = px.line(df, x='timestamp', y='value', title=f'График для key={selected_key}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 