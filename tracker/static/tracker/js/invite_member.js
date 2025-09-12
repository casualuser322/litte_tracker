document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("invite-btn");
    const input = document.getElementById("emailInput");
    const hidden = document.getElementById("emailsHidden");
    const form = btn.closest("form");

    let expanded = false;

    btn.addEventListener("click", (e) => {
        if (!expanded) {
            expanded = true;
            input.style.maxWidth = "250px";
            input.style.opacity = "1";
            input.focus();

            btn.textContent = "Send";
        } else {
            const email = hidden.value.trim();
            if (!email) {
                return alert("Enter email");
            }

            form.submit();
        }
    });
});
