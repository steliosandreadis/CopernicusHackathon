var map, lyr, mil;

$(function() {

  $("select#select-date").horizontalSelector();

  var preselectedDate = $("select#select-date").children("option:selected"). val();
  searchTweets(preselectedDate);
  searchImagery(preselectedDate);

  $("select#select-date").change(function(){
    var selectedDate = $(this). children("option:selected"). val();
    searchTweets(selectedDate);
    searchImagery(selectedDate);
  });

});

function searchTweets(date){

  runningRequest = $.ajax({
    type: "POST",
    url : "php/findTweets.php",
    data: {"date" : date},
    dataType: "JSON",
    success : function (data) {
      addTweetsToMap(data);
    }
  });

}

function addTweetsToMap(data){

  var markers = [];

  $.each(data.items, function(index, element) {
    var date = new Date(element.creationDate);
    var creationDate = date.format("ddd, dd mmm yyyy HH:MM");
    if(element.estimated_locations!="n/a"){
      $.each(element.estimated_locations, function(index, estimated_location) {
        markers.push({"id":element.id, "text":urlify(element.title), "image":element.image_url, "date":creationDate, "lat":""+estimated_location.geometry.coordinates[1], "lng":""+estimated_location.geometry.coordinates[0]});
      });
    }
  });

  require(
  [
    "dojo/_base/array",

    "esri/Color",
    "esri/map",
    "esri/symbols/SimpleMarkerSymbol",
    "esri/symbols/SimpleLineSymbol",
    "esri/renderers/ClassBreaksRenderer",
    "esri/SpatialReference",
    "esri/dijit/PopupTemplate",
    "esri/geometry/Point",
    "esri/geometry/webMercatorUtils",

    "extras/ClusterLayer",

    "dijit/layout/BorderContainer",
    "dijit/layout/ContentPane",

    "dojo/domReady!"
  ],
  function(arrayUtils, Color, Map, SimpleMarkerSymbol, SimpleLineSymbol, ClassBreaksRenderer, SpatialReference, PopupTemplate, Point, webMercatorUtils, ClusterLayer){

    if(map==undefined){
      map = new Map("the-map", {
          basemap: "satellite",
          center: [13.63, 47.35], // longitude, latitude
          zoom: 4
      });
      map.on("load", function() {
        addClusters(markers);
      });
    }else{
      if(map.loaded){
        if(lyr!=undefined){
          map.removeLayer(lyr);
        }
        addClusters(markers);
      }else{
        map.on("load", function() {
          addClusters(markers);
        });
      }
    }

    function addClusters(markers) {

      var wgs = new SpatialReference({
        "wkid": 4326
      });

      var data = arrayUtils.map(markers, function(item) {
        var latlng = new  Point(parseFloat(item.lng), parseFloat(item.lat), wgs);
        var webMercator = webMercatorUtils.geographicToWebMercator(latlng);
        var attributes = {
          "id": item.id,
          "text": item.text,
          "image": item.image,
          "date": item.date
        };
        return {
          "x": webMercator.x,
          "y": webMercator.y,
          "attributes": attributes
        };
      });

      var pTemplate = new PopupTemplate({
        description: "<img src='{image}'><br>{text}<br><br>{date}" //html
      });

      lyr = new ClusterLayer({
        "data": data,
        "distance": 20,
        "id": "tweetsLayer",
        "labelColor": "#000",
        "labelOffset": -5,
        "resolution": map.extent.getWidth() / map.width,
        "singleColor": "#000",
        "singleTemplate": pTemplate
      });

      var defaultSym = new SimpleMarkerSymbol();
      var renderer = new ClassBreaksRenderer(defaultSym, "clusterCount");

      var small = new SimpleMarkerSymbol();
      small.style = SimpleMarkerSymbol.STYLE_CIRCLE;
      small.setSize(20);
      small.setColor(new Color([28,221,40]));
      small.setOutline(new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID,new Color([0,0,0]),1));

      var medium = new SimpleMarkerSymbol();
      medium.style = SimpleMarkerSymbol.STYLE_CIRCLE;
      medium.setSize(30);
      medium.setColor(new Color([28,221,40]));
      medium.setOutline(new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID,new Color([0,0,0]),1));

      var large = new SimpleMarkerSymbol();
      large.style = SimpleMarkerSymbol.STYLE_CIRCLE;
      large.setSize(40);
      large.setColor(new Color([28,221,40]));
      large.setOutline(new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID,new Color([0,0,0]),1));

      renderer.addBreak(0, 1, small);
      renderer.addBreak(1, 50, medium);
      renderer.addBreak(50, 1000, large);

      lyr.setRenderer(renderer);

      map.addLayer(lyr);

      map.on("click", cleanUp);

    }



    function cleanUp() {
      map.infoWindow.hide();
      lyr.clearSingles();
    }

  }
);

}

function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url + '" target="_blank">' + url + '</a>';
    })
}

function searchImagery(date){

  runningRequest = $.ajax({
    type: "POST",
    url : "php/getImagery.php",
    data: {"date" : date},
    dataType: "JSON",
    success : function (data) {
      addImageryToMap(data);
    }
  });

}

function addImageryToMap(data){

  require(["esri/map", "esri/layers/MapImageLayer", "esri/layers/MapImage"],
  function(Map, MapImageLayer, MapImage) {

    if(map==undefined){
      map = new Map("the-map", {
          basemap: "satellite",
          center: [2.35, 48.86], // longitude, latitude
          zoom: 8
      });
      map.on("load", function() {
        addImageLayer();
      });
    }else{
      if(map.loaded){
        if(mil!=undefined){
          map.removeLayer(mil);
        }
        addImageLayer();
      }else{
        map.on("load", function() {
          addImageLayer();
        });
      }
    }

    function addImageLayer(){
      mil = new esri.layers.MapImageLayer();
      map.addLayer(mil);
      var mi = new esri.layers.MapImage({
        'extent': { 'xmin': data.xmin, 'ymin': data.ymin, 'xmax': data.xmax, 'ymax': data.ymax },
        'href': 'data/' + data.filename
      });
      mil.addImage(mi);
    }

  });
}
