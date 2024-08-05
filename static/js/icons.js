// icons.js

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

// Handle adding new options
function addNewOption(event, section) {
    event.preventDefault();
    
    const form = event.target;
    const newOptionName = form.querySelector('input[name="newOption"]').value;
    const newOptionValue = form.querySelector('input[name="newValue"]').value;
    
    fetch('/create_section', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            section_name: section,
            option_name: newOptionName,
            option_value: newOptionValue
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload(); // Reload the page to reflect changes
        } else {
            alert('Failed to add new option: ' + data.message);
        }
    });
}

