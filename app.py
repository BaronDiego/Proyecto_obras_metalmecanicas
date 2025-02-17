import numpy as np
import pandas as pd
from dash import Dash, html, dcc,Input, Output, callback, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_ag_grid as dag



# Cargar datos
df_proyectos = pd.read_excel('data.xlsx', sheet_name='proyectos')
df_tareas = pd.read_excel('data.xlsx', sheet_name='data', header=1).sort_values(by="Fecha Inicio")
df_resumen = pd.read_excel('data.xlsx', sheet_name='resumen')
df_tareas['Planeado'] = (df_tareas['Planeado'] * 100).astype(int)
df_tareas['Ejecutado'] = (df_tareas['Ejecutado'] * 100).astype(int)
df_tareas['Diferencia'] = (df_tareas['Diferencia'] * 100).astype(int)
df_proyectos['Planeado'] = (df_proyectos['Planeado'] * 100).astype(int)
df_proyectos['Ejecutado'] = (df_proyectos['Ejecutado'] * 100).astype(int)
df_resumen['programdo'] = (df_resumen['programdo'] * 100).astype(int)
df_resumen['ejecutado'] = (df_resumen['ejecutado'] * 100).astype(float)
# Inicializar la app Dash

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# if using the vizro theme
vizro_bootstrap = "https://cdn.jsdelivr.net/gh/mckinsey/vizro@main/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css?v=2"

app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ, dbc.icons.FONT_AWESOME])
# MORPH - QUARTZ - SLATE -  SOLAR - SUPERHERO - VAPOR -  CYBORG

app.title = 'Dashboard de Proyectos de Construcción'

header = html.Div(
    #className="bg-primary p-2 mb-2 text-center",
    children=[
        html.H1('Dashboard de Proyectos de Construcción - Proyectos Meltalmecánicos', style={'textAlign': 'center'}),
        html.P('DashBoard para el análisis, seguimiento y control de proyectos en el sector metalmecánico (adaptable a otro sector de la infraestructura).', style={'textAlign': 'center'}),
        ],
    style={'padding': '7px'}
)

# Primera sección
titulo_seccion_1 = html.H4('SEGUIMIENTO DE PROYECTOS', style={'textAlign': 'center'})

@app.callback(
    [Output('gantt-chart', 'figure'),
     Output('costos-chart', 'figure'),
     Output('tbl_out', 'children'),
     Output('bar_costos', 'figure'),
     Output('inicio_proy', 'children'),
     Output('fin_proy', 'children'),
     Output('dura_proy', 'children'),
     Output('costo_proy', 'children'),
     Output('planeado_proy', 'children'),
     Output('ejecutado_proy', 'children'),
     Output('bar_1', 'figure'),
     Output('bar_2', 'figure'),
     Output('bar_3', 'figure'),
     Output('bar_4', 'figure')],
    [Input('proyecto-dropdown', 'value')]
)
def update_graphs(proyecto_id):
    # Filtrar datos
    tareas_proyecto = df_tareas[df_tareas['proyecto_id'] == proyecto_id]
    curva_s = df_resumen[df_resumen['proyecto_id'] == proyecto_id]
    nombre_proyecto = df_proyectos[df_proyectos['proyecto_id'] == proyecto_id]
    tabla = df_tareas[df_tareas['proyecto_id'] == proyecto_id]
    tabla = tabla[['Nombre Tarea', 'Fecha Inicio', 'Fecha Fin', 'Duración (días)','Costo (USD)','Planeado','Ejecutado', 'Diferencia','Estado']]
    tabla['Fecha Inicio'] = pd.to_datetime(tabla['Fecha Inicio']).dt.date
    tabla['Fecha Fin'] = pd.to_datetime(tabla['Fecha Fin']).dt.date
    info_proyecto = df_proyectos[df_proyectos['proyecto_id']==proyecto_id]
    inicio_proyecto = pd.to_datetime(info_proyecto['inicio_proyecto']).dt.date
    fin_proyecto = pd.to_datetime(info_proyecto['fin_proyecto']).dt.date
    duracion_proyecto = info_proyecto['duracion_proyecto'].astype(str) + " Días"
    costo_proyecto = info_proyecto['costo_proyecto']
    planeado_proyecto = info_proyecto['Planeado'].astype(str) + " %"
    ejecutado_proyecto =  info_proyecto['Ejecutado'].astype(str) + " %"
    resumen_costos_data = info_proyecto[["nombre_proyecto","Costo Planeado", "Costo Ejecutado", "Costo Real"]]

    
    # Gráfico de Gantt
    gantt_fig = px.timeline(
        tareas_proyecto,
        x_start="Fecha Inicio",
        x_end="Fecha Fin",
        y="Nombre Tarea",
        color="Estado",
        title=f"Cronograma de Tareas {nombre_proyecto.iloc[0,1]}",
    )
    gantt_fig.update_yaxes(autorange="reversed")
    
    # Curva S
    costos_fig = px.line(curva_s, x="Fecha", y=["programdo", "ejecutado"],title=f"Curva S {nombre_proyecto.iloc[0,1]}", labels={'value':'%'})

    # Tabla Resumen Actividades
    grid = dash_table.DataTable(tabla.to_dict('records'),[{"name": i, "id": i} for i in tabla.columns], style_table={"overflowX": "auto"})

    resumen_costos = px.bar(resumen_costos_data, x="nombre_proyecto", y=["Costo Planeado", "Costo Ejecutado", "Costo Real"], barmode="group", labels={'nombre_proyecto':'Proyecto', 'value':'Costo'})

    grafico_bar_1 = fig =px.bar(tareas_proyecto, x="Nombre Tarea", y="Diferencia", title="Relación entre el Peso % y la Diferencia en Ejecución", barmode="group", color="Peso %")
    grafico_bar_2 = px.bar(tareas_proyecto, x="Nombre Tarea", y="Ejecutado", title="Relación entre la Ejecución y el Costo", barmode="group", color="Costo (USD)")
    grafico_bar_3 = px.bar(tareas_proyecto, x="Nombre Tarea", y="Duración (días)", title="Relación entre la Duración y el Costo", barmode="group", color="Costo (USD)")
    grafico_bar_4 = px.bar(tareas_proyecto, x="Nombre Tarea", y="Diferencia", title="Relación entre la Diferencia y el Costo", barmode="group", color="Costo (USD)")
    
    return gantt_fig, costos_fig, grid, resumen_costos,inicio_proyecto, fin_proyecto, duracion_proyecto,costo_proyecto, planeado_proyecto, ejecutado_proyecto, grafico_bar_1, grafico_bar_2, grafico_bar_3, grafico_bar_4

grafico_gantt = dbc.Tab([dcc.Graph(id='gantt-chart')], label="Gantt")
curva_s = dbc.Tab([dcc.Graph(id='costos-chart', className='graph')], label="Curva S")
tabla = dbc.Tab(id='tbl_out', label="Resumen Actividades", className="text-primary")
costos = dbc.Tab([dcc.Graph(id='bar_costos', className='graph')], label="Resumen Costos")
tabs = dbc.Card(dbc.Tabs([grafico_gantt, curva_s, tabla, costos]))
tab_1 = dbc.Card(dbc.CardBody([html.H4("Fecha Inicio", className="card-title"), html.H5(id='inicio_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})
tab_2 = dbc.Card(dbc.CardBody([html.H4("Fecha Fin", className="card-title"), html.H5(id='fin_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})
tab_3 = dbc.Card(dbc.CardBody([html.H4("Duración", className="card-title"), html.H5(id='dura_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})
tab_4 = dbc.Card(dbc.CardBody([html.H4("Costo (USD)", className="card-title"), html.H5(id='costo_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})
tab_5 = dbc.Card(dbc.CardBody([html.H4("Planeado", className="card-title"), html.H5(id='planeado_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})
tab_6 = dbc.Card(dbc.CardBody([html.H4("Ejecutado", className="card-title"), html.H5(id='ejecutado_proy', className="card-subtitle")]),style={'margin-bottom': '4px'})


grafico_bar_1 = dbc.Card(dcc.Graph(id="bar_1"), style={'margin-bottom': '4px'})
grafico_bar_2 = dbc.Card(dcc.Graph(id="bar_2"), style={'margin-bottom': '4px'})
grafico_bar_3 = dbc.Card(dcc.Graph(id="bar_3"), style={'margin-bottom': '4px'})
grafico_bar_4 = dbc.Card(dcc.Graph(id="bar_4"), style={'margin-bottom': '4px'})


controls = html.Div(
    children=[
        html.H6('Seleccionar proyecto:'),
        dcc.Dropdown(
        id='proyecto-dropdown',
        options=[{'label': row['nombre_proyecto'], 'value': row['proyecto_id']} 
                 for index, row in df_proyectos.iterrows()],
        value=df_proyectos['proyecto_id'].iloc[0],
        className='text-primary'
    ),
    ],
    style={'width': '40%', 'margin': 'auto', 'textAlign': 'center'},
)

contenido_seccion_1 = html.Div(
    className='row',
    children=[
        titulo_seccion_1,
        controls,
        dbc.Row(
            children=[
                dbc.Col(html.Div(tab_1)),
                dbc.Col(html.Div(tab_2)),
                dbc.Col(html.Div(tab_3)),
                dbc.Col(html.Div(tab_4)),
                dbc.Col(html.Div(tab_5)),
                dbc.Col(html.Div(tab_6)),
                ],
            style={'margin': 'auto', 'padding': '10px', 'textAlign': 'center'}
        ),
        dbc.Row(
            className='row',
            children=[
                html.Div(
                    className='col',
                    children=[
                        tabs
                    ]       
                ),
                ],
            style={'margin': 'auto', 'padding': '10px', 'textAlign': 'center'}
        ),
        dbc.Row(
            children=[
                dbc.Col(html.Div(grafico_bar_1), className='col-md-6 col-xs-12'),
                dbc.Col(html.Div(grafico_bar_2), className='col-md-6 col-xs-12'),
            ]
        ),
        dbc.Row(
           children=[
                dbc.Col(html.Div(grafico_bar_3),className='col-md-6 col-xs-12'),
                dbc.Col(html.Div(grafico_bar_4),className='col-md-6 col-xs-12'),
            ]
        ),
    ],
    style={'margin': 'auto', 'padding': '10px'}
)











# Layout del dashboard
app.layout = html.Div(
    children=[
        header,
        contenido_seccion_1,

])

server = app.server

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)