document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const sectionCards = document.querySelectorAll(".section-card");

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = searchInput.value.toLowerCase();
      sectionCards.forEach(function (card) {
        const sectionName = card
          .querySelector(".card-header h5")
          .textContent.toLowerCase();
        card.style.display = sectionName.includes(query) ? "" : "none";
      });
    });
  }

  document.querySelectorAll(".card-header").forEach((header) => {
    header.addEventListener("click", () => {
      const targetId = header.getAttribute("data-target");
      const target = document.querySelector(targetId);
      if (target) {
        target.classList.toggle("open");
        const isOpen = target.classList.contains("open");
        header
          .querySelector(".toggle-icon")
          .classList.toggle("fa-chevron-down", !isOpen);
        header
          .querySelector(".toggle-icon")
          .classList.toggle("fa-chevron-up", isOpen);
      }
    });
  });

  document.querySelectorAll(".delete-button").forEach((button) => {
    button.addEventListener("click", function () {
      if (confirm("Are you sure you want to delete this option?")) {
        deleteOption(this);
      }
    });
  });

  // Save configuration while typing in input fields
  document.querySelectorAll("input[data-save]").forEach((input) => {
    input.addEventListener("change", function () {
      const sectionElement =
        this.closest(".section-card").querySelector(".card-header h5");
      const section = sectionElement ? sectionElement.textContent.trim() : "";
      const option = this.getAttribute("data-option");
      const value = this.value;

      // Log values for debugging
      console.log("Updating option:", { section, option, value });

      updateOption(section, option, value);
    });
  });
});

// Handle deleting an option
function deleteOption(button) {
  const form = button.closest("form");
  const section = form.querySelector('input[name="section"]').value;
  const option = form.querySelector('input[name="option"]').value;

  fetch("/delete_option", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      section: section,
      option: option,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        location.reload(); // Reload the page to reflect changes
      } else {
        alert("Failed to delete option: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while deleting the option.");
    });
}

// Handle adding new options
function addNewOption(event, section) {
  event.preventDefault();

  const form = event.target;
  const newOptionName = form.querySelector('input[name="newOption"]').value;
  const newOptionValue = form.querySelector('input[name="newValue"]').value;

  fetch("/add_option", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      section: section,
      option: newOptionName,
      value: newOptionValue,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        location.reload(); // Reload the page to reflect changes
      } else {
        alert("Failed to add new option: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while adding the new option.");
    });
}

// Handle creating new section
function createNewSection(event) {
  event.preventDefault();

  const form = event.target;
  const sectionName = form.querySelector('input[name="section_name"]').value;
  const optionName = form.querySelector('input[name="option_name"]').value;
  const optionValue = form.querySelector('input[name="option_value"]').value;

  fetch("/create_section", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      section_name: sectionName,
      option_name: optionName,
      option_value: optionValue,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        location.reload(); // Reload the page to reflect changes
      } else {
        alert("Failed to create section: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while creating the section.");
    });
}

// Toggle visibility of create new section form
function toggleCreateSectionForm() {
  const form = document.getElementById("createSectionForm");
  form.style.display = form.style.display === "none" ? "block" : "none";
}

function updateValue(event) {
  const input = event.target;
  const section = input.dataset.section;
  const option = input.dataset.option;
  const value = input.value;

  fetch("/update_option", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      section: section,
      option: option,
      value: value,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        console.log("Configuration updated successfully");
      } else {
        console.error("Failed to update configuration:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Update an existing option in the configuration file
function updateOption(section, option, value) {
  fetch("/update_option", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      section: section,
      option: option,
      value: value,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status !== "success") {
        alert("Failed to update option: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while updating the option.");
    });
}
