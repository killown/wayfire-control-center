document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sectionCards = document.querySelectorAll('.section-card');

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.toLowerCase();
        sectionCards.forEach(function(card) {
            const sectionName = card.querySelector('.card-header h5').textContent.toLowerCase();
            if (sectionName.includes(query)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });

    document.querySelectorAll('.card-header').forEach(header => {
        header.addEventListener('click', () => {
            const targetId = header.getAttribute('data-target');
            const target = document.querySelector(targetId);
            target.classList.toggle('open');
            const isOpen = target.classList.contains('open');
            header.querySelector('.toggle-icon').classList.toggle('fa-chevron-down', !isOpen);
            header.querySelector('.toggle-icon').classList.toggle('fa-chevron-up', isOpen);
        });
    });

    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this option?')) {
                this.closest('form').submit();
            }
        });
    });
});

