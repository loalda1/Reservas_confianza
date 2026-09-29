document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(".ajax-estado-form");

    forms.forEach(function (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const button = form.querySelector("button");
            const originalText = button.textContent;

            button.disabled = true;
            button.textContent = "Processing...";

            try {
                const csrfToken = form.querySelector(
                    "input[name='csrfmiddlewaretoken']"
                ).value;

                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrfToken,
                    },
                    body: new FormData(form),
                });

                if (!response.ok) {
                    const failure = await response.json().catch(() => ({}));
                    throw new Error((failure.errors || ["Request failed"]).join(" "));
                }

                const data = await response.json();

                if (data.ok) {
                    const statusLabel = document.getElementById(
                        "estado-reserva-" + data.id
                    );

                    statusLabel.textContent = data.estado_display;
                    statusLabel.className = "estado estado-" + data.estado;
                }
            } catch (error) {
                alert(error.message || "The booking status could not be updated.");
            } finally {
                button.disabled = false;
                button.textContent = originalText;
            }
        });
    });
});
