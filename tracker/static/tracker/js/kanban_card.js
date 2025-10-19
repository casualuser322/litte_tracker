function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('kanban-board');
    if (!board) return;
    
    const updateUrl = board.dataset.updateUrl;
    const columns = board.querySelectorAll('.kanban-column');
    
    let draggedCard = null;
    let oldColumn = null;

    const csrftoken = getCookie('csrftoken');
    console.log('CSRF Token loaded:', csrftoken ? `Length: ${csrftoken.length}` : 'NOT FOUND');

    board.addEventListener('dragstart', e => {
        if (e.target.classList.contains('kanban-card')) {
            draggedCard = e.target;
            oldColumn = draggedCard.parentElement;
            setTimeout(() => draggedCard.style.opacity = '0.5', 0);
        }
    });

    board.addEventListener('dragend', e => {
        if (draggedCard) {
            draggedCard.style.opacity = '1';
            draggedCard = null;
            oldColumn = null;
        }
    });

    columns.forEach(column => {
        column.addEventListener('dragover', e => e.preventDefault());
        column.addEventListener('dragenter', e => {
            e.preventDefault();
            column.classList.add('drag-over');
        });
        column.addEventListener('dragleave', () => column.classList.remove('drag-over'));

        column.addEventListener('drop', (e) => {
            e.preventDefault();
            column.classList.remove('drag-over');
            if (!draggedCard) return;

            const taskId = draggedCard.dataset.taskId;
            const newStatus = column.dataset.status;

            column.appendChild(draggedCard);

            if (!csrftoken) {
                console.error('CSRF token not available');
                revertCardMove();
                return;
            }

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ task_id: taskId, status: newStatus })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Task status updated successfully');
                    const badge = draggedCard.querySelector('.badge');
                    if (badge && data.status_display) {
                        badge.textContent = data.status_display;
                    }
                } else {
                    throw new Error(data.error || 'Update failed');
                }
            })
            .catch(err => {
                console.error('Error updating task status:', err);
                revertCardMove();
            });

            function revertCardMove() {
                if (draggedCard && oldColumn) {
                    oldColumn.appendChild(draggedCard);
                }
            }
        });
    });
});