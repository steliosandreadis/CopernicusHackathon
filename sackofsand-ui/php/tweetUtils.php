<?php

function getTweetText($document){
  if( isset($document["retweeted_status"]) ){
    $retweeted_status = $document["retweeted_status"];
    if( isset($retweeted_status["extended_tweet"]) ){
      $extended_tweet = $retweeted_status["extended_tweet"];
      return $extended_tweet["full_text"];
    }else{
      return $retweeted_status["text"];
    }
  }else if( isset($document["extended_tweet"]) ){
    $extended_tweet = $document["extended_tweet"];
    return $extended_tweet["full_text"];
  }else{
    return $document["text"];
  }
}

function getImageURL($document){
  if( isset($document["extended_tweet"]) ){

    $extended_tweets = $document["extended_tweet"];
    $entities = $extended_tweets["entities"];
    if( isset($entities["media"]) ){
      $media = $entities["media"];
      if( sizeof($media) > 0 ){

        $image = $media[0];
        return ( isset($image["media_url_https"]) ? $image["media_url_https"] : "");
      }
    }
  }else if( isset($document["entities"]) ){

    $entities = $document["entities"];
    if( isset($entities["media"]) ){
      $media = $entities["media"];
      if( sizeof($media) > 0 ){
        $image = $media[0];
        return ( isset($image["media_url_https"]) ? $image["media_url_https"] : "");

      }
    }
  }
  return "";
}

?>
