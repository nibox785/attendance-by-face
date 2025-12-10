// Sidebar menu functionality
(function($) {
    "use strict";
    
    $(document).ready(function() {
        // Sidebar toggle
        $(".sidebartoggler").on("click", function() {
            $("#main-wrapper").toggleClass("mini-sidebar");
        });
        
        // Mobile menu toggle
        $(".nav-toggler").on("click", function() {
            $("body").toggleClass("show-sidebar");
            $(this).toggleClass("ti-menu");
            $(this).toggleClass("ti-close");
        });
        
        // Submenu handling - has-arrow items
        $("#sidebarnav a.has-arrow").on("click", function(e) {
            e.preventDefault();
            var $submenu = $(this).next("ul");
            
            // Close other submenus
            $("#sidebarnav a.has-arrow").not(this).removeClass("active");
            $("#sidebarnav a.has-arrow").not(this).next("ul").slideUp(200).removeClass("in");
            
            // Toggle current submenu
            if ($submenu.hasClass("in")) {
                $submenu.slideUp(200).removeClass("in");
                $(this).removeClass("active");
            } else {
                $submenu.slideDown(200).addClass("in");
                $(this).addClass("active");
            }
        });
        
        // Perfect scrollbar for sidebar (if exists)
        if ($(".scroll-sidebar").length) {
            $(".scroll-sidebar").css({"overflow": "auto"});
        }
        
        // Set active menu based on current URL
        var url = window.location.href;
        $("#sidebarnav a").each(function() {
            if (this.href === url) {
                $(this).addClass("active");
                $(this).parents(".sidebar-item").addClass("selected");
                $(this).parents("ul").addClass("in").prev("a").addClass("active");
            }
        });
    });
    
})(jQuery);
