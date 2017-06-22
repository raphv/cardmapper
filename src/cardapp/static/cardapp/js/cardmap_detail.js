$(function () {
    var map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -5
    });
    var bounds = [[0, 0], [window.IMAGE_HEIGHT, window.IMAGE_WIDTH]];

    L.imageOverlay(window.IMAGE_URL, bounds).addTo(map);
    map.fitBounds(bounds);

    window.CARDS_JSON.forEach(function (card) {
        var marker = L.marker([card.y, card.x]);
        marker.bindPopup(card.title);
        marker.addTo(map);
        marker.on('mouseover', function () {
            marker.openPopup();
        });
        marker.on('mouseout', function () {
            marker.closePopup();
        });
        marker.on('click', function () {
            $('#card_modal_' + card.id).modal('show');
        });
    });
});
