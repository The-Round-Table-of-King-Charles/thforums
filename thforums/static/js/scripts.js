// auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);
    console.log('Tavernhold Forums scripts loaded');

    // Offcanvas sidebar open on hover
    const offcanvasToggle = document.getElementById('offcanvasToggle');
    const offcanvasElem = document.getElementById('offcanvas');
    if (offcanvasToggle && offcanvasElem) {
        let offcanvasInstance = bootstrap.Offcanvas.getOrCreateInstance(offcanvasElem);

        offcanvasToggle.addEventListener('mouseenter', function() {
            if (!offcanvasElem.classList.contains('show')) {
                offcanvasInstance.show();
            }
        });

        // Optional: close when mouse leaves the sidebar area
        offcanvasElem.addEventListener('mouseleave', function(e) {
            // Only close if mouse leaves to outside the sidebar
            if (!offcanvasElem.contains(e.relatedTarget)) {
                offcanvasInstance.hide();
            }
        });
    }

    // Mark notifications as read when notification offcanvas is opened
    const notifOffcanvasElem = document.getElementById('notificationOffcanvas');
    if (notifOffcanvasElem) {
        notifOffcanvasElem.addEventListener('show.bs.offcanvas', function() {
            // Send AJAX request to mark notifications as read
            fetch('/notifications/mark_read', {method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'}})
                .then(() => {
                    // Optionally update badge or UI
                    const badge = document.querySelector('#notificationBell .badge');
                    if (badge) badge.style.display = 'none';
                    // Remove bold, add greyed-out style
                    document.querySelectorAll('#notificationOffcanvas .list-group-item.fw-bold').forEach(el => {
                        el.classList.remove('fw-bold');
                        el.classList.add('notification-read');
                    });
                });
        });

        // Mark all as read button
        const markAllReadBtn = document.getElementById('markAllReadBtn');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', function() {
                fetch('/notifications/mark_read', {method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(() => {
                        // Remove bold from notifications
                        document.querySelectorAll('#notificationOffcanvas .list-group-item.fw-bold').forEach(el => {
                            el.classList.remove('fw-bold');
                            el.classList.add('notification-read');
                        });
                        // Hide badge
                        const badge = document.querySelector('#notificationBell .badge');
                        if (badge) badge.style.display = 'none';
                    });
            });
        }

        // Delete all notifications button
        const deleteAllNotifBtn = document.getElementById('deleteAllNotifBtn');
        if (deleteAllNotifBtn) {
            deleteAllNotifBtn.addEventListener('click', function() {
                if (!confirm('Are you sure you want to delete all notifications?')) return;
                fetch('/notifications/delete_all', {method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'}})
                    .then(() => {
                        // Remove all notifications from the list
                        const notifList = document.querySelector('#notificationOffcanvas .list-group');
                        if (notifList) notifList.innerHTML = '';
                        // Show "No notifications yet."
                        const aside = document.querySelector('#notificationOffcanvas aside');
                        if (aside) {
                            let emptyMsg = aside.querySelector('.text-center.text-white');
                            if (!emptyMsg) {
                                emptyMsg = document.createElement('div');
                                emptyMsg.className = 'text-center text-white';
                                emptyMsg.textContent = 'No notifications yet.';
                                aside.appendChild(emptyMsg);
                            }
                        }
                        // Hide badge
                        const badge = document.querySelector('#notificationBell .badge');
                        if (badge) badge.style.display = 'none';
                    });
            });
        }
    }
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