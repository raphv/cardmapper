$(function () {

    var $win = $(window);
    var $searchableItems = $(".searchable-item");
    var $searchField = $("#search-field");
    var $formGroup = $searchField.parents(".input-group");
    var defaultTitle = $searchField.attr("title");

    $searchField.tooltip({
        placement: "left",
        animation: false,
    });

    $searchableItems.each(function () {
        var $this = $(this);
        var searchIndex = Array.from($this.find(".searchable-field").map(function () {
            return $(this).text();
        })).join(" ").toLowerCase();
        $this.attr("data-search-index", searchIndex);
    });

    $searchField.on("input", function () {
        $searchableItems.find("span.highlight").each(function () {
            var $highlightParent = $(this).parent();
            $highlightParent.text($highlightParent.text());
        });
        $formGroup.removeClass("has-success has-error");
        var val = $searchField.val().toLowerCase();
        if (val.length > 1) {
            var resultCount = 0;
            $searchableItems.each(function () {
                var $this = $(this);
                if ($this.attr("data-search-index").indexOf(val) >= 0) {
                    $this.show();
                    resultCount++;
                    $this.find(".searchable-field").each(function () {
                        var $element = $(this);
                        var el_text = $element.text();
                        var pos = el_text.toLowerCase().indexOf(val);
                        if (pos >= 0) {
                            $element.empty();
                            $element.append(el_text.substr(0, pos));
                            $element.append($("<span>").addClass("highlight").text(el_text.substr(pos, val.length)));
                            $element.append(el_text.substr(pos + val.length));
                        }
                    });
                } else {
                    $this.hide();
                }
            });
            $formGroup.addClass(resultCount ? "has-success" : "has-error");
            $searchField.attr("title", resultCount + " item(s) found")
                .tooltip('fixTitle').tooltip('show');
        } else {
            $searchableItems.show();
            $searchField.attr("title", defaultTitle).tooltip('fixTitle').tooltip('hide');
        }
        $win.trigger("resize");
    });

    $win.on("keydown", function (event) {
        if (event.ctrlKey && event.key == "f") {
            $("#search-field")[0].focus();
            event.preventDefault();
        }
    });
});
