document.addEventListener('DOMContentLoaded', function() {
    const sectionCards = document.querySelectorAll('.section-card');

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

