<?php
    $config= file_get_contents("/etc/bt_router_scraper/conf.json");
    $data = json_decode($config, true);
    $file_name = $data['friendly_names']; 
    $contents = file_get_contents($file_name);
    echo $contents;
?>
