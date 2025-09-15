document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('kanban-board');
    const updateUrl = board.dataset.updateUrl;

    const columns = board.querySelectorAll('.kanban-column');

    let draggedCard = null;

    board.addEventListener('dragstart', e => {
        if (e.target.classList.contains('kanban-card')) {
            draggedCard = e.target;
            setTimeout(() => draggedCard.style.opacity = '0.5', 0);
        }
    });

    board.addEventListener('dragend', e => {
        if (draggedCard) {
            draggedCard.style.opacity = '1';
            draggedCard = null;
        }
    });

    columns.forEach(column => {
        column.addEventListener('dragover', e => e.preventDefault());
        column.addEventListener('dragenter', e => {
            e.preventDefault();
            column.classList.add('drag-over');
        });
        column.addEventListener('dragleave', () => column.classList.remove('drag-over'));

        column.addEventListener('drop', () => {
            column.classList.remove('drag-over');
            if (!draggedCard) return;

            const oldColumn = draggedCard.parentElement;
            const taskId = draggedCard.dataset.taskId;
            const newStatus = column.dataset.status;

            column.appendChild(draggedCard);

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                },
                body: JSON.stringify({ task_id: taskId, status: newStatus })
            })
            .then(response => {
                if (!response.ok) throw new Error('Status update failed');
                return response.json();
            })
            .then(data => {
                const badge = draggedCard.querySelector('.badge');
                if (badge) {
                    badge.textContent = newStatus.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
                    badge.className = `badge ${data.badge_class || badge.className}`;
                }
            })
            .catch(err => {
                console.error(err);
                oldColumn.appendChild(draggedCard);
            });
        });
    });
});