const tg = window.Telegram.WebApp;
tg.expand();


const maleButton = document.getElementById("male");
const femaleButton = document.getElementById("female");

maleButton.addEventListener("click", function() {
    tg.sendData(JSON.stringify({gender: "male"}));
});
femaleButton.addEventListener("click", function() {
    tg.sendData(JSON.stringify({gender: "female"}));
});

const lookingForMaleButton = document.getElementById("looking_for_male");
const lookingForFemaleButton = document.getElementById("looking_for_female");
const lookingForBothButton = document.getElementById("looking_dont_care");

lookingForMaleButton.addEventListener("click", function() {
    tg.sendData(JSON.stringify({looking_for: "for_male"}));
});
lookingForFemaleButton.addEventListener("click", function() {
    tg.sendData(JSON.stringify({looking_for: "for_female"}));
});
lookingForBothButton.addEventListener("click", function() {
    tg.sendData(JSON.stringify({looking_for: "for_both"}));
});