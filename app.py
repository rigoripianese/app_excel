from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    # Mostra la pagina index.html
    return render_template('index.html')

@app.route('/genera-analisi', methods=['GET', 'POST'])
def genera_analisi():
    if request.method == 'POST':
        nome_squadra = request.form['nome_squadra']
        nome_squadra_completo = request.form['nome_squadra_completo']

        # Percorso della directory della squadra
        squadra_dir = os.path.join('static/campionato', 'squadre', nome_squadra)

        # Crea la directory della squadra se non esiste
        os.makedirs(squadra_dir, exist_ok=True)

        # Dati dei giocatori
        nomi_giocatori = request.form.getlist('nome_giocatore')
        cognomi = request.form.getlist('cognome')
        piedi = request.form.getlist('piede')
        numeri = request.form.getlist('numero')

        squadra_data = []

        for i, nome_giocatore in enumerate(nomi_giocatori):
            giocatore_id = i  # Usiamo l'indice come ID univoco

            # Percorso della directory del giocatore
            giocatore_dir = os.path.join(squadra_dir, nome_giocatore)

            # Crea la directory del giocatore se non esiste
            os.makedirs(giocatore_dir, exist_ok=True)

            # Raccogli dati dei tiri
            partite = request.form.getlist(f'partita-{giocatore_id}')
            minuti = request.form.getlist(f'minuto-{giocatore_id}')
            esiti = request.form.getlist(f'esito-{giocatore_id}')
            risultati = request.form.getlist(f'risultato-{giocatore_id}')
            link_video = request.form.getlist(f'link-{giocatore_id}')
            tops = request.form.getlist(f'top-{giocatore_id}')
            lefts = request.form.getlist(f'left-{giocatore_id}')

            # Se ci sono tiri registrati, crea un file Excel per il giocatore
            if partite and len(partite) > 0:
                giocatore_data = {
                    'Partita': partite,
                    'Minuto': minuti,
                    'Esito': [int(esito) for esito in esiti],
                    'Risultato': risultati,
                    'Link': link_video,
                    'Top': [float(top) for top in tops],
                    'Left': [float(left) for left in lefts],
                    'Piede': piedi[i],
                    'Squadra': nome_squadra
                }
                df_giocatore = pd.DataFrame(giocatore_data)

                # Salva il file Excel nella directory del giocatore
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

        # Salva il file CSV della squadra nella directory della squadra
        df_squadra = pd.DataFrame(squadra_data)
        df_squadra.to_csv(os.path.join(squadra_dir, 'giocatori.csv'), index=False)

        # Salva il file CSV con i dettagli della squadra
        pd.DataFrame([{'squadra': nome_squadra, 'nome_squadra': nome_squadra_completo}]).to_csv(
            os.path.join('static/campionato', 'squadre', f'{nome_squadra}', 'squadra.csv'), index=False
        )

        # Esecuzione di script.py
        try:
            result = subprocess.run(
                ['python', 'script.py', nome_squadra],  # Comando per eseguire script.py
                check=True,  # Genera un'eccezione se il comando fallisce
                text=True,  # Output del comando come stringa
                capture_output=True  # Cattura stdout e stderr
            )
            # Debug: mostra l'output di script.py
            print("Output script.py:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Errore durante l'esecuzione di script.py:", e.stderr)
            return f"Errore durante l'esecuzione dello script: {e.stderr}"

        return "File generati con successo!"
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
