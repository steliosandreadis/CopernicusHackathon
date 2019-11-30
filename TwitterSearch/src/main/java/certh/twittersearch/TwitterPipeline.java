package gr.mklab;




import javax.ws.rs.core.MediaType;


import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;

import javax.ws.rs.QueryParam;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonSyntaxException;
import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.MongoClientURI;
import com.mongodb.MongoCredential;
import com.mongodb.ServerAddress;
import com.mongodb.util.JSON;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.net.UnknownHostException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;
import twitter4j.GeoLocation;
import twitter4j.Query;
import twitter4j.Query.Unit;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;
import twitter4j.json.DataObjectFactory;



public class TwitterPipeline {

	MongoDatabase db = null;
	MongoClient mongoClient = null;

	ConfigurationBuilder cb = new ConfigurationBuilder();
	Twitter twitter;
	ArrayList<Status> tweets, records;
	int count;



	public static String access_token;
	public static String access_token_secret; 
	public static String consumer_key; 
	public static String consumer_key_secret; 
	public static String dbName;
	public static String dbCollectionName;
	public static String dbHost;
	public static String dbPort;
	public static String dbUsername;
	public static String dbPassword;
	public static String dbAuthMech;
	public static String locationDetectionService;



	TwitterPipeline() {

		InputData inputD = loadTextFileWithInputParameters("parametersMongoTwitter.txt");

		locationDetectionService = inputD.getLocationDetectionService();

		access_token = inputD.getAccessToken();
		access_token_secret = inputD.getAccessTokenSecret();
		consumer_key = inputD.getConsumerKey();
		consumer_key_secret = inputD.getConsumerKeySecret();

		dbName = inputD.getDatabaseName();
		dbCollectionName = inputD.getCollectionName();
		dbHost = inputD.getDatabaseHost();
		dbPort = inputD.getDatabasePort();
		dbUsername = inputD.getDatabaseUsername();
		dbPassword = inputD.getDatabasePassword();
		dbAuthMech = inputD.getDatabaseAuthenticationMechanism();


		cb.setJSONStoreEnabled(true);
		cb.setDebugEnabled(true).setOAuthConsumerKey(consumer_key)
		.setOAuthConsumerSecret(consumer_key_secret)
		.setOAuthAccessToken(access_token)
		.setOAuthAccessTokenSecret(access_token_secret);
		twitter = new TwitterFactory(cb.build()).getInstance();
		tweets = new ArrayList<>();
		records = new ArrayList<>();
	}


	public String twitterPipeline(String inputQuery) {



		// Getting dates
		DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");

		Date date = new Date();
		String todate = dateFormat.format(date);

		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DATE, -8);
		Date todate1 = cal.getTime();    
		String fromdate = dateFormat.format(todate1);

		System.out.println(todate);
		System.out.println(fromdate);

System.out.println(access_token);

		// Variables
		//int numberOfTweets = 1000000;
		//int queryCount = 100;
		int numberOfTweets = 110;
		int queryCount = 10;
		int count;



		// Getting tweets
		Query query = new Query(inputQuery);
		
		String since = fromdate;
		query.since(since.substring(0, since.indexOf("T"))); //limited to 6-9 days ago
		String until = todate;
		query.until(until.substring(0, until.indexOf("T")));


		
		long lastID = Long.MAX_VALUE;

		while (tweets.size() < numberOfTweets) {
			if (numberOfTweets - tweets.size() > 100)
				count = queryCount;
			else
				count = numberOfTweets - tweets.size();
			//System.out.println("numberOfTweets="+numberOfTweets+" tweets.size()=" + tweets.size()+" count="+count);
			query.setCount(count);
			try {
				QueryResult result = twitter.search(query);
				System.out.println("Gathered " + result.getTweets().size() + " tweets");
				tweets.addAll(result.getTweets());
				for (Status t : tweets) {
					if (t.getId() < lastID)
						lastID = t.getId();
				}
				records.addAll(result.getTweets());
				writeTweets();
			}catch (TwitterException te) {
				System.out.println("Rate limit exhausted");
				try {
					java.util.concurrent.TimeUnit.MINUTES.sleep(15);
				} catch (InterruptedException ex) {}
			}
			query.setMaxId(lastID - 1);
		}
		 
		
		return "success";


	}


	public void writeTweets() {

		MongoDatabase db = connectToDB(dbHost, dbPort, dbName, dbUsername, dbPassword, dbAuthMech);
		MongoCollection coll = db.getCollection(dbCollectionName);

		for (Status tweet : records) {
			String json = DataObjectFactory.getRawJSON(tweet);
			BasicDBObject res = (BasicDBObject) JSON.parse(json);
			
			
			//Location Detection
			String id = res.get("id_str").toString();
			ArrayList<ExtractedLocation> locations = getLocation(res.getString(tweetText), id);
			JsonArray estimatedLocations = new JsonArray();
			for(ExtractedLocation location : locations){
				if(location.getLat()!= 91 && location.getLon()!= 181){
					JsonObject locationObj = new JsonObject();
					locationObj.addProperty("location_in_text",location.getPlaceQuery());
					locationObj.addProperty("location_fullname",location.getPlaceName());
					JsonObject geometry = new JsonObject();
					geometry.addProperty("type", "Point");
					JsonArray coordinates = new JsonArray();
					coordinates.add(location.getLon());
					coordinates.add(location.getLat());
					geometry.add("coordinates", coordinates);
					locationObj.add("geometry",geometry);
					estimatedLocations.add(locationObj);
				}
			}

			if(estimatedLocations.size()>0){
				res.append("estimated_locations", estimatedLocations);
			}
			 
			
			coll.insertOne(res);
		}

		mongoClient.close();

		//System.out.println("Inserted " + records.size() + " tweets");
		records.clear();

	}


	public static ArrayList<ExtractedLocation> getLocation(String text, String id){

		ArrayList<ExtractedLocation> locations = new ArrayList<>();
		String placeQuery = "", placeName = "";
		double lat = 91, lon = 181; //invalid values

		try {

			URL url = new URL(locationDetectionService+"tweet="+URLEncoder.encode(text,"UTF-8").replace("+", "%20")+"&tweetId="+id);
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept", "application/json");
			if (conn.getResponseCode() == 200) {
				BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
				try{
					String output = br.readLine();
					if(!output.equals("null")){
						JsonObject obj = new JsonParser().parse(output).getAsJsonObject();
						if(obj.has("finalLocations")){
							JsonArray finalLocations = obj.get("finalLocations").getAsJsonArray();
							for(JsonElement finalLocation : finalLocations){
								JsonObject location = finalLocation.getAsJsonObject();
								if(location.has("placequery")){
									placeQuery = location.get("placequery").getAsString();
								}
								if(location.has("placename")){
									placeName = location.get("placename").getAsString();
								}
								if(location.has("coords.lat")){
									lat = Double.parseDouble(location.get("coords.lat").getAsString());
								}
								if(location.has("coords.lon")){
									lon = Double.parseDouble(location.get("coords.lon").getAsString());
								}
								locations.add(new ExtractedLocation(placeQuery, placeName, lat, lon));
							}
						}
					}
				} catch (JsonSyntaxException | IOException e){
					System.out.println("Error on location detection: " + e);
				}
			}

			conn.disconnect();

		}catch (IOException e) {
			System.out.println("Error on location detection: " + e);
		}

		return locations;

	}




	public MongoDatabase connectToDB(String host, String port, String databaseName, String mongoUsername, String mongoPassword, String authenticationUserMechamism){

		if(authenticationUserMechamism == null){
			mongoClient = new MongoClient(new MongoClientURI(host != null ? "mongodb://" + host + ':' + port : "mongodb://localhost:27017"));
		}
		else {

			if(authenticationUserMechamism.equalsIgnoreCase("MONGODB-CR")){
				MongoCredential credential1 = MongoCredential.createMongoCRCredential(mongoUsername, databaseName, mongoPassword.toCharArray());
				mongoClient = new MongoClient(new ServerAddress(host + ":" + port), Arrays.asList(credential1));
			}

			if(authenticationUserMechamism.equalsIgnoreCase("SCRAM-SHA-1")){
				MongoCredential credential2 = MongoCredential.createScramSha1Credential(mongoUsername, databaseName, mongoPassword.toCharArray());
				mongoClient = new MongoClient(new ServerAddress(host + ":" + port), Arrays.asList(credential2));
			}
		}

		db = mongoClient.getDatabase(databaseName);

		return db;
	}


	private InputData loadTextFileWithInputParameters(String inputFile){

		String thisLine = "";
		InputData id = new InputData();

		FileReader fr;
		try {
			fr = new FileReader(inputFile);
			BufferedReader br = new BufferedReader(fr);

			while ( (thisLine = br.readLine())!=null) {
				String data = thisLine.substring(thisLine.indexOf("=") + 1).trim();			

				if(thisLine.startsWith("locationDetectionService")) { id.setLocationDetectionService(data); }

				if(thisLine.startsWith("access_token")) { id.setAccessToken(data); }
				if(thisLine.startsWith("access_token_secret")) { id.setAccessTokenSecret(data); }

				if(thisLine.startsWith("consumer_key")) { id.setConsumerKey(data); }
				if(thisLine.startsWith("consumer_key_secret")) { id.setConsumerKeySecret(data); }

				if(thisLine.startsWith("databaseName")) { id.setDatabaseName(data); }
				if(thisLine.startsWith("databaseCollection")) { id.setCollectionName(data); }

				if(thisLine.startsWith("databaseHost")) { id.setDatabaseHost(data); }
				if(thisLine.startsWith("databasePort")) { id.setDatabasePort(data); }
				if(thisLine.startsWith("databaseUsername")) { id.setDatabaseUsername(data); }
				if(thisLine.startsWith("databasePassword")) { id.setDatabasePassword(data); }
				if(thisLine.startsWith("databaseAuthenticationMechanism")) { id.setDatabaseAuthenticationMechanism(data); }
			}

			br.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}


		return id;
	}


	public ArrayList<String> readFile(String filename) {
		String thisLine = "";
		ArrayList<String> wholeFile = new ArrayList<String>();

		FileReader fr = null;
		BufferedReader br = null;
		try{
			fr = new FileReader(filename);
			br = new BufferedReader(fr);

			while ( (thisLine = br.readLine())!=null) {
				wholeFile.add(thisLine);
			}

			br.close();
		}catch(IOException io){
			System.out.println("Exception in 'readFile' function" + io.toString());
		}	

		return wholeFile;
	}

	public static void main(String[] args){

		TwitterPipeline tp = new TwitterPipeline();
		tp.twitterPipeline("flood Venice");

	}

}