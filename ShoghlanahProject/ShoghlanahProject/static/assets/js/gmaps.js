  var geocoder;
  var map;
  var marker;
  var zoom;

  function getLocation(callback){
    if (navigator.geolocation){
      navigator.geolocation.getCurrentPosition(function (position){
        latlng = position.coords.latitude + "," + position.coords.longitude;
        callback(latlng);         
      }, showError);
    }
    else{
      gmaps_init(null);
    }
  }

  function showError(error)
  {
    gmaps_init(null);
  }
  // initialise the google maps objects, and add listeners
  function gmaps_init(position){

    // center of the universe
      // add if to support if now location
      
    if(position==null){
      latlng = new google.maps.LatLng(30.0444,31.2357);
      zoom=10;
    }
    else{
      position = position.split(',');
      latlng = new google.maps.LatLng(position[0], position[1]);
      zoom=13;
    }
    
    var options = {
      zoom: zoom,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    // create our map object
    map = new google.maps.Map(document.getElementById("map_canvas"), options);

    // the geocoder object allows us to do latlng lookup based on address
    geocoder = new google.maps.Geocoder();

    // the marker shows us the position of the latest address
    marker = new google.maps.Marker({
      map: map,
      draggable: true
    });

    //default inputbox to update
    textfield = typeof textfield !== 'undefined' ? textfield : '#gmaps-input-address';
    the_marker = typeof the_marker !== 'undefined' ? the_marker : marker;
    the_map = typeof the_map !== 'undefined' ? the_map : map;
    
    // event triggered when marker is dragged and dropped
    google.maps.event.addListener(marker, 'dragend', function() {
      geocode_lookup( 'latLng', marker.getPosition(), textfield);
    });

    // event triggered when map is clicked
    google.maps.event.addListener(map, 'click', function(event) {
      marker.setPosition(event.latLng);
      geocode_lookup( 'latLng', event.latLng, textfield);
    });

    if(position!=null){
      geocode_lookup('latLng',latlng, textfield, the_map, the_marker, true);
    }
    
  }

  function final_update(){
    if(typeof map !== 'undefined'){
      google.maps.event.trigger(map, 'resize'); 
      map.setCenter(latlng);
      map.setZoom(zoom);   
    }
    else{
      getLocation(function(latlng){
        gmaps_init(latlng); 
      });
    }
    
  }
  // move the marker to a new position, and center the map on it
  function update_map( geometry, the_map, the_marker) {
    the_marker = typeof the_marker !== 'undefined' ? the_marker : marker;
    the_map = typeof the_map !== 'undefined' ? the_map : map;
    the_map.fitBounds( geometry.viewport );
    the_marker.setPosition( geometry.location );
  }

  // fill in the UI elements with new position data
  function update_ui( address, latLng , textfield) {
    //textfield = typeof textfield !== 'undefined' ? textfield : '#gmaps-input-address';
    $(textfield).autocomplete("close");
    $(textfield).val(address);
    $('#gmaps-output-latitude').val(latLng.lat());
    $('#gmaps-output-longitude').val(latLng.lng());
  }

  // Query the Google geocode object
  //
  // type: 'address' for search by address
  //       'latLng'  for search by latLng (reverse lookup)
  //
  // value: search query
  //
  // update: should we update the map (center map and position marker)?
  function geocode_lookup( type, value, textfield, the_map, the_marker, update ) {
    // default value: update = false
    update = typeof update !== 'undefined' ? update : false;
    textfield = typeof textfield !== 'undefined' ? textfield : '#gmaps-input-address';

    request = {};
    request[type] = value;

    geocoder.geocode(request, function(results, status) {
      $('#gmaps-error').html('');
      if (status == google.maps.GeocoderStatus.OK) {
        // Google geocoding has succeeded!
        if (results[0]) {
          // Always update the UI elements with new location data
          update_ui( results[0].formatted_address,
                     results[0].geometry.location,
                     textfield )

          // Only update the map (position marker and center map) if requested
          if( update ) {
             if(textfield == '#gmaps-input-address'){
              update_map( results[0].geometry )
            }
            else{
              update_map( results[0].geometry, the_map, the_marker)
            }
          }
        } else {
          // Geocoder status ok but no results!?
          $('#gmaps-error').html("Sorry, something went wrong. Try again!");
        }
      } else {
        // Google Geocoding has failed. Two common reasons:
        //   * Address not recognised (e.g. search for 'zxxzcxczxcx')
        //   * Location doesn't map to address (e.g. click in middle of Atlantic)

        if( type == 'address' ) {
          // User has typed in an address which we can't geocode to a location
          $('#gmaps-error').html("Sorry! We couldn't find " + value + ". Try a different search term, or click the map." );
        } else {
          // User has clicked or dragged marker to somewhere that Google can't do a reverse lookup for
          // In this case we display a warning, clear the address box, but fill in LatLng
          $('#gmaps-error').html("Woah... that's pretty remote! You're going to have to manually enter a place name." );
          update_ui('', value,textfield)
        }
      };
    });
  };

  // initialise the jqueryUI autocomplete element
  function autocomplete_init(textfield, the_marker, the_map) {
    the_marker = typeof the_marker !== 'undefined' ? the_marker : marker;
    the_map = typeof the_map !== 'undefined' ? the_map : map;
    textfield = typeof textfield !== 'undefined' ? textfield : '#gmaps-input-address';
    $(textfield).autocomplete({

      // source is the list of input options shown in the autocomplete dropdown.
      // see documentation: http://jqueryui.com/demos/autocomplete/
      source: function(request,response) {

        // the geocode method takes an address or LatLng to search for
        // and a callback function which should process the results into
        // a format accepted by jqueryUI autocomplete
        geocoder.geocode( {'address': request.term }, function(results, status) {
          response($.map(results, function(item) {
            return {
              label: item.formatted_address, // appears in dropdown box
              value: item.formatted_address, // inserted into input element when selected
              geocode: item                  // all geocode data: used in select callback event
            }
          }));
        })
      },

      // event triggered when drop-down option selected
      select: function(event,ui){
        update_ui(  ui.item.value, ui.item.geocode.geometry.location, textfield )
        if(textfield == '#gmaps-input-address'){
          update_map( ui.item.geocode.geometry)
        }
        else{
          update_map( ui.item.geocode.geometry, the_map, the_marker)
        }
        
      }
    });

    // triggered when user presses a key in the address box
    $(textfield).bind('keydown', function(event) {
      if(event.keyCode == 13) {
        geocode_lookup( 'address', $(textfield).val(), textfield, the_map, the_marker, true );

        // ensures dropdown disappears when enter is pressed
        $(textfield).autocomplete("disable")
      } else {
        // re-enable if previously disabled above
        $(textfield).autocomplete("enable")
      }
    });
  }; // autocomplete_init

  $(document).ready(function() { 
    if( $('#map_canvas').length ) {
      getLocation(function(latlng){
       gmaps_init(latlng); 
     });
      
      autocomplete_init();
    };  

  });

  function switchMap(edit_marker,edit_map,edit_text, txt_lat, txt_lng){
      var edit_lng; var edit_lat;
      if(edit_marker == null){
          edit_marker = new google.maps.Marker({
              map: edit_map,
              draggable: false
          });
      }
      edit_marker.setDraggable(true);
      if(edit_marker.position){
          var new_position = edit_marker.getPosition();
          edit_lat = new_position.lat();
          edit_lng = new_position.lng();
          edit_map.setCenter(edit_marker.getPosition());
          edit_map.setZoom(13);
      }
      else{
          edit_map.setCenter(new google.maps.LatLng(30.0444,31.2357));
          edit_map.setZoom(10);
      }
      autocomplete_init(edit_text,edit_marker,edit_map);
      
      google.maps.event.addListener(edit_marker, 'dragend', function() {
        geocode_lookup( 'latLng', edit_marker.getPosition(), edit_text, edit_map, edit_marker);
      });

      google.maps.event.addListener(edit_map, 'click', function(event) {
        edit_marker.setPosition(event.latLng);
        geocode_lookup( 'latLng', event.latLng, edit_text, edit_map, edit_marker  );
      });

      google.maps.event.addListener(edit_marker, 'position_changed', function() {
          var new_position = edit_marker.getPosition();
          edit_lat = new_position.lat();
          edit_lng = new_position.lng();
          // geocode_lookup( 'latLng', new_position,edit_text, edit_map, edit_marker);
          $(txt_lat).val(edit_lat);
          $(txt_lng).val(edit_lng);
      });   
      return edit_marker;
  }

  function map_initialize(lat,lng,drag,elem) {
      var map;
      var marker;
      var myLatlng = new google.maps.LatLng(lat, lng);
      var zoom = 13;
      if(lat == 200 || lng == 200){
          
       myLatlng = new google.maps.LatLng(30.0444,31.2357);   
       zoom = 11;
      }
      
      var myOptions = {
          zoom: zoom,
          center: myLatlng,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
      }
      var id = ''+elem;
      map = new google.maps.Map(document.getElementById(id), myOptions);
      if(lat != 200 && lng != 200){
          marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            draggable: drag
          });
      }
      else{
          marker = new google.maps.Marker({
            map: map,
            draggable: drag
          });
      }
      return {"marker" : marker, "map" : map};
  }


