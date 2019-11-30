package gr.mklab;



public class ExtractedLocation {
    
    private final String placeQuery;
    private final String placeName;
    private final double lat;
    private final double lon;
    
    public ExtractedLocation(String placeQuery, String placeName, double lat, double lon){
        this.placeQuery = placeQuery;
        this.placeName = placeName;
        this.lat = lat;
        this.lon = lon;
    }
    
    public String getPlaceQuery(){
        return placeQuery;
    }
    
    public String getPlaceName(){
        return placeName;
    }
    
    public double getLat(){
        return lat;
    }
    
    public double getLon(){
        return lon;
    }
    
}

