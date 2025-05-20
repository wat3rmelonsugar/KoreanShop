$(document).ready(function () {
    $('#search-input').on('keyup', function () {
        let query = $(this).val();
        if (query.length > 1) {
            $.ajax({
                url: "{% url 'products:ajax_search' %}",
                data: {
                    'q': query
                },
                dataType: 'json',
                success: function (data) {
                    let resultBox = $('#search-results');
                    resultBox.empty().show();
                    if (data.results.length > 0) {
                        data.results.forEach(product => {
                            resultBox.append(`<a href="/products/${product.id}/${product.slug}/">${product.name}</a>`);
                        });
                    } else {
                        resultBox.html('<p style="padding: 10px;">Ничего не найдено</p>');
                    }
                }
            });
        } else {
            $('#search-results').hide();
        }
    });

    // Закрытие результатов при клике вне поля
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.search-bar').length) {
            $('#search-results').hide();
        }
    });
});
