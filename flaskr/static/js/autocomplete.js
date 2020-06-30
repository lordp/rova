$(document).ready(function() {
    $('#search').select2({
        ajax: {
            url: '/search',
            dataType: 'json',
            delay: 250,
        },
        placeholder: 'Search for a song or artist',
        minimumInputLength: 3,
        width: "100%"
    });

    $('#search').on('select2:select', function (e) {
        var data = e.params.data;
        location.href = '/' + data['type'] + '/' + data['slug'];
    });
});