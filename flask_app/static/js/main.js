document.addEventListener("DOMContentLoaded", function () {
    // Cerrar las alertas después de unos segundos.
    const alerts = document.querySelectorAll(".alert-dismissible");

    alerts.forEach(function (alert) {
        setTimeout(function () {
            const closeBtn = alert.querySelector(".btn-close");
            if (closeBtn) {
                closeBtn.click();
            }
        }, 6000);
    });
});
