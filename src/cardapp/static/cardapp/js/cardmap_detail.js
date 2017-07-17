$(function () {
    var map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -5
    });
    var bounds = [[0, 0], [window.IMAGE_HEIGHT, window.IMAGE_WIDTH]];

    L.imageOverlay(window.IMAGE_URL, bounds).addTo(map);
    map.fitBounds(bounds);

    window.CARDS_JSON.forEach(function (card) {
        var marker = L.marker(
            [card.y, card.x],
            {icon: window.CARD_ICON}
        );
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

    window.ANNOTATIONS_JSON.forEach(function (annotation) {
        var marker = L.marker(
            [annotation.y, annotation.x],
            { icon: window.ANNOTATION_ICON }
        );
        marker.bindPopup(annotation.content);
        marker.addTo(map);
        marker.on('mouseover', function () {
            marker.openPopup();
        });
        marker.on('mouseout', function () {
            marker.closePopup();
        });
        marker.on('click', function () {
            $('#annotation_modal_' + annotation.id).modal('show');
        });
    });
});
