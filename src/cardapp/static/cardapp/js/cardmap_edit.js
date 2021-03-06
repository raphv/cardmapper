$(function () {
    var map = L.map('edit_map', {
        crs: L.CRS.Simple,
        minZoom: -5
    });
    var bounds = [[0, 0], [window.IMAGE_HEIGHT, window.IMAGE_WIDTH]];
    var finalData = {
        "annotations": [],
        "cards": [],
    };
    var mapHasChanged = false;

    L.imageOverlay(window.IMAGE_URL, bounds).addTo(map);
    map.fitBounds(bounds);

    function addCardMarkerToMap(card_id, card_title, x, y, open_popup) {
        var marker = L.marker(
            [y, x],
            {
                "draggable": true,
                "icon": window.CARD_ICON
            }
        );
        var $popup = $("#card-template").clone();
        var card_data = {
            "card_id": card_id,
            "x": x,
            "y": y
        };
        finalData.cards.push(card_data);
        $popup.removeAttr("id")
        $popup.find("h3").text(card_title);
        $popup.find("button.popup-modal").click(function () {
            $("#card_modal_" + card_id).modal("show");
            return false;
        });
        $popup.find("button.popup-remove").click(function () {
            var card_index = finalData.cards.indexOf(card_data);
            if (card_index >= 0) {
                finalData.cards.splice(card_index, 1);
                map.removeLayer(marker);
                mapHasChanged = true;
            }
            return false;
        });
        marker.bindPopup($popup[0]);
        marker.addTo(map); 
        marker.on("dragstart", function (event) {
            mapHasChanged = true;
        });
        marker.on("dragend", function (event) {
            var yx = marker.getLatLng();
            card_data.x = yx.lng;
            card_data.y = yx.lat;
        });
        if (open_popup) {
            marker.openPopup();
        }
        return marker;
    }

    function addAnnotationMarkerToMap(content, x, y, open_popup) {
        var marker = L.marker(
            [y, x],
            {
                "draggable": true,
                "icon": window.ANNOTATION_ICON
            }
        );
        var $popup = $("#annotation-template").clone();
        var annotation_data = {
            "content": content,
            "x": x,
            "y": y
        };
        finalData.annotations.push(annotation_data);
        $popup.removeAttr("id")
        $popup.find("textarea").val(content).on("input", function () {
            annotation_data.content = $(this).val();
            mapHasChanged = true;
        });
        $popup.find("button.popup-remove").click(function () {
            var card_index = finalData.annotations.indexOf(annotation_data);
            if (card_index >= 0) {
                finalData.annotations.splice(card_index, 1);
                map.removeLayer(marker);
                mapHasChanged = true;
            }
            return false;
        });
        marker.bindPopup($popup[0]);
        marker.addTo(map);
        marker.on("dragstart", function (event) {
            mapHasChanged = true;
        });
        marker.on("dragend", function (event) {
            var yx = marker.getLatLng();
            annotation_data.x = yx.lng;
            annotation_data.y = yx.lat;
        });
        if (open_popup) {
            marker.openPopup();
        }
        return marker;
    }

    $('div.draggable-card-item').on('dragstart', function (event) {
        var $this = $(this);
        event.originalEvent.dataTransfer.setData('application/card-id', $this.attr("data-card-id"));
        event.originalEvent.dataTransfer.setData('application/card-title', $this.find(".card-title").text());
        event.originalEvent.dataTransfer.effectAllowed = 'copy';
    });

    $('#edit_map').on('dragover dragenter', function () {
        event.preventDefault();
    }).on('drop', function (event) {
        event.preventDefault();
        var card_id = event.originalEvent.dataTransfer.getData("application/card-id");
        var card_title = event.originalEvent.dataTransfer.getData("application/card-title");
        var coords = map.mouseEventToLatLng(event.originalEvent);
        addCardMarkerToMap(card_id, card_title, coords.lng, coords.lat, true);
        mapHasChanged = true;
    });

    window.CARDS_JSON.forEach(function (card) {
        addCardMarkerToMap(card.card_id, card.title, card.x, card.y);
    });

    window.ANNOTATIONS_JSON.forEach(function (annotation) {
        addAnnotationMarkerToMap(annotation.content, annotation.x, annotation.y);
    });

    map.doubleClickZoom.disable();
    map.on("dblclick", function (event) {
        var p = event.latlng;
        addAnnotationMarkerToMap("", p.lng, p.lat, true);
    });

    $("button.add-to-map-center").click(function () {
        var $card = $(this).parents("div.draggable-card-item");
        var map_center = map.getCenter();
        var card_title = $card.find(".card-title").text();
        var card_id = $card.attr("data-card-id");
        addCardMarkerToMap(card_id, card_title, map_center.lng, map_center.lat, true);
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
            var $highlightParent = $(this).parent();
            $highlightParent.text($highlightParent.text());
        });
    }

    function highlightElement($element, val) {
        var el_text = $element.text();
        var pos = el_text.toLowerCase().indexOf(val);
        if (pos >= 0) {
            $element.empty();
            $element.append(el_text.substr(0, pos));
            $element.append($("<span>").addClass("highlight").text(el_text.substr(pos, val.length)));
            $element.append(el_text.substr(pos + val.length));
        }
    }

    $("#search-field").on("input", function () {
        removeHighlights();
        var val = $(this).val().toLowerCase();
        if (val.length > 1) {
            $("div.draggable-card-item").each(function () {
                var $this = $(this);
                if ($this.attr("data-search-index").indexOf(val) >= 0) {
                    $this.show();
                    highlightElement($this.find(".card-title"), val);
                    highlightElement($this.find(".card-tags"), val);
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
    
    var current_item = null;
    var $dragged_copy = null;
    var origin_touch_x = null;
    var origin_touch_y = null;
    var original_offset = null;
    function endMove() {
        if ($dragged_copy) {
            $dragged_copy.remove();
            $(current_item).css("opacity", 1);
        }
        current_item = null;
        $dragged_copy = null;
    }
    function moveCopy(touch_x, touch_y) {
        $dragged_copy.css({
            "left": (original_offset.left + touch_x - origin_touch_x) + "px",
            "top": (original_offset.top + touch_y - origin_touch_y) + "px",
        });
    }
    $(window).on("touchmove", function (event) {
        if ($dragged_copy) {
            var touches = event.originalEvent.touches;
            if (touches.length == 1) {
                moveCopy(touches[0].clientX, touches[0].clientY);
            } else {
                endMove();
            }
        }
    }).on("touchend", function () {
        if ($dragged_copy) {
            var $map = $("#edit_map");
            var map_off = $map.offset();
            var dc_offset = $dragged_copy.offset();
            var x = dc_offset.left + $dragged_copy.width() / 2;
            var y = dc_offset.top + $dragged_copy.height() / 2;
            if (x >= map_off.left
                && x <= (map_off.left + $map.width())
                && y >= map_off.top
                && y <= (map_off.top + $map.height())) {
                var card_title = $dragged_copy.find(".card-title").text();
                var card_id = $dragged_copy.attr("data-card-id");
                var coords = map.mouseEventToLatLng({ "clientX": x, "clientY": y });
                addCardMarkerToMap(card_id, card_title, coords.lng, coords.lat, true);
            }
            endMove();
        }
    });
    $("div.draggable-card-item").on('touchstart', function (event) {
        var touches = event.originalEvent.touches;
        if (touches.length == 1) {
            current_item = this;
            origin_touch_x = touches[0].clientX;
            origin_touch_y = touches[0].clientY;
        }
    }).on('touchmove', function (event) {
        var touches = event.originalEvent.touches;
        if (current_item == this && !$dragged_copy && touches.length == 1) {
            var touch_x = touches[0].clientX;
            if (origin_touch_x - touch_x > 5) { // Must have sufficiently moved left
                var $original = $(current_item);
                original_offset = $original.offset();
                $dragged_copy = $original.clone();
                $dragged_copy.css({
                    "position": "absolute",
                    "z-index": 1200,
                    "width": $original.width(),
                    "height": $original.height(),
                    "box-sizing": "border-box",
                    "opacity": .7,
                }).appendTo("body");
                moveCopy(touch_x, touches[0].clientY);
                $original.css("opacity", .2);
            }
        }
    });

});
