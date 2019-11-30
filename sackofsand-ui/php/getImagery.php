<?php
$date = $_POST["date"];

$item = array();

if($date=="20-11-2019"){
  $item["filename"] = "S2B_MSIL1C_20191120T110249_N0208_R094_T31UDQ_20191120T112844_water_bodies_small.png";
  $item["xmin"] = 1.6142723681935194;
  $item["ymin"] = 48.65705300757955;
  $item["xmax"] = 3.1351792144248876;
  $item["ymax"] = 49.65272280202541;
}else if($date=="22-11-2019"){
  $item["filename"] = "S2A_MSIL1C_20191122T105351_N0208_R051_T31UDQ_20191122T112943_water_bodies_small.png";
  $item["xmin"] = 1.6142723681935194;
  $item["ymin"] = 48.65705300757955;
  $item["xmax"] = 3.1351792144248876;
  $item["ymax"] = 49.65272280202541;
}else if($date=="25-11-2019"){
  $item["filename"] = "S2A_MSIL1C_20191125T110401_N0208_R094_T31UDQ_20191125T112328_water_bodies_small.png";
  $item["xmin"] = 1.6142723681935194;
  $item["ymin"] = 48.65705300757955;
  $item["xmax"] = 3.1351792144248876;
  $item["ymax"] = 49.65272280202541;
}else if($date=="27-11-2019"){
  $item["filename"] = "S2B_MSIL1C_20191127T105309_N0208_R051_T31UDQ_20191127T113500_water_bodies_small.png";
  $item["xmin"] = 1.6142723681935194;
  $item["ymin"] = 48.65705300757955;
  $item["xmax"] = 3.1351792144248876;
  $item["ymax"] = 49.65272280202541;
}else if($date=="30-11-2019"){
  $item["filename"] = "S2B_MSIL1C_20191130T110319_N0208_R094_T31UDQ_20191130T112606_water_bodies_small.png";
  $item["xmin"] = 1.6142723681935194;
  $item["ymin"] = 48.65705300757955;
  $item["xmax"] = 3.1351792144248876;
  $item["ymax"] = 49.65272280202541;
}

echo json_encode($item);

?>
