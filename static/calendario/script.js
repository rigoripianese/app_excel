document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendar');
    const prevMonthButton = document.getElementById('prevMonth');
    const nextMonthButton = document.getElementById('nextMonth');

    const months = [
        { name: 'Agosto', days: 31, matches: [
            { date: 25, team: 'SS Arezzo', logo: '../campionato/loghi/arezzo.png' },
            { date: 31, team: 'FC Legnago Salus', logo: '../campionato/loghi/legnago.png' }
        ] },
        { name: 'Settembre', days: 30, matches: [
            { date: 8, team: 'US Pianese', logo: '../campionato/loghi/logo.png' },
            { date: 14, team: 'Torres', logo: '../campionato/loghi/torres.png' },
            { date: 20, team: 'AS Gubbio 1910', logo: '../campionato/loghi/gubbio.png' },
            { date: 26, team: 'Vis Pesaro 1898', logo: '../campionato/loghi/vispesaro.png' },
            { date: 29, team: 'US Città di Pontedera', logo: '../campionato/loghi/pontedera.png' }
        ] },
        { name: 'Ottobre', days: 31, matches: [
            { date: 7, team: 'Ternana Calcio', logo: '../campionato/loghi/ternana.png' },
            { date: 13, team: 'SPAL', logo: '../campionato/loghi/spal.png' },
            { date: 21, team: 'Pineto Calcio', logo: '../campionato/loghi/pineto.png' },
            { date: 26, team: 'US Sestri Levante', logo: '../campionato/loghi/levante.png' },
            { date: 30, team: 'Ascoli Calcio', logo: '../campionato/loghi/ascoli.png' }
        ] },
        { name: 'Novembre', days: 30, matches: [
            { date: 3, team: 'Lucchese 1905', logo: '../campionato/loghi/lucchese.png' },
            { date: 10, team: 'AC Carpi', logo: '../campionato/loghi/carpi.png' },
            { date: 24, team: 'Virtus Entella', logo: '../campionato/loghi/entella.png' }
        ] },
        { name: 'Dicembre', days: 31, matches: [
            { date: 1, team: 'Rimini FC', logo: '../campionato/loghi/rimini.png' },
            { date: 9, team: 'AC Perugia Calcio', logo: '../campionato/loghi/perugia.png' },
            { date: 14, team: 'Delfino Pescara 1936', logo: '../campionato/loghi/pescara.png' },
            { date: 22, team: 'SS Arezzo', logo: '../campionato/loghi/arezzo.png' }
        ] },
        { name: 'Gennaio', days: 31, matches: [
            { date: 5, team: 'FC Legnago Salus', logo: '../campionato/loghi/legnago.png' },
            { date: 12, team: 'US Pianese', logo: '../campionato/loghi/logo.png' },
            { date: 19, team: 'Torres', logo: '../campionato/loghi/torres.png' },
            { date: 25, team: 'AS Gubbio 1910', logo: '../campionato/loghi/gubbio.png' }
        ] },
        { name: 'Febbraio', days: 29, matches: [
            { date: 2, team: 'Vis Pesaro 1898', logo: '../campionato/loghi/vispesaro.png' },
            { date: 9, team: 'US Città di Pontedera', logo: '../campionato/loghi/pontedera.png' },
            { date: 16, team: 'Ternana Calcio', logo: '../campionato/loghi/ternana.png' },
            { date: 22, team: 'SPAL', logo: '../campionato/loghi/spal.png' }
        ] },
        { name: 'Marzo', days: 31, matches: [
            { date: 2, team: 'Pineto Calcio', logo: '../campionato/loghi/pineto.png' },
            { date: 8, team: 'US Sestri Levante', logo: '../campionato/loghi/levante.png' },
            { date: 11, team: 'Ascoli Calcio', logo: '../campionato/loghi/ascoli.png' },
            { date: 15, team: 'Lucchese 1905', logo: '../campionato/loghi/lucchese.png' },
            { date: 23, team: 'AC Carpi', logo: '../campionato/loghi/carpi.png' },
            { date: 30, team: 'Milan Futuro', logo: '../campionato/loghi/milan.png' }
        ] },
        { name: 'Aprile', days: 30, matches: [
            { date: 6, team: 'Virtus Entella', logo: '../campionato/loghi/entella.png' },
            { date: 13, team: 'Rimini FC', logo: '../campionato/loghi/rimini.png' },
            { date: 20, team: 'AC Perugia Calcio', logo: '../campionato/loghi/perugia.png' },
            { date: 27, team: 'Delfino Pescara 1936', logo: '../campionato/loghi/pescara.png' }
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
