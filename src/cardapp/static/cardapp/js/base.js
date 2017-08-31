$(function () {
    function equalizeGrid() {
        $(".row.grid").each(function () {
            var $children = $(this).find(">div>div");
            $children.css("height", "auto");
            var maxH = Math.max.apply(Math, $children.map(function () {
                return $(this).height();
            }));
            $children.css("height", maxH);
        });
    }
    $(window).on("resize load", equalizeGrid);
    equalizeGrid();
});
