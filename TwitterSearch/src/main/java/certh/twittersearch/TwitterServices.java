package certh.twittersearch;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Response;



import javax.ws.rs.core.MediaType;


import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

import javax.ws.rs.QueryParam;

import com.google.gson.Gson;
import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.MongoClient;
import com.mongodb.util.JSON;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.ArrayList;
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

import certh.twittersearch.TwitterPipeline;



@Path("hackathon")
public class TwitterServices {





	@GET @Path("twitterService")
	@Produces(MediaType.APPLICATION_JSON)
	public Response twitterSearch(@QueryParam("query") String userQuery) {

		String result = null;


		TwitterPipeline tp = new TwitterPipeline();
		String res = tp.twitterPipeline(userQuery);

		Gson gson = new Gson();
		return Response.status(200).entity(gson.toJson(res))
				.header("Access-Control-Allow-Origin", "*").build();

	}







	
}
