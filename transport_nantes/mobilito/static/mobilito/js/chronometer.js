let seconds = 0;
let minutes = 0;
let hours = 0;

var chronometer = document.getElementById('chrono');
var progressBar = document.getElementById('bar');
var cheerTextElement = document.getElementById('cheer-text');

var completedBarTime = 0;

var FirstStage = {
    duration: 60*3,
    styles: () =>{return;},
    cheerText: "Go !"
}
var SecondStage = {
    duration: 60*2,
    styles: () =>{
        $(".progress")[0].classList.add("bg-success");
        progressBar.classList.remove("bg-success");
        progressBar.classList.add("bg-warning");
    },
    cheerText: "Super ! Continuez comme ça !"
}
var ThirdStage = {
    duration: 60*5,
    styles: () =>{
        $(".progress")[0].classList.remove("bg-success");
        $(".progress")[0].classList.add("bg-warning");
        progressBar.classList.remove("bg-warning");
        progressBar.classList.add("bg-danger");
    },
    cheerText: "Vous êtes au top !"
}

var stages = [FirstStage, SecondStage, ThirdStage];
function* stagesIterator(stages) {
    for (let i = 0; i < stages.length; i++) {
        yield stages[i];
    }
}

var stage = stagesIterator(stages);
var currentStage = stage.next().value;
var goal = currentStage.duration;
var applyStyles = () => {
    currentStage.styles();
}
cheerTextElement.textContent = currentStage.cheerText;

const updateTime = () => {
    seconds = parseInt(seconds);
    minutes = parseInt(minutes);
    hours = parseInt(hours);

    seconds++;
    var total_seconds = seconds + (minutes * 60) + (hours * 3600);

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
    updateProgressBar(total_seconds);
}

const updateProgressBar = (total_seconds) => {

    total_seconds -= completedBarTime;
    var progress = (total_seconds / goal) * 100;

    if (currentStage) {
        progressBar.style.width = `${progress}%`;
        applyStyles();
    }

    if (progress >= 100) {
        if (currentStage) {
            completedBarTime += currentStage.duration;
        }
        currentStage = stage.next().value;
        if (currentStage) {
            goal = currentStage.duration
            applyStyles = currentStage.styles;
            cheerTextElement.textContent = currentStage.cheerText;
        }
    }
}

setInterval(updateTime, 1000);
