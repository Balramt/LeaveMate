window.addEventListener("DOMContentLoaded", function () {
    const startDateInput = document.querySelector("input[name='start_date']");
    const endDateInput = document.querySelector("input[name='end_date']");
    const form = document.querySelector(".admin-leave-form") || document.querySelector(".edit-leave-form");

    if (startDateInput && endDateInput && form) {
        startDateInput.addEventListener("change", function () {
            const startDate = startDateInput.value;
            if (startDate) {
                endDateInput.min = startDate;
                // Optional: auto-correct end date if it's before start
                if (new Date(endDateInput.value) < new Date(startDate)) {
                    endDateInput.value = startDate;
                }
            }
        });

        form.addEventListener("submit", function (event) {
            const start = new Date(startDateInput.value);
            const end = new Date(endDateInput.value);

            if (end < start) {
                event.preventDefault();
                alert("❌ End date cannot be before start date!");
            }
        });
    }
});
