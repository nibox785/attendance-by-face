// Waves effect for material design
(function() {
    'use strict';
    
    var Waves = {
        init: function() {
            var ripples = document.querySelectorAll('.waves-effect');
            ripples.forEach(function(ripple) {
                ripple.addEventListener('click', function(e) {
                    var rect = this.getBoundingClientRect();
                    var rippleX = e.clientX - rect.left;
                    var rippleY = e.clientY - rect.top;
                    
                    var rippleElement = document.createElement('span');
                    rippleElement.classList.add('waves-ripple');
                    rippleElement.style.left = rippleX + 'px';
                    rippleElement.style.top = rippleY + 'px';
                    
                    this.appendChild(rippleElement);
                    
                    setTimeout(function() {
                        rippleElement.remove();
                    }, 600);
                });
            });
        }
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', Waves.init);
    } else {
        Waves.init();
    }
})();
