/*
# DOCUMENTATION
LeafletJS
https://leafletjs.com/examples/quick-start/

Google reverse geocoding API
https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding
*/

// Initializing the map
var map = L.map('map').fitWorld();
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
    }
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
    // Display the map with the user's location.
    $('#map').css('display', 'block');
    // Display None prevents the map from knowing its size, calling
    // invalidateSize() once the map has an actual size fixes a bug where the
    // map doesn't display properly. (Apparently, it doesn't know how many
    // tiles it has to load)
    map.invalidateSize();
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
    // If the user is already loading, don't do anything.
    if (isLoading) {
        return;
    }
    // We only want one marker on the map.
    if (marker) {
        map.removeLayer(marker);
    }
    isLoading = true;
    // Geocode the latitude and longitude of the click and display the address.
    getGeocodedAddress(e.latlng.lat, e.latlng.lng).then(function (data) {
        let addr = data.results[0].formatted_address;
        marker = L.marker(e.latlng).addTo(map)
            .bindPopup(`${addr}`).openPopup();
        $('#id_location').val(`${addr}`)
        $('#id_latitude').val(`${e.latlng.lat}`)
        $('#id_longitude').val(`${e.latlng.lng}`)
        isLoading = false;
    });
}
map.on('click', onMapClick);

// Function to get user's location with geocoding, limited 50 requests per second.
async function getGeocodedAddress(lat, lng) {
    let api_key = JSON.parse(document.getElementById('maps_api_key').textContent);
    let url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${api_key}`;
    let response = await $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log(data);
        },
        error: function (err) {
            console.log(err);
        }
    });
    return response;
}
