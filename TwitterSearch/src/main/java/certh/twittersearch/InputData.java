package certh.twittersearch;


public class InputData {


	String access_token;
	String access_token_secret; 
	String consumer_key; 
	String consumer_key_secret; 
	String collectionName;
	String databaseName;
	String databaseHost;
	String databasePort;
	String databaseUsername;
	String databasePassword;
	String databaseAuthenticationMechanism;
	String locationDetectionService;
	
	
	public InputData(){	}
	
	
	public void setLocationDetectionService(String locationDetectionService) { this.locationDetectionService = locationDetectionService; }
	
	public void setAccessToken(String access_token) { this.access_token = access_token; }
	public void setAccessTokenSecret(String access_token_secret) { this.access_token_secret = access_token_secret; }
	public void setConsumerKey(String consumer_key) { this.consumer_key = consumer_key; }
	public void setConsumerKeySecret(String consumer_key_secret) { this.consumer_key_secret = consumer_key_secret; }
	
	public void setDatabaseName(String databaseName) { this.databaseName = databaseName; }
	public void setCollectionName(String collectionName) { this.collectionName = collectionName; }
	public void setDatabaseHost(String databaseHost) { this.databaseHost = databaseHost; }
	public void setDatabasePort(String databasePort) { this.databasePort = databasePort; }
	public void setDatabaseUsername(String databaseUsername) { this.databaseUsername = databaseUsername; }
	public void setDatabasePassword(String databasePassword) { this.databasePassword = databasePassword; }
	public void setDatabaseAuthenticationMechanism(String databaseAuthenticationMechanism) { this.databaseAuthenticationMechanism = databaseAuthenticationMechanism; } 
	
	
	public String getLocationDetectionService() { return locationDetectionService; }
	
	public String getAccessToken() { return access_token; }
	public String getAccessTokenSecret() { return access_token_secret; }
	public String getConsumerKey() { return consumer_key; }
	public String getConsumerKeySecret() { return consumer_key_secret; }
	
	public String getDatabaseName() { return databaseName; }
	public String getCollectionName() { return collectionName; }
	public String getDatabaseHost() { return databaseHost; }
	public String getDatabasePort() { return databasePort; }
	public String getDatabaseUsername() { return databaseUsername; }
	public String getDatabasePassword() { return databasePassword; }
	public String getDatabaseAuthenticationMechanism() { return databaseAuthenticationMechanism; }

}

