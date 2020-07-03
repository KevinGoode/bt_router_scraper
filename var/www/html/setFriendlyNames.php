<?php
    $config= file_get_contents("/etc/bt_router_scraper/conf.json");
    $data = json_decode($config, true);
    $file_name = $data['friendly_names']; 
    $name = $_POST['name'];
    $id = $_POST['id'];
    $contents = file_get_contents($file_name);
    $json = json_decode($contents);
    $found = false;

    foreach($json->data as $item){
       if(strcmp($item->id, $id)==0){
           $item->name=$name;
           $found = true;
           break;
       }
    }
   if (!$found){
      $new_item = (object) array('id' => $id, 'name' => $name);
      array_push($json->data,$new_item);
   }
   $outputJson=json_encode($json);
   $fp = fopen($file_name, 'w');
   $output=json_encode($json);
   fwrite($fp, $output);
   fclose($fp);

  
?>

