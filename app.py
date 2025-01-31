from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup



app = Flask(__name__)

PASSWORD_CORRETTA = "tester"

# Configurazione dell'ambiente Jinja2
script_dir = os.getcwd()


def calculate_pressure_index(answers):
    """Calcola l'indice di pressione sulla base delle risposte al questionario."""
    weights = [1, 0.5, 0.8, 0.5, 1, 1, 0.7, 0.6, 0.6, 0.5, 0.4]
    return sum(weight for answer, weight in zip(answers, weights) if answer == 'yes')

def calculate_clutch(data):
    """Calcola il valore clutch di un giocatore."""
    total_pressure = sum(data['Indice di Pressione'])
    successful_pressure = sum(data[data['Esito'] == 1]['Indice di Pressione'])
    return (successful_pressure / total_pressure) * 100 if total_pressure > 0 else 0


def get_giocatore_dir(squadra, giocatore):
    """
    Generate the directory path for a specific player within a team's directory.

    This function constructs the filesystem path for a player within a specified team's
    directory. It appends the player's directory under the team's specific path within
    a predefined base directory structure.

    :param squadra: Name of the team for which the directory is being constructed.
    :type squadra: str
    :param giocatore: Name of the player whose directory is being referenced.
    :type giocatore: str
    :return: The constructed file path for the player's directory within the team's folder.
    :rtype: str
    """
    squadra_dir = os.path.join('static/campionato', 'squadre', squadra)
    return os.path.join(squadra_dir, giocatore)


def aggiorna_campionato_html(nome_squadra, nome_squadra_completo):
    """
    Updates the contents of the 'campionato.html' file by adding a new team if it
    does not already exist. The teams are sorted alphabetically and the file is
    rewritten with the updated structure. The function works specifically with
    HTML to parse, modify, and regenerate its structure based on the provided team
    information.

    :param nome_squadra: Short identifier for the new team being added.
    :type nome_squadra: str
    :param nome_squadra_completo: Full display name of the new team being added.
    :type nome_squadra_completo: str
    :return: None
    """
    campionato_file = os.path.join('static/campionato', 'campionato.html')

    # Verifica se il file esiste
    if not os.path.exists(campionato_file):
        print(f"File {campionato_file} non trovato.")
        return

    # Leggi il contenuto del file
    with open(campionato_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Trova il container dei team
    teams_container = soup.find('div', class_='teams-container')
    if not teams_container:
        print("Container dei team non trovato.")
        return

    # Estrarre i team esistenti
    team_buttons = teams_container.find_all('button', class_='team-button')
    teams = []

    for button in team_buttons:
        onclick = button.get('onclick', '')
        if "window.location.href='" in onclick:
            link = onclick.split("'")[1]
        else:
            continue
        img = button.find('img')
        span = button.find('span')

        if img and span:
            teams.append({
                'link': link,
                'img_src': img['src'],
                'img_alt': img['alt'],
                'name': span.text.strip()
            })

    # Aggiungi la nuova squadra se non esiste già
    new_team = {
        'link': f"squadre/{nome_squadra}/{nome_squadra}.html",
        'img_src': f"loghi/{nome_squadra}.png",
        'img_alt': nome_squadra_completo,
        'name': nome_squadra_completo.strip()
    }

    if not any(team['name'].lower() == new_team['name'].lower() for team in teams):
        teams.append(new_team)

    # Ordina i team in base al nome
    teams = sorted(teams, key=lambda t: t['name'].lower())

    # Pulisci il container e ricostruisci il contenuto
    teams_container.clear()
    for team in teams:
        team_button = soup.new_tag('button',
                                   **{'class': 'team-button', 'onclick': f"window.location.href='{team['link']}'"})
        img_tag = soup.new_tag('img', src=team['img_src'], alt=team['img_alt'])
        span_tag = soup.new_tag('span')
        span_tag.string = team['name']

        team_button.append(img_tag)
        team_button.append(span_tag)
        teams_container.append(team_button)

    # Scrivi il contenuto aggiornato nel file
    with open(campionato_file, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Aggiornato {campionato_file} con successo.")
@app.route('/')
def index():
    """
    Defines a route for the root URL endpoint and renders the index.html template.

    :return: Rendered HTML content of the index.html template.
    :rtype: str
    """
    return render_template('index.html')

@app.route('/genera-analisi', methods=['GET', 'POST'])
def genera_analisi():
    """
    Handles the generation of files and directories related to team's analysis and
    player data, using the POST request to receive and process form data and files. This
    function manages data organizing, video and image handling, and export to CSV or Excel.

    :param nome_squadra: Short name of the team.
    :type nome_squadra: str
    :param nome_squadra_completo: Full name of the team.
    :type nome_squadra_completo: str
    :param nome_giocatore: List of player names for the team.
    :type nome_giocatore: List[str]
    :param cognome: List of player surnames.
    :type cognome: List[str]
    :param piede: List indicating the preferred feet of each player.
    :type piede: List[str]
    :param numero: List of jersey numbers for the players.
    :type numero: List[str]
    :param immagine_giocatore: Uploaded image file of a player.
    :type immagine_giocatore: Werkzeug.datastructures.FileStorage
    :param partita: Matches played by a player.
    :type partita: List[str]
    :param minuto: Minutes corresponding to a specific match event for each player.
    :type minuto: List[str]
    :param esito: Outcomes of specific match events.
    :type esito: List[int]
    :param risultato: Scores corresponding to match events.
    :type risultato: List[str]
    :param link_video: Video analysis links for match events.
    :type link_video: List[str]
    :param top: Vertical position data for some match-related analysis.
    :type top: List[float]
    :param left: Horizontal position data for some match-related analysis.
    :type left: List[float]
    :param video: List of uploaded video files for matches.
    :type video: List[Werkzeug.datastructures.FileStorage]

    :raises KeyError: If a required key isn't found in the form or files request.

    :returns: Renders the form for GET requests or returns a success message
        upon completion of file generation for POST requests.
    :rtype: str
    """
    if request.method == 'POST':
        nome_squadra = request.form['nome_squadra']
        nome_squadra_completo = request.form['nome_squadra_completo']

        squadra_dir = os.path.join('static/campionato', 'squadre', nome_squadra)
        os.makedirs(squadra_dir, exist_ok=True)

        squadra_dir_videos = os.path.join('static/videos', nome_squadra)
        os.makedirs(squadra_dir_videos, exist_ok=True)

        nomi_giocatori = request.form.getlist('nome_giocatore')
        cognomi = request.form.getlist('cognome')
        piedi = request.form.getlist('piede')
        numeri = request.form.getlist('numero')

        squadra_data = []
        for i, nome_giocatore in enumerate(nomi_giocatori):
            giocatore_dir = os.path.join(squadra_dir, nome_giocatore)
            os.makedirs(giocatore_dir, exist_ok=True)

            # Salva l'immagine caricata
            immagine_giocatore = request.files.get(f'immagine_giocatore-{i}')
            if immagine_giocatore:
                immagine_path = os.path.join(giocatore_dir, f"{nome_giocatore}.webp")
                immagine_giocatore.save(immagine_path)


            partite = request.form.getlist(f'partita-{i}')
            minuti = request.form.getlist(f'minuto-{i}')
            esiti = request.form.getlist(f'esito-{i}')
            risultati = request.form.getlist(f'risultato-{i}')
            link_video = request.form.getlist(f'link-{i}')
            tops = request.form.getlist(f'top-{i}')
            lefts = request.form.getlist(f'left-{i}')
            pressure_indices = []
            for j in range(len(partite)):
                question_answers = [
                    request.form.get(f'questionario-{i}-{k}') for k in range(11)  # question number
                ]
                pressure_index = calculate_pressure_index(question_answers)
                pressure_indices.append(pressure_index)

            giocatore_dir_videos = os.path.join(squadra_dir_videos, nome_giocatore)
            os.makedirs(giocatore_dir_videos, exist_ok=True)

            video_files = request.files.getlist(f'video-{i}')
            video_paths = []
            for idx, video_file in enumerate(video_files):
                if video_file:
                    video_path = os.path.join(giocatore_dir, f"video_{idx + 1}.mp4")
                    video_paths.append(video_path)
                    video_file.save(video_path)
            pressure_indices = []
            for j in range(len(partite)):
                question_answers = [
                    request.form.get(f'questionario-{i}-{k}', 'no') for k in range(11)  # question number
                ]
                pressure_index = calculate_pressure_index(question_answers)
                pressure_indices.append(pressure_index)
            if partite:
                giocatore_data = {
                    'Partita': partite,
                    'Minuto': minuti,
                    'Esito': [int(esito) for esito in esiti],
                    'Risultato': risultati,
                    'Link': link_video,
                    'Top': [float(top) for top in tops],
                    'Left': [float(left) for left in lefts],
                    'Video': video_paths,
                    'Piede': piedi[i],
                    'Squadra': nome_squadra,
                    'Indice di Pressione' : pressure_indices
                }
                df_giocatore = pd.DataFrame(giocatore_data)
                giocatore_file = os.path.join(giocatore_dir, f'{nome_giocatore}.xlsx')
                df_giocatore.to_excel(giocatore_file, index=False)
            squadra_data.append({
                'nome_giocatore': nome_giocatore,
                'nome': nome_giocatore,
                'cognome': cognomi[i],
                'squadra': nome_squadra,
                'piede': piedi[i],
                'numero': numeri[i]
            })


        df_squadra = pd.DataFrame(squadra_data)
        df_squadra.to_csv(os.path.join(squadra_dir, 'giocatori.csv'), index=False)
        pd.DataFrame([{'squadra': nome_squadra, 'nome_squadra': nome_squadra_completo}]).to_csv(
            os.path.join('static/campionato', 'squadre', f'{nome_squadra}', 'squadra.csv'), index=False
        )

        genera_pagine_html(nome_squadra, nome_squadra_completo)
        return redirect(url_for('index'))
    return render_template('form.html')

def genera_pagine_html(nome_squadra, nome_squadra_completo):
    """
    Generates dynamic HTML pages for teams and players based on provided CSV and Excel data.
    This function primarily formats and writes team and player-specific pages using templates
    and data inputs, while also creating additional data visualizations and statistics.

    :param nome_squadra: Name of the team.
    :type nome_squadra: str
    :param nome_squadra_completo: Full name of the team.
    :type nome_squadra_completo: str
    :return: None.
    """
    squadra_dir = os.path.join('static/campionato', 'squadre', nome_squadra)
    squadra_csv_path = os.path.join(squadra_dir, 'squadra.csv')
    squadra_df = pd.read_csv(squadra_csv_path)



    #template_squadra = env.get_template('template_squadra.html')
    for _, row in squadra_df.iterrows():
        giocatori_file = os.path.join(squadra_dir, 'giocatori.csv')
        giocatori_df = pd.read_csv(giocatori_file)



        players_html = ""
        for _, giocatore_row in giocatori_df.iterrows():
            giocatore = giocatore_row['nome_giocatore']
            cognome = giocatore_row['cognome']
            numero = giocatore_row['numero']
            players_html += f'<a href="{giocatore}/{giocatore}.html" class="player-button">{cognome} {numero}</a>'

        output_squadra = render_template(
        'template_squadra.html',
        nome_squadra_completo=nome_squadra_completo,
        nome_squadra=nome_squadra,
        players=players_html,
        static_path='static'
    )
        squadra_html_file = os.path.join(squadra_dir, f'{nome_squadra}.html')
        with open(squadra_html_file, 'w', encoding='utf-8') as f:
            f.write(output_squadra)

        aggiorna_campionato_html(nome_squadra,nome_squadra_completo)

        # Genera pagine giocatori...
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
                        <th>Indice di Pressione</th>
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
                <a href="{ url_for('playlist',nome_squadra=nome_squadra, nome_giocatore=giocatore, video_name=ball['Video'][i]) }" target="_blank" class="ball-link-{i}">
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
                    <td>{ball['Indice di Pressione']}</td>
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
            clutch_value = calculate_clutch(df)
            # Render giocatore
            output_giocatore = render_template(
                'template.html',
                nome_giocatore=giocatore,
                nome_completo=nome_completo,
                nome_squadra=nome_squadra,
                piede_giocatore=piede,
                balls_html=balls_html,
                list_html=list_html,
                grafici_html=grafici_html,
                clutch_value=clutch_value,
                static_path = 'static'
            )

            giocatore_html_file = os.path.join(giocatore_dir, f'{giocatore}.html')
            with open(giocatore_html_file, 'w', encoding='utf-8') as f:
                f.write(output_giocatore)

@app.route('/playlist/<nome_squadra>/<nome_giocatore>/<video_name>', methods=['GET'])
def playlist(nome_squadra,nome_giocatore, video_name):
    """
    Generate a playlist page for a specified football player's videos. This function retrieves a
    specific team's player's directory, gathers all video files within the directory, and renders an
    HTML playlist page. The URL for the video is dynamically constructed using the specified
    parameters.

    :param nome_squadra: Football team's name.
    :type nome_squadra: str
    :param nome_giocatore: Football player's name.
    :type nome_giocatore: str
    :param video_name: Name of the currently selected video file.
    :type video_name: str
    :return: Rendered HTML page for the playlist, including the list of video files, and URL for
             the currently selected video.
    :rtype: str
    """
    giocatore_dir = get_giocatore_dir(nome_squadra, nome_giocatore)
    videos = [
        file for file in os.listdir(giocatore_dir)
        if file.endswith(".mp4")
    ]
    video_url = f"/static/campionato/squadre/{nome_squadra}/{nome_giocatore}/{video_name}"
    return render_template(
        'playlist.html',
        nome_completo=f"{nome_giocatore}",
        nome_giocatore=nome_giocatore,
        videos=videos,
        video_url=video_url,
        nome_squadra=f"{nome_squadra}"
    )
@app.route('/squadra/<nome_squadra>')
def pagina_squadra(nome_squadra):
    squadra_dir = os.path.join('static/campionato/squadre', nome_squadra)
    squadra_csv_path = os.path.join(squadra_dir, 'squadra.csv')

    if not os.path.exists(squadra_csv_path):
        return "Squadra non trovata", 404

    squadra_df = pd.read_csv(squadra_csv_path)
    giocatori_file = os.path.join(squadra_dir, 'giocatori.csv')
    giocatori_df = pd.read_csv(giocatori_file)

    players_html = "".join([
        f'<a href="{url_for("pagina_giocatore", nome_squadra=nome_squadra, nome_giocatore=row["nome_giocatore"])}" class="player-button">{row["cognome"]} {row["numero"]}</a>'
        for _, row in giocatori_df.iterrows()
    ])

    return render_template("template_squadra.html", nome_squadra=nome_squadra, players=players_html)


@app.route('/giocatore/<nome_squadra>/<nome_giocatore>')
def pagina_giocatore(nome_squadra, nome_giocatore):
    giocatore_dir = os.path.join('static/campionato/squadre', nome_squadra, nome_giocatore)
    excel_file = os.path.join(giocatore_dir, f'{nome_giocatore}.xlsx')

    if not os.path.exists(excel_file):
        return "Giocatore non trovato", 404

    df = pd.read_excel(excel_file)

    # Recupera nome completo e piede
    giocatori_file = os.path.join(f'static/campionato/squadre/{nome_squadra}/giocatori.csv')
    df_giocatori = pd.read_csv(giocatori_file)

    giocatore_info = df_giocatori[df_giocatori['nome_giocatore'] == nome_giocatore].iloc[0]
    nome_completo = f"{giocatore_info['nome']} {giocatore_info['cognome']}"
    piede = giocatore_info['piede']

    # Recupera immagine del giocatore
    immagine_giocatore = f"{nome_giocatore}.webp"

    # Genera la lista dei palloni con link ai video o ai link esterni
    balls_html = ""
    table_html = """
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

    for i, row in df.iterrows():
        esito_color = '#4CAF50' if row['Esito'] == 1 else '#F44336'
        esito_text = 'Trasformato' if row['Esito'] == 1 else 'Sbagliato'
        ball_img = "football.png" if row['Esito'] == 1 else "missed.png"

        link = row['Link'] if pd.notna(row['Link']) else url_for('playlist', nome_squadra=nome_squadra, nome_giocatore=nome_giocatore, video_name=row['Video'])

        balls_html += f"""
        <a href="{link}" target="_blank">
            <div class="ball" style="top: {row['Top'] / 10 * 100}%; left: {row['Left'] / 30 * 100}%;">
                <img src="{url_for('static', filename='images/' + ball_img)}" alt="Football">
                <span class="ball-number" style="color: black;">{i + 1}</span>
            </div>
        </a>
        """

        table_html += f"""
        <tr>
            <td>{i + 1}</td>
            <td>{row['Partita']}</td>
            <td>{row['Minuto']}</td>
            <td style="background-color: {esito_color}; color: white;">{esito_text}</td>
            <td>{row['Risultato']}</td>
            <td><a href="{link}" target="_blank">link</a></td>
        </tr>
        """

        # Conta rigori a "chiudere" e "aprire"
        if row['Left'] <= 15:
            chiudere += 1
            chiudere_gol += row['Esito']
        else:
            aprire += 1
            aprire_gol += row['Esito']

    table_html += "</tbody></table>"

    # Generazione dati per i grafici
    grafici_html = f"""
    <script>
        var ctxTotal = document.getElementById('graficoTotale').getContext('2d');
        new Chart(ctxTotal, {{
            type: 'pie',
            data: {{
                labels: ['Chiudere', 'Aprire'],
                datasets: [{{
                    data: [{chiudere}, {aprire}],
                    backgroundColor: ['#4CAF50', '#0000FF'],
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'top' }},
                    tooltip: {{ enabled: false }},
                    datalabels: {{
                        color: '#fff',
                        font: {{ size: 18, weight: 'bold' }},
                        formatter: (value, context) => {{
                            var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            return value + ' (' + Math.round((value / total) * 100) + '%)';
                        }}
                    }}
                }}
            }},
            plugins: [ChartDataLabels]
        }});

        var ctxAprire = document.getElementById('graficoAprire').getContext('2d');
        new Chart(ctxAprire, {{
            type: 'pie',
            data: {{
                labels: ['Gol', 'Sbagliati'],
                datasets: [{{
                    data: [{aprire_gol}, {aprire - aprire_gol}],
                    backgroundColor: ['#4CAF50', '#F44336'],
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'top' }},
                    tooltip: {{ enabled: false }},
                    datalabels: {{
                        color: '#fff',
                        font: {{ size: 18, weight: 'bold' }},
                        formatter: (value, context) => {{
                            var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            return value + ' (' + Math.round((value / total) * 100) + '%)';
                        }}
                    }}
                }}
            }},
            plugins: [ChartDataLabels]
        }});

        var ctxChiudere = document.getElementById('graficoChiudere').getContext('2d');
        new Chart(ctxChiudere, {{
            type: 'pie',
            data: {{
                labels: ['Gol', 'Sbagliati'],
                datasets: [{{
                    data: [{chiudere_gol}, {chiudere - chiudere_gol}],
                    backgroundColor: ['#4CAF50', '#F44336'],
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'top' }},
                    tooltip: {{ enabled: false }},
                    datalabels: {{
                        color: '#fff',
                        font: {{ size: 18, weight: 'bold' }},
                        formatter: (value, context) => {{
                            var total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            return value + ' (' + Math.round((value / total) * 100) + '%)';
                        }}
                    }}
                }}
            }},
            plugins: [ChartDataLabels]
        }});
    </script>
    """

    return render_template(
        "template.html",
        nome_completo=nome_completo,
        nome_squadra=nome_squadra,
        nome_giocatore=nome_giocatore,
        piede_giocatore=piede,
        immagine_giocatore=immagine_giocatore,
        balls_html=balls_html,
        list_html=table_html,
        grafici_html=grafici_html
    )


@app.route('/aggiungi_giocatore/<nome_squadra>', methods=['POST'])
def aggiungi_giocatore(nome_squadra):
    # Controlla la password
    password = request.form.get("password")
    if password != PASSWORD_CORRETTA:
        return "Errore: Password errata", 403

    squadra_dir = os.path.join('static/campionato/squadre', nome_squadra)
    giocatori_file = os.path.join(squadra_dir, 'giocatori.csv')

    if os.path.exists(giocatori_file):
        df_giocatori = pd.read_csv(giocatori_file)
    else:
        df_giocatori = pd.DataFrame(columns=['nome_giocatore', 'nome', 'cognome', 'numero', 'piede'])

    nome_giocatore = request.form['nome_giocatore']
    nome = request.form['nome']
    numero = request.form['numero']
    piede = request.form['piede']

    nuovo_giocatore = pd.DataFrame([{
        'nome_giocatore': nome_giocatore,
        'cognome': nome_giocatore.split()[0] if ' ' in nome_giocatore else nome_giocatore,
        'nome': nome,
        'numero': numero,
        'piede': piede
    }])

    df_giocatori = pd.concat([df_giocatori, nuovo_giocatore], ignore_index=True)
    df_giocatori.to_csv(giocatori_file, index=False)

    # Creazione della cartella per il giocatore
    giocatore_dir = os.path.join(squadra_dir, nome_giocatore)
    os.makedirs(giocatore_dir, exist_ok=True)

    # Salva la foto del giocatore
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto.filename:
            foto_path = os.path.join(giocatore_dir, f'{nome_giocatore}.webp')  # Salva come PNG
            foto.save(foto_path)

    # Creazione del file Excel vuoto per i rigori del giocatore
    excel_file = os.path.join(giocatore_dir, f'{nome_giocatore}.xlsx')
    if not os.path.exists(excel_file):
        df_vuoto = pd.DataFrame(columns=['Partita', 'Minuto', 'Esito', 'Risultato', 'Link', 'Top', 'Left', 'Video'])
        df_vuoto.to_excel(excel_file, index=False)

    return redirect(url_for('pagina_squadra', nome_squadra=nome_squadra))


@app.route('/aggiungi_rigore/<nome_squadra>/<nome_giocatore>', methods=['POST'])
def aggiungi_rigore(nome_squadra, nome_giocatore):
    # Controlla la password
    password = request.form.get("password")
    if password != PASSWORD_CORRETTA:
        return "Errore: Password errata", 403

    giocatore_dir = os.path.join('static/campionato/squadre', nome_squadra, nome_giocatore)
    excel_file = os.path.join(giocatore_dir, f'{nome_giocatore}.xlsx')

    if not os.path.exists(excel_file):
        return "Errore: File Excel del giocatore non trovato", 404

    df = pd.read_excel(excel_file)

    partite = request.form.getlist('partita')
    minuti = request.form.getlist('minuto')
    esiti = request.form.getlist('esito')
    risultati = request.form.getlist('risultato')
    links = request.form.getlist('link')
    tops = request.form.getlist('top')
    lefts = request.form.getlist('left')

    nuovi_rigori = []

    for i in range(len(partite)):
        # Domande del questionario (11 in totale)
        question_keys = [
            "Il risultato è in bilico?",
            "Il rigore è stato calciato negli ultimi 15 minuti?",
            "Il rigore è stato calciato negli ultimi 5 minuti?",
            "Il portiere si muove prima della battuta?",
            "Il rigore è durante i calci di rigore?",
            "Il rigore è stato controllato al VAR?",
            "La partita si gioca in trasferta?",
            "Il pubblico avversario disturba il tiratore?",
            "Le condizioni meteo sono avverse?",
            "Il campo è in cattive condizioni nella zona del dischetto del rigore?",
            "Il rigorista è appena entrato in campo?"
        ]

        # Raccogli le risposte alle domande
        question_answers = [
            request.form.get(f'questionario-{i}-{k}', 'no') for k in range(len(question_keys))
        ]

        # Calcola l'Indice di Pressione per questo rigore
        pressure_index = calculate_pressure_index(question_answers)

        nuovo_rigore = {
            'Partita': partite[i],
            'Minuto': int(minuti[i]),
            'Esito': int(esiti[i]),
            'Risultato': risultati[i],
            'Link': links[i] if links[i] else None,
            'Top': float(tops[i]),
            'Left': float(lefts[i]),
            'Indice di Pressione': pressure_index
        }

        # Salvataggio video, se presente
        video_key = f'video-{i}'
        if video_key in request.files:
            video_file = request.files[video_key]
            if video_file.filename:
                video_path = os.path.join(giocatore_dir, f"video_{i + 1}.mp4")
                nuovo_rigore['Video'] = video_path
                video_file.save(video_path)
            else:
                nuovo_rigore['Video'] = None

        nuovi_rigori.append(nuovo_rigore)

    df_nuovi_rigori = pd.DataFrame(nuovi_rigori)

    df = pd.concat([df_nuovi_rigori, df], ignore_index=True)
    df.to_excel(excel_file, index=False)

    return redirect(url_for('pagina_giocatore', nome_squadra=nome_squadra, nome_giocatore=nome_giocatore))
if __name__ == '__main__':
    app.run(debug=True,port=8080)


