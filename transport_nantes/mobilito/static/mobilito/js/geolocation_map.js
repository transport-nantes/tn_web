/*
# DOCUMENTATION
LeafletJS
https://leafletjs.com/examples/quick-start/

Google reverse geocoding API
https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding
*/

// Initializing the map
var map = L.map('map').setView([47.218371, -1.553621], 8);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
// Add locate user control
const LOCATE_OPTIONS = {
    drawCircle: false,
    strings: {
        popup: ({ distance, unit }) => {
            return `<p>Vous êtes dans les ${distance} ${unit} de ce point.</p>`
        },
        metersUnit: "mètres"
    },
    setView: false,
    clickBehavior: {
        inView: 'stop',
        outOfView: 'stop',
        inViewNotFollowing: 'stop'
    },
    icon: 'fa-solid fa-location-crosshairs'

}
L.control.locate(LOCATE_OPTIONS).addTo(map);
var marker;
// geocoder uses per default nominatim.openstreetmap.org as geocoding service
// https://nominatim.org/release-docs/develop/api/Search/
// This API doesn't require an API key, but it's limited to 1 request per second.
// (see : https://operations.osmfoundation.org/policies/nominatim/)
// This geocoder's source code is accessible here :
// https://github.com/perliedman/leaflet-control-geocoder
// It's compatible with Google Maps API according to its readme, but I couldn't
// find where to set the API key just yet.
// Because the number of requests has very low chance to exceed 1 per sec
// for now, we can stick to nominatim but the Google Maps API is still an option
// if we need to.
var geocoder = L.Control.geocoder(
    { defaultMarkGeocode: false, }
).on(
    'markgeocode', function (e) {
        var customEvent = {
            latlng: e.geocode.center,
        }
        onMapClick(customEvent);
    })
geocoder.addTo(map);
// Pressing share-location button will trigger the geolocation, once user
// has granted permission to share location.
$('#share-location').on('click', function () {
    map.locate({ setView: true, maxZoom: 16 });
});

// What happens when user has granted permission to share location and it's
// been found.
function onLocationFound(e) {
    // setView centers the map on the user's location, whith a zoom level that
    // depends on the event's accuracy. (More accurate = zoom level higher)
    // https://leafletjs.com/examples/zoom-levels/
    if (e.accuracy > 1000) {
        map.setView(e.latlng, 12);
    } else {
        map.setView(e.latlng, 16);
    }
    // Add a marker to the map the same way we do for clicks
    onMapClick(e);
}
map.on('locationfound', onLocationFound);

var isLoading = false;
// What happens when user clicks on the map.
function onMapClick(e) {
    // If position location is toggled ON and user clicks on the map, we
    // toggle off the control. A way to see if the location is toggled on is
    // to check if the div with the class 'leaflet-control-locate' has the
    // class 'active'.
    if ($('.leaflet-control-locate').hasClass('active')) {
        // The <a> element inside the control effectively toggles the control
        // on/off.
        $('a.leaflet-bar-part')[0].click();
    }
    // If the user is already loading, don't do anything.
    if (isLoading) {
        return;
    }
    // We only want one marker on the map.
    if (marker) {
        map.removeLayer(marker);
    }
    isLoading = true;
    $('#id_latitude').val(`${e.latlng.lat}`)
    $('#id_longitude').val(`${e.latlng.lng}`)
    marker = L.marker(e.latlng).addTo(map)
    // Geocode the latitude and longitude of the click and display the address.
    getGeocodedAddress(e.latlng.lat, e.latlng.lng).then(function (data) {
        // Maps API has a spec for status codes, see :
        // https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding#reverse-status-codes
        if (data.status === "OK") {
            let addr = data.results[0].formatted_address;
            marker.bindPopup(`${addr}`).openPopup();
            $('#id_location').val(`${addr}`)
        } else {
            $('#id_location').val("")
        }
        isLoading = false;
    });
}
map.on('click', onMapClick);

// Function to get user's location with geocoding, limited 50 requests per second.
async function getGeocodedAddress(lat, lng) {
    let url = "/mobilito/ajax/get-address/";
    let response = await $.ajax({
        url: url,
        headers: {"X-CSRFToken": getCookie("csrftoken")},
        type: 'POST',
        dataType: 'json',
        data: {
            lat: lat,
            lng: lng,
        },
        mode: 'same-origin',
        error: function (err) {
            console.log(err);
        }
    });
    return response;
}
