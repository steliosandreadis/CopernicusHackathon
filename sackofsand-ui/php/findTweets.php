<?php
include('tweetUtils.php');

ini_set('mongo.long_as_object', 1);
ini_set('max_execution_time', 300);
MongoCursor::$timeout = -1;

$results = array();

$username = "hackathon";
$password = "RpoJ*Ct";

$con = new MongoClient("mongodb://localhost:27017", array("username" => $username, "password" => $password));
$database = "hackathon";
$db = $con->$database;

$table = "EnglishSnow";
$collection = $db->$table;

$date = $_POST["date"];
$from = $date." 00:00";
$to = $date." 23:59";

$filters = array();
array_push($filters, array('nudity' => false));
array_push($filters, array('timestamp_ms' => array( '$gte' => (strtotime($from) * 1000)."", '$lte' => (strtotime($to) * 1000)."" )));

$documents = $collection->find(array('$and' => $filters))->sort(array("id" => -1));

$items = array();
foreach($documents as $document){
  $item = array();
  $item["id"] = $document["id_str"];
  $item["title"] = getTweetText($document);
  $item["creationDate"] = $document["created_at"];
  $item["image_url"] = getImageURL($document);
  $item["estimated_locations"] = ( isset($document["estimated_locations"]) ? $document["estimated_locations"] : "n/a");

  array_push($items, $item);
}

$results["items"] = $items;

echo json_encode($results);

?>
