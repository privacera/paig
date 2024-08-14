document.addEventListener('DOMContentLoaded', function () {
    var downloadLinks = document.querySelectorAll('a[link-download]');

    downloadLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            var url = link.getAttribute('href');
            var filename = link.getAttribute('link-download');

            fetch(url)
                .then(response => response.blob())
                .then(blob => {
                    var a = document.createElement('a');
                    var url = window.URL.createObjectURL(blob);
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }, 0);
                });
        });
    });
});
