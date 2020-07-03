<?php
    
    function modify_last($last, $time){
        $last->{'time'}->{'epoch'}=$time;
        $last->{'time'}->{'utc'}=gmdate("d-m-Y H:i:s", $time);
    }
    function add_last($last, &$results, $end){
         //Because history only contains
         //records when state has changed we need to  do some extrapolation
         //IE We know record for current time is the same as the last one stored so
        //If end time is bigger than lasttime just modify time of last record to be now
        if($last != null){
            $last_epoch = (int) $last->time->epoch;
            if($end > $last_epoch)
            {
                $epoch=time();
                $utc=gmdate("d-m-Y H:i:s", $epoch);
                $clone = clone $last;
                $clone->time= (object) array('epoch' => $epoch, 'utc' => $utc);
                array_push($results,$clone);
            }
        }
    }
    function add_previous($last, &$results, $time){
         //Because history only contains
         //records when state has changed we need to  do some extrapolation
         //IE We know start record is equal to previous
         //We also know last record is same as the last one stored so can just modify time of last record
         if($last != null){
            modify_last($last,$time);
            array_push($results,$last);
         }
    }
    $start=(int) $_GET["start"];
    $end=(int) $_GET["end"];
    $results = array();
    $last = null;
    $previous = false;

    $config= file_get_contents("/etc/bt_router_scraper/conf.json");
    $data = json_decode($config, true);
    $file_name = $data['state_file'];
    $lines = file($file_name);
    // Loop through each line. Converting to json, check value in range then add to output json
    foreach ($lines as  $line) {
        $json = json_decode($line);
        $reading=$json->{'data'};
        $time=$json->{'time'};
        $epoch=(int) $time->{'epoch'};
        if(($epoch >= $start) && ($epoch <= $end)){
           if($previous == false){
               $previous=true;
               add_previous($last,$results,$start);
           }
           array_push($results,$json);
         }
        $last=$json;
    }
    //Modify time of last record 
    add_last($last,$results,$end);
    $outputJson=json_encode($results);
    echo $outputJson;
?>

