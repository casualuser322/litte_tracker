const emailInput = document.getElementById("emailInput");
const autocompleteUrl = emailInput.dataset.autocompleteUrl;
const suggestionsBox = document.getElementById("suggestionsBox");
const selectedEmails = document.getElementById("selectedEmails");
const emailsHidden = document.getElementById("emailsHidden");

let emails = [];
emailInput.addEventListener("input", async () => {
    const query = emailInput.value;
    if (query.length < 2) {
        suggestionsBox.style.display = "none";
        return;
    }

    const response = await fetch(`${autocompleteUrl}?q=${query}`);
    const data = await response.json();

    suggestionsBox.innerHTML = "";
    if (data.length > 0) {
        suggestionsBox.style.display = "block";
        data.forEach(user => {
            let li = document.createElement("li");
            li.classList.add("list-group-item", "list-group-item-action");
            li.textContent = user.email;
            li.onclick = () => addEmail(user.email);
            suggestionsBox.appendChild(li);
        });
    } else {
        suggestionsBox.style.display = "none";
    }
});

function addEmail(email) {
    if (emails.includes(email)) return;

    emails.push(email);

    const chip = document.createElement("span");
    chip.classList.add("badge", "bg-primary", "p-2");
    chip.innerHTML = `${email} <button type="button" class="btn-close btn-close-white btn-sm ms-1" aria-label="Remove"></button>`;

    chip.querySelector("button").onclick = () => {
        selectedEmails.removeChild(chip);
        emails = emails.filter(e => e !== email);
        updateHiddenField();
    };

    selectedEmails.appendChild(chip);
    updateHiddenField();

    emailInput.value = "";
    suggestionsBox.style.display = "none";
}

function updateHiddenField() {
    emailsHidden.value = emails.join(",");
}

document.addEventListener("click", (e) => {
    if (!emailInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.style.display = "none";
    }
});