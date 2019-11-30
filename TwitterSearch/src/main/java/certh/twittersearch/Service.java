package gr.mklab;


import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;
import java.io.IOException;
import java.net.URI;

public class Service {

	public static String host="";
	public static String port="";
	public static String BASE_URI = "";


	public static HttpServer startServer() {

		final ResourceConfig rc = new ResourceConfig().packages("vbs.auto.query");

		return GrizzlyHttpServerFactory.createHttpServer(URI.create(BASE_URI), rc);
	}


	public static void main(String[] args) {

		try {
			host = "";
			port = "";

			BASE_URI = "http://" + host + ":" + port + "/api/";

			final HttpServer server = startServer();


			System.out.println(String.format("Jersey app started with WADL available at " 
					+ "%sapplication.wadl\nHit enter to stop it...", BASE_URI));

			System.in.read();

			server.shutdown();

		} 
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}


	}

}

