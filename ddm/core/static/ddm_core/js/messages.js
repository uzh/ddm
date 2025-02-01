document.addEventListener('DOMContentLoaded', function () {
    // Handle manual closing of message pop-ups.
    const closeButtons = document.querySelectorAll('.ddm-message-close');
    closeButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const messageElement = event.target.closest('.ddm-message');
            if (messageElement) {
                messageElement.remove();
            }
        });
    });

    // Automatically close message pop-ups after some time
    var messages = document.querySelectorAll('.ddm-message');
    messages.forEach(function (message) {
        message.style.transition = 'opacity 300ms, top 300ms';
        requestAnimationFrame(function () {
            message.style.opacity = '1';
            message.style.top = '0px';
        });
        setTimeout(function () {
            message.style.opacity = '0';
            message.style.top = '-50px';
        }, 7000);
    });
});
