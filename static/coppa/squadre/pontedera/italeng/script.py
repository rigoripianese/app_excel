#In questo script genero il documento interattivo, devo recuperare dal file excel il link
#al video e la posizione in cui inserire il pallone con il numero e cliccabile col link
#allegato
from typing import TypedDict, List
import pandas as pd
class Ball(TypedDict):
    Link: str
    Top: int
    Left: int
i = 0

df = pd.read_excel('/Users/reus3111/Clip_Pianese/sito_web/coppa/squadre/pontedera/italeng/rigori_italeng.xlsx')
balls_data = df.to_dict(orient='records')



balls_html = ""
list_html = ""
for ball in balls_data:
    i+=1
    if ball['Esito']==1:
        balls_html += f"""
        <a href="{ball['Link']}" target="_blank" class="ball-link{i}">
            <div class="ball" style="position: absolute; top: {ball['Top']/10*100}%; left: {ball['Left']/30*100}%;">
                <img src="../../../../images/football.png" alt="Football">
                <span class="ball-number" style="color: black;">{i}</span>
            </div>
        </a>
        """
        list_html+=f"""
        <div class="relazione" style="flex-wrap: wrap;">
            {i}) Partita: {ball['Partita']}, rigore calciato al minuto: {ball['Minuto']} e trasformato, il risultato della partita al momento del tiro era: {ball['Risultato']}. <a href="{ball['Link']}" target="_blank" class="ball-link{i}" style="text-decoration: none;">Video</a>
        </div>
        """
    else:
        balls_html += f"""
        <a href="{ball['Link']}" target="_blank" class="ball-link{i}">
            <div class="ball" style="position: absolute; top: {ball['Top']/10*100}%; left: {ball['Left']/30*100}%;">
                <img src="../../../../images/missed.png" alt="Football">
                <span class="ball-number" style="color: black;">{i}</span>
            </div>
        </a>
        """
        list_html+=f"""
        <div class="relazione" style="flex-wrap: wrap;">
            {i}) Partita: {ball['Partita']}, rigore calciato al minuto: {ball['Minuto']} e sbagliato, il risultato della partita al momento del tiro era: {ball['Risultato']}. <a href="{ball['Link']}" target="_blank" class="ball-link{i}" style="text-decoration: none;">Video</a>
        </div>
        """
    

with open("coppa/squadre/pontedera/italeng/italeng.html", "r") as file:
    html_content = file.read()

# Trova il punto di inserimento
insert_point = html_content.find('<div id="balls-container" class="balls-container">') + len('<div id="balls-container" class="balls-container">')

# Inserisci il codice HTML generato
new_html_content = html_content[:insert_point] + balls_html + html_content[insert_point:]

# Trova il punto di inserimento per il testo
insert_point_text = new_html_content.find('<div class="list_of_penalties">') + len('<div class="list_of_penalties">')

# Inserisci il contenuto del file di testo
new_html_content = new_html_content[:insert_point_text] + list_html + new_html_content[insert_point_text:]

# Scrivi il nuovo contenuto HTML in un file
with open("coppa/squadre/pontedera/italeng/italeng.html", "w") as file:
    file.write(new_html_content)