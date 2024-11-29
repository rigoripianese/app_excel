document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendar');
    const prevMonthButton = document.getElementById('prevMonth');
    const nextMonthButton = document.getElementById('nextMonth');

    const months = [
        { name: 'Agosto', days: 31, matches: [
            { date: 10, team: 'Pontedera - Primo turno Coppa', logo: '../campionato/loghi/pontedera.png' },
            { date: 24, team: 'Perugia', logo: '../campionato/loghi/perugia.png' }
        ] },
        { name: 'Settembre', days: 30, matches: [
            { date: 2, team: 'Ascoli', logo: '../campionato/loghi/ascoli.png' },
            { date: 8, team: 'Campobasso', logo: '../campionato/loghi/campobasso.png' },
            { date: 16, team: 'Pescara', logo: '../campionato/loghi/pescara.png' },
            { date: 22, team: 'Virtus Entella', logo: '../campionato/loghi/entella.png' },
            { date: 25, team: 'Lucchese', logo: '../campionato/loghi/lucchese.png' },
            { date: 29, team: 'Sestri Levante', logo: '../campionato/loghi/sestrilevante.png' }
        ] },
        { name: 'Ottobre', days: 31, matches: [
            { date: 6, team: 'Milan Futuro', logo: '../campionato/loghi/milan.png' },
            { date: 13, team: 'Carpi', logo: '../campionato/loghi/carpi.png' },
            { date: 20, team: 'Rimini', logo: '../campionato/loghi/rimini.png' },
            { date: 27, team: 'Gubbio', logo: '../campionato/loghi/gubbio.png' },
            { date: 30, team: 'SPAL', logo: '../campionato/loghi/spal.png' }
        ] },
        { name: 'Novembre', days: 30, matches: [
            { date: 3, team: 'Torres', logo: '../campionato/loghi/torres.png' },
            { date: 10, team: 'Vis Pesaro', logo: '../campionato/loghi/vispesaro.png' },
            { date: 17, team: 'Pontedera', logo: '../campionato/loghi/pontedera.png' },
            { date: 24, team: 'Legnago Salus', logo: '../campionato/loghi/legnago.png' }
        ] },
        { name: 'Dicembre', days: 31, matches: [
            { date: 1, team: 'Pineto', logo: '../campionato/loghi/pineto.png' },
            { date: 8, team: 'Ternana', logo: '../campionato/loghi/ternana.png' },
            { date: 15, team: 'Arezzo', logo: '../campionato/loghi/arezzo.png' },
            { date: 22, team: 'Perugia', logo: '../campionato/loghi/perugia.png' }
        ] },
        { name: 'Gennaio', days: 31, matches: [
            { date: 5, team: 'Ascoli', logo: '../campionato/loghi/ascoli.png' },
            { date: 12, team: 'Campobasso', logo: '../campionato/loghi/campobasso.png' },
            { date: 19, team: 'Pescara', logo: '../campionato/loghi/pescara.png' },
            { date: 26, team: 'Virtus Entella', logo: '../campionato/loghi/entella.png' }
        ] },
        { name: 'Febbraio', days: 29, matches: [
            { date: 2, team: 'Lucchese', logo: '../campionato/loghi/lucchese.png' },
            { date: 9, team: 'Sestri Levante', logo: '../campionato/loghi/sestrilevante.png' },
            { date: 16, team: 'Milan Futuro', logo: '../campionato/loghi/milan.png' },
            { date: 23, team: 'Carpi', logo: '../campionato/loghi/carpi.png' }
        ] },
        { name: 'Marzo', days: 31, matches: [
            { date: 2, team: 'Rimini', logo: '../campionato/loghi/rimini.png' },
            { date: 9, team: 'Gubbio', logo: '../campionato/loghi/gubbio.png' },
            { date: 12, team: 'SPAL', logo: '../campionato/loghi/spal.png' },
            { date: 16, team: 'Torres', logo: '../campionato/loghi/torres.png' },
            { date: 23, team: 'Vis Pesaro', logo: '../campionato/loghi/vispesaro.png' },
            { date: 30, team: 'Pontedera', logo: '../campionato/loghi/pontedera.png' }
        ] },
        { name: 'Aprile', days: 30, matches: [
            { date: 6, team: 'Legnago Salus', logo: '../campionato/loghi/legnago.png' },
            { date: 13, team: 'Pineto', logo: '../campionato/loghi/pineto.png' },
            { date: 19, team: 'Ternana', logo: '../campionato/loghi/ternana.png' },
            { date: 27, team: 'Arezzo', logo: '../campionato/loghi/arezzo.png' }
        ] }
    ];

    let currentMonthIndex = 0;

    function renderCalendar(monthIndex) {
        const month = months[monthIndex];
        const weeks = [];
        
        for (let i = 0; i < month.days; i++) {
            const weekIndex = Math.floor(i / 6);
            if (!weeks[weekIndex]) {
                weeks[weekIndex] = [];
            }
            weeks[weekIndex].push(i + 1);
        }

        calendarContainer.innerHTML = `
            <div class="month">
                <h2>${month.name}</h2>
                ${weeks.map(week => `
                    <div class="week">
                        ${week.map(day => {
                            const match = month.matches.find(match => match.date === day);
                            return `
                                <div class="day${match ? ' match' : ''}">
                                    <span class="date">${day} ${month.name.substring(0, 3)}</span>
                                    ${match ? `<img src="${match.logo}" alt="${match.team}">
                                    <span class="team">${match.team}</span>` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                `).join('')}
            </div>
        `;
    }

    prevMonthButton.addEventListener('click', () => {
        if (currentMonthIndex > 0) {
            currentMonthIndex--;
            renderCalendar(currentMonthIndex);
        }
    });

    nextMonthButton.addEventListener('click', () => {
        if (currentMonthIndex < months.length - 1) {
            currentMonthIndex++;
            renderCalendar(currentMonthIndex);
        }
    });

    renderCalendar(currentMonthIndex); // Renderizza il mese iniziale
});
