from app import app
from typing import TypedDict
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
import sys
from flask import url_for
# Nome della squadra passato come argomento
n_sq = sys.argv[1] if len(sys.argv) > 1 else None

if not n_sq:
    print("Errore: nessun nome squadra fornito.")
    sys.exit(1)


# Definizione del TypedDict
class Ball(TypedDict):
    Link: str
    Top: int
    Left: int

# Percorso della directory dello script
script_dir = os.getcwd()  # Utilizza la directory corrente come base

# Directory dei template
template_dir = os.path.join(script_dir, 'templates')

# Inizializza l'ambiente Jinja2 con il percorso corretto
env = Environment(loader=FileSystemLoader(template_dir))

env.globals['url_for'] = url_for

with app.app_context():
    # Carica i template
    template = env.get_template('template.html')
    template_squadra = env.get_template('template_squadra.html')

    # Percorso base dei dati
    base_path = os.path.join(script_dir,'static', 'campionato', 'squadre')

    # Funzioni per la generazione dinamica dei percorsi
    def get_squadra_dir(squadra: str) -> str:
        return os.path.join(base_path, squadra)

    def get_giocatore_dir(squadra: str, giocatore: str) -> str:
        return os.path.join(get_squadra_dir(squadra), giocatore)

    # Lettura del file della squadra
    squadra_csv_path = os.path.join(base_path, n_sq ,'squadra.csv')
    squadra_df = pd.read_csv(squadra_csv_path)

    # Genera la pagina HTML per ogni squadra
    for _, row in squadra_df.iterrows():
        nome_squadra = row['squadra']
        nome_squadra_completo = row['nome_squadra']
        squadra_dir = get_squadra_dir(nome_squadra)

        # Percorso del file CSV dei giocatori
        giocatori_file = os.path.join(squadra_dir, 'giocatori.csv')
        giocatori_df = pd.read_csv(giocatori_file)

        # Creazione della pagina della squadra
        players_html = ""
        for _, giocatore_row in giocatori_df.iterrows():
            giocatore = giocatore_row['nome_giocatore']
            cognome = giocatore_row['cognome']
            numero = giocatore_row['numero']
            players_html += f'\n\t\t\t<a href="{giocatore}/{giocatore}.html" class="player-button">{cognome} {numero}</a>'

        output_squadra = template_squadra.render(
            nome_squadra_completo=nome_squadra_completo,
            nome_squadra=nome_squadra,
            players_html=players_html,
            static_path='/static'
        )
        squadra_html_file = os.path.join(squadra_dir, f'{nome_squadra}.html')
        with open(squadra_html_file, 'w', encoding='utf-8') as f:
            f.write(output_squadra)

        print(f"Pagina HTML generata per la squadra {nome_squadra_completo}: {squadra_html_file}")

        # Generazione pagine giocatori
        for _, giocatore_row in giocatori_df.iterrows():
            giocatore = giocatore_row['nome_giocatore']
            cognome = giocatore_row['cognome']
            numero = giocatore_row['numero']
            nome_completo = f"{giocatore_row['nome']} {cognome}"
            piede = giocatore_row['piede']
            giocatore_dir = get_giocatore_dir(nome_squadra, giocatore)
            os.makedirs(giocatore_dir, exist_ok=True)

            # Percorso file Excel
            excel_file = os.path.join(giocatore_dir, f'{giocatore}.xlsx')
            try:
                df = pd.read_excel(excel_file)
            except FileNotFoundError:
                print(f"File Excel per {giocatore} non trovato: {excel_file}")
                continue

            # Creazione elementi dinamici
            balls_data = df.to_dict(orient='records')
            balls_html = ""
            list_html = """
            <table class="penalty-table" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Partita</th>
                        <th>Minuto</th>
                        <th>Esito</th>
                        <th>Risultato</th>
                        <th>Video</th>
                    </tr>
                </thead>
                <tbody>
            """
            aprire, chiudere, aprire_gol, chiudere_gol = 0, 0, 0, 0
            for i, ball in enumerate(balls_data, start=1):
                esito_color = '#4CAF50' if ball['Esito'] == 1 else '#F44336'
                esito_text = 'Trasformato' if ball['Esito'] == 1 else 'Sbagliato'
                ball_img = "football.png" if ball['Esito'] == 1 else "missed.png"
                balls_html += f"""
                <a href="{ball['Link']}" target="_blank" class="ball-link-{i}">
                    <div class="ball" style="top: {ball['Top'] / 10 * 100}%; left: {ball['Left'] / 30 * 100}%;">
                        <img src="{url_for('static', filename=f'images/{ball_img}')}" alt="Football">
                        <span class="ball-number" style="color: black;">{i}</span>
                    </div>
                </a>
                """
                list_html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{ball['Partita']}</td>
                    <td>{ball['Minuto']}</td>
                    <td style="background-color: {esito_color}; color: #fff;">{esito_text}</td>
                    <td>{ball['Risultato']}</td>
                    <td><a href="{ball['Link']}" target="_blank">link</a></td>
                </tr>
                """
                if ball['Left'] <= 15:
                    chiudere += 1
                    chiudere_gol += ball['Esito']
                else:
                    aprire += 1
                    aprire_gol += ball['Esito']

            list_html += "</tbody></table>"

            # Grafici dinamici
            grafici_html = ""
            grafici_aprire_html = ""
            grafici_chiudere_html = ""
            if aprire != 0:
                grafici_aprire_html = f"""
    
                        var ctxAprire = document.getElementById('graficoAprire').getContext('2d');
                        var graficoAprire = new Chart(ctxAprire, {{
                            type: 'pie',
                            data: {{
                                labels: ['Gol', 'Sbagliati'],
                                datasets: [{{
                                    label: 'Rigori ad Aprire',
                                    data: [{aprire_gol}, {aprire - aprire_gol}],
                                    backgroundColor: ['#4CAF50', '#F44336'],
                                    hoverOffset: 4
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                plugins: {{
                                    legend: {{
                                        position: 'top',
                                    }},
                                    tooltip: {{
                                        enabled : false
                                    }},
                                    datalabels: {{
                                        color: '#fff',
                                        font: {{
                                            size: 18,  // Imposta la dimensione del font delle etichette
                                            weight: 'bold' // Puoi anche aggiungere altre proprietà come il peso del font
                                        }},
                                        formatter: function(value, context) {{
                                            var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            var percent = Math.round((value / total) * 100);
                                            return value + ' (' + percent + '%)';
                                        }}
                                    }}
                                }}
                            }},
                            plugins: [ChartDataLabels]
                        }});
                    """
            if chiudere != 0:
                grafici_chiudere_html = f"""
                    var ctxChiudere = document.getElementById('graficoChiudere').getContext('2d');
                    var graficoChiudere = new Chart(ctxChiudere, {{
                        type: 'pie',
                        data: {{
                            labels: ['Gol', 'Sbagliati'],
                            datasets: [{{
                                label: 'Rigori a Chiudere',
                                data: [{chiudere_gol}, {chiudere - chiudere_gol}],
                                backgroundColor: ['#4CAF50', '#F44336'],
                                hoverOffset: 4
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{
                                    position: 'top',
                                }},
                                tooltip: {{
                                    enabled : false
                                }},
                                datalabels: {{
                                    color: '#fff',
                                    font: {{
                                        size: 18,  // Imposta la dimensione del font delle etichette
                                        weight: 'bold' // Puoi anche aggiungere altre proprietà come il peso del font
                                    }},
                                    formatter: function(value, context) {{
                                        var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        var percent = Math.round((value / total) * 100);
                                        return value + ' (' + percent + '%)';
                                    }}
                                }}
                            }}
                        }},
                        plugins: [ChartDataLabels]
                    }});
                    """

            logica_html = ""
            if aprire != 0 and chiudere != 0:
                logica_html = f"""
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                        <h3> Rigori Calciati </h3>
                        <canvas id="graficoTotale"></canvas>
                        </div>
                    </div>
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                            <h3>Rigori ad Aprire</h3>
                            <canvas id="graficoAprire"></canvas>
                        </div>
                        <div>
                            <h3>Rigori a Chiudere</h3>
                            <canvas id="graficoChiudere"></canvas>
                        </div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
                    """
            elif aprire == 0 and chiudere != 0:
                logica_html = f"""
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                        <h3> Rigori Calciati </h3>
                        <canvas id="graficoTotale"></canvas>
                        </div>
                    </div>
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                            <h3>Rigori ad Aprire</h3>
                            <p style="margin-top:20px;">Non ci sono rigori ad Aprire</p>
                        </div>
                        <div>
                            <h3>Rigori a Chiudere</h3>
                            <canvas id="graficoChiudere"></canvas>
                        </div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
                    """
            elif chiudere == 0 and aprire != 0:
                logica_html = f"""
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                        <h3> Rigori Calciati </h3>
                        <canvas id="graficoTotale"></canvas>
                        </div>
                    </div>
                    <div class="grafici-container" style="display: flex; justify-content: space-around; margin-top: 50px; margin-bottom: 100px">
                        <div>
                            <h3>Rigori ad Aprire</h3>
                            <canvas id="graficoAprire"></canvas>
                        </div>
                        <div>
                            <h3>Rigori a Chiudere</h3>
                            <p style="margin-top:20px;">Non ci sono rigori a chiudere</p>
                        </div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
                    """

            grafici_html = logica_html + f"""
                    <script>
                        var ctxTotal = document.getElementById('graficoTotale').getContext('2d');
                        var graficoTotal = new Chart(ctxTotal, {{
                            type: 'pie',
                            data: {{
                                labels: ['Chiudere', 'Aprire'],
                                datasets: [{{
                                    label: 'Rigori Calciati',
                                    data: [{chiudere}, {aprire}],
                                    backgroundColor: ['#4CAF50', '#0000FF'],
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                plugins: {{
                                    legend: {{
                                        position: 'top',
                                    }},
                                    tooltip: {{
                                        enabled : false
                                    }},
                                    datalabels: {{
                                        color: '#fff',
                                        font: {{
                                            size: 18,  // Imposta la dimensione del font delle etichette
                                            weight: 'bold' // Puoi anche aggiungere altre proprietà come il peso del font
                                        }},
                                        formatter: function(value, context) {{
                                            var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            var percent = Math.round((value / total) * 100);
                                            return value + ' (' + percent + '%)';
                                        }}
                                    }}
                                }}
                            }},
                            plugins: [ChartDataLabels]
                        }});
                    """
            grafici_html += grafici_aprire_html + grafici_chiudere_html + "</script>"
            # Render giocatore
            output_giocatore = template.render(
                nome_giocatore=giocatore,
                nome_completo=nome_completo,
                nome_squadra=nome_squadra,
                piede_giocatore=piede,
                balls_html=balls_html,
                list_html=list_html,
                grafici_html=grafici_html,
                static_path = '/static'
            )

            giocatore_html_file = os.path.join(giocatore_dir, f'{giocatore}.html')
            with open(giocatore_html_file, 'w', encoding='utf-8') as f:
                f.write(output_giocatore)

            print(f"Pagina HTML generata per {giocatore}: {giocatore_html_file}")