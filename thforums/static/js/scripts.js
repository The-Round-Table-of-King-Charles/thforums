// auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);
    console.log('Tavernhold Forums scripts loaded');
});


//sound effects
const buttons = document.querySelectorAll(".soundBtn");
const sound = document.getElementById("btnSound");

buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      sound.currentTime = 0;
      sound.play();
    });
  })