$(function () {
    var map = L.map('edit_map', {
        crs: L.CRS.Simple,
        minZoom: -5
    });
    var bounds = [[0, 0], [window.IMAGE_HEIGHT, window.IMAGE_WIDTH]];
    var finalData = [];
    var mapHasChanged = false;

    L.imageOverlay(window.IMAGE_URL, bounds).addTo(map);
    map.fitBounds(bounds);

    function removeMarker(marker) {
        var markerIndex = finalData.indexOf(marker._card_data);
        if (markerIndex >= 0) {
            finalData.splice(markerIndex,1);
            map.removeLayer(marker);
            mapHasChanged = true;
        }
    }

    function addMarkerToMap(card_id, card_title, x, y, open_popup) {
        var marker = L.marker(
            [y, x],
            { "draggable": true }
        );
        var $popup = $("#popup-template").clone();
        $popup.removeAttr("id")
        $popup.find("h3").text(card_title);
        $popup.find("button.popup-modal").click(function () {
            $("#card_modal_" + card_id).modal("show");
            return false;
        });
        $popup.find("button.popup-remove").click(function () {
            removeMarker(marker);
            return false;
        });
        marker.bindPopup($popup[0]);
        marker.addTo(map);
        marker._card_data = {
            "card_id": card_id,
            "x": x,
            "y": y
        }
        marker.on("dragstart", function (event) {
            mapHasChanged = true;
        });
        marker.on("dragend", function (event) {
            var yx = marker.getLatLng();
            marker._card_data.x = yx.lng;
            marker._card_data.y = yx.lat;
        });
        finalData.push(marker._card_data);
        if (open_popup) {
            marker.openPopup();
        }
        return marker;
    }

    $('div.draggable-card-item').on('dragstart', function (event) {
        var $this = $(this);
        event.originalEvent.dataTransfer.setData('application/card-id', $this.attr("data-card-id"));
        event.originalEvent.dataTransfer.setData('application/card-title', $this.find("h4").text());
        event.originalEvent.dataTransfer.effectAllowed = 'copy';
    });

    $('#edit_map').on('dragover dragenter', function () {
        event.preventDefault();
    }).on('drop', function (event) {
        event.preventDefault();
        var card_id = event.originalEvent.dataTransfer.getData("application/card-id");
        var card_title = event.originalEvent.dataTransfer.getData("application/card-title");
        var coords = map.mouseEventToLatLng(event.originalEvent);
        addMarkerToMap(card_id, card_title, coords.lng, coords.lat, true);
        mapHasChanged = true;
    });

    window.CARDS_JSON.forEach(function (card) {
        addMarkerToMap(card.card_id, card.title, card.x, card.y);
    });

    $("button.add-to-map-center").click(function () {
        var $card = $(this).parents("div.draggable-card-item");
        var map_center = map.getCenter();
        var card_title = $card.find("h4").text();
        var card_id = $card.attr("data-card-id");
        addMarkerToMap(card_id, card_title, map_center.lng, map_center.lat, true);
    });

    $("#update-form").submit(function () {
        $("#data_field").val(JSON.stringify(finalData));
        mapHasChanged = false;
    });

    $(window).on("beforeunload", function () {
        if (mapHasChanged) {
            return "Changes to this map will be lost!"
        }
    });

    function removeHighlights() {
        $("div.draggable-card-item span.highlight").each(function () {
            var $h4 = $(this).parent();
            $h4.text($h4.text());
        });
    }

    $("#search-field").on("input", function () {
        removeHighlights();
        var val = $(this).val().toLowerCase();
        if (val.length > 1) {
            $("div.draggable-card-item").each(function () {
                var $this = $(this);
                if ($this.attr("data-search-index").indexOf(val) >= 0) {
                    $this.show();
                    var $h4 = $this.find("h4");
                    var h4_text = $h4.text();
                    var pos = h4_text.toLowerCase().indexOf(val);
                    if (pos >= 0) {
                        var $new = $("<h4>");
                        $new.append(h4_text.substr(0, pos));
                        $new.append($("<span>").addClass("highlight").text(h4_text.substr(pos, val.length)));
                        $new.append(h4_text.substr(pos + val.length));
                        $h4.replaceWith($new);
                    }
                } else {
                    $this.hide();
                }
            });
        } else {
            $("div.draggable-card-item").show();
        }
    });

    $(window).on("keydown", function (event) {
        if (event.ctrlKey && event.key == "f") {
            $("#search-field")[0].focus();
            event.preventDefault();
        }
    });

});
