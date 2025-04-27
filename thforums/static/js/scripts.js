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
    btn.addEventListener('mouseover', () => {
      sound.currentTime = 0;
      sound.play();
    });
  })

// commend (like) system for threads and replies
document.addEventListener('DOMContentLoaded', function() {
    // Thread commend
    document.querySelectorAll('.btn-commend-thread').forEach(btn => {
        btn.addEventListener('click', function() {
            const threadId = btn.getAttribute('data-thread-id');
            fetch(`/commend/thread/${threadId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                btn.classList.toggle('commended', data.commended);
                btn.querySelector('.commend-label').textContent = data.commended ? 'Commended' : 'Commend';
                btn.querySelector('.commend-count').textContent = data.count;
            });
        });
    });

    // reply commend
    document.querySelectorAll('.btn-commend-reply').forEach(btn => {
        btn.addEventListener('click', function() {
            const replyId = btn.getAttribute('data-reply-id');
            fetch(`/commend/reply/${replyId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                btn.classList.toggle('commended', data.commended);
                btn.querySelector('.commend-label').textContent = data.commended ? 'Commended' : 'Commend';
                btn.querySelector('.commend-count').textContent = data.count;
            });
        });
    });

    // user commend
    document.querySelectorAll('.btn-commend-user').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = btn.getAttribute('data-user-id');
            fetch(`/commend/user/${userId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                btn.classList.toggle('commended', data.commended);
                btn.querySelector('.commend-label').textContent = data.commended ? 'Commended' : 'Commend';
                // update commend count in profile header
                const countSpan = btn.parentElement.querySelector('b');
                if (countSpan) countSpan.textContent = data.count;
            });
        });
    });
});