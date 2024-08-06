document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sectionCards = document.querySelectorAll('.section-card');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = searchInput.value.toLowerCase();
            sectionCards.forEach(function(card) {
                const sectionName = card.querySelector('.card-header h5').textContent.toLowerCase();
                card.style.display = sectionName.includes(query) ? '' : 'none';
            });
        });
    }

    document.querySelectorAll('.card-header').forEach(header => {
        header.addEventListener('click', () => {
            const targetId = header.getAttribute('data-target');
            const target = document.querySelector(targetId);
            if (target) {
                target.classList.toggle('open');
                const isOpen = target.classList.contains('open');
                header.querySelector('.toggle-icon').classList.toggle('fa-chevron-down', !isOpen);
                header.querySelector('.toggle-icon').classList.toggle('fa-chevron-up', isOpen);
            }
        });
    });

    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default form submission
            const form = this.closest('form');
            deleteOption(form);
        });
    });
});

// Function to handle option deletion
function deleteOption(form) {
    const sectionInput = form.querySelector('input[name="section"]');
    const optionInput = form.querySelector('input[name="option"]');
    
    if (!sectionInput || !optionInput) {
        console.error('Required input fields not found in the form.');
        return;
    }
    
    const section = sectionInput.value;
    const option = optionInput.value;

    if (confirm('Are you sure you want to delete this option?')) {
        fetch('/delete_option', {  // Ensure the endpoint matches your Flask route
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                section: section,
                option: option
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); // Reload the page to reflect changes
            } else {
                alert('Failed to delete option: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the option.');
        });
    }
}

// Function to handle adding new options
function addNewOption(event, section) {
    event.preventDefault();
    
    const form = event.target;
    const newOptionName = form.querySelector('input[name="newOption"]').value;
    const newOptionValue = form.querySelector('input[name="newValue"]').value;
    
    fetch('/add_option', {  // Ensure the endpoint matches your Flask route
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            section: section,
            option: newOptionName,
            value: newOptionValue
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload(); // Reload the page to reflect changes
        } else {
            alert('Failed to add new option: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the new option.');
    });
}

