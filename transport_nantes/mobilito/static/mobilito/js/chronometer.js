let seconds = 0;
let minutes = 0;
let hours = 0;

var chronometer = document.getElementById('chrono');

const updateTime = () => {
    seconds = parseInt(seconds);
    minutes = parseInt(minutes);
    hours = parseInt(hours);

    seconds++;
    
    if (seconds == 60) {
        minutes++;
        seconds = 0;
    }

    if (minutes == 60) {
        hours++;
        minutes = 0;
    }

    if (seconds < 10) {
        seconds = "0" + seconds;
    }

    if (minutes < 10) {
        minutes = "0" + minutes;
    }

    if (hours < 10) {
        hours = "0" + hours;
    }
    chronometer.innerHTML = `${hours}:${minutes}:${seconds}`;
}

setInterval(updateTime, 1000);