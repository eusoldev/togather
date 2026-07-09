odoo.define('contract_and_offer.main', function(require) {

    const AbstractAction = require('web.AbstractAction');

    const core = require('web.core');

    const OurAction = AbstractAction.extend({

        start: function() {
            console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                console.log(xhttp.responseText)
                if (this.readyState == 4 && this.status == 200) {
                    // Typical action to be performed when the document is ready:
                    document.getElementById("demo").innerHTML = xhttp.responseText;
                } else {
                    console.log("error");
                }
            };
            xhttp.open("GET", "https://cors-anywhere.herokuapp.com/https://maps.googleapis.com/maps/api/js?v=quarterly&amp;key=AIzaSyAed63K1yIX7WsLjWW-tesAIeiirY9EMws&amp;libraries=geometry,places&amp;language=en&amp;region=MV", true);
            xhttp.send();
            console.log("dddddddddddddddddddddddd");
        }
    });
    core.action_registry.add('contract_and_offer.action', OurAction);
});