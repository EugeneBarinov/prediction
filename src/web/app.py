import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

DATA_FILE = 'data/rabbitmq_log.csv'

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Функция для чтения и подготовки данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['timestamp', 'key', 'value'])
    df = pd.read_csv(DATA_FILE)
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    except Exception:
        pass
    return df

def get_key_options(df):
    keys = df['key'].unique()
    return [{'label': str(k), 'value': k} for k in sorted(keys) if pd.notna(k) and str(k).lower() != 'nan' and str(k).strip() != '']

# Создаем макет с несколькими графиками и элементами управления
app.layout = html.Div([
    html.H1('Мониторинг параметров эксгаустера', style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        html.Div([
            html.Label('Выберите параметр:'),
            dcc.Dropdown(id='key-dropdown', placeholder='Выберите параметр'),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label('Временной интервал:'),
            dcc.Dropdown(
                id='time-range',
                options=[
                    {'label': 'Последние 5 минут', 'value': '5min'},
                    {'label': 'Последние 15 минут', 'value': '15min'},
                    {'label': 'Последний час', 'value': '1hour'},
                    {'label': 'Последние 6 часов', 'value': '6hours'},
                    {'label': 'Последние 24 часа', 'value': '24hours'}
                ],
                value='15min'
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
    ], style={'margin': '20px'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='main-graph'),
        ], style={'width': '100%'}),
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='gauge-graph'),
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='histogram-graph'),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    
    dcc.Interval(id='interval', interval=5*1000, n_intervals=0),
    
    html.Div(id='status-indicator', style={'textAlign': 'center', 'margin': '20px'})
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
    Output('gauge-graph', 'figure'),
    Output('histogram-graph', 'figure'),
    Output('status-indicator', 'children'),
    Input('key-dropdown', 'value'),
    Input('time-range', 'value'),
    Input('interval', 'n_intervals')
)
def update_graphs(selected_key, time_range, n):
    df = load_data()
    
    if selected_key is None or df.empty:
        empty_fig = px.line(title='Нет данных для отображения')
        return empty_fig, empty_fig, empty_fig, "Статус: Ожидание данных"
    
    # Фильтрация по временному диапазону
    now = datetime.now()
    if time_range == '5min':
        start_time = now - timedelta(minutes=5)
    elif time_range == '15min':
        start_time = now - timedelta(minutes=15)
    elif time_range == '1hour':
        start_time = now - timedelta(hours=1)
    elif time_range == '6hours':
        start_time = now - timedelta(hours=6)
    else:  # 24hours
        start_time = now - timedelta(hours=24)
    
    df = df[df['timestamp'] >= start_time]
    df = df[df['key'] == selected_key]
    
    try:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
    except Exception:
        pass
    
    # Основной график
    main_fig = px.line(df, x='timestamp', y='value', 
                      title=f'График параметра: {selected_key}',
                      template='plotly_white')
    main_fig.update_layout(
        xaxis_title='Время',
        yaxis_title='Значение',
        hovermode='x unified'
    )
    
    # График-индикатор
    current_value = df['value'].iloc[-1] if not df.empty else 0
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_value,
        title={'text': f"Текущее значение: {selected_key}"},
        gauge={'axis': {'range': [df['value'].min(), df['value'].max()] if not df.empty else [0, 100]}}
    ))
    
    # Гистограмма
    hist_fig = px.histogram(df, x='value',
                           title=f'Распределение значений: {selected_key}',
                           template='plotly_white')
    
    # Статус
    status = "Статус: Данные обновлены" if not df.empty else "Статус: Нет данных"
    
    return main_fig, gauge_fig, hist_fig, status

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 