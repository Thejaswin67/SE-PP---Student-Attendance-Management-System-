document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll(".message");
    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = "0";
            message.style.transition = "opacity 0.4s";
        }, 4000);
    });
});
