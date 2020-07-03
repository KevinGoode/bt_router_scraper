var duration={};
var hosts=[];
var friendlyNames=[];
var rawData=null;
var graphData=null;
//SIX_MINS_IN_MILLISECS
var SIX_MINS=6*60*1000;
$(function() {

initialiseElements();
initGraphSelected();
initialiseDateTimeBoxes();
initialiseRefreshButton();
refreshGraph();

});
function initialiseElements(){
	// Add the Flot version string to the footer
	$("#footer").prepend("Network Usage v1.1. Flot " + $.plot.version + " &ndash;");
        $("#nicename").val("");
        $("#changename").click(changeName)
}
function changeName(){
    var value = $("#nicename").val();
    $("#nicename").val("");
    var index=$('#graphType').val();
    var host_id=hosts[index].id
    var newname={name:value,id:host_id};
    if (value!=""){
         $.ajax({type: 'POST',url:"setFriendlyNames.php",data:newname,success:gotFriendlyNames});
    }
    setFriendlyName(host_id, value);
    processData(rawData);
    populateDropDown();
    calculateDurations();
    $("#graphType").val(index);
    displaySelectedGraph();
}
function initGraphSelected(){
    $('#graphType').change(displaySelectedGraph);
}
function setDateTimeBoxes(){
        var now=new Date();
        var nowmilli=now.getTime();
        var yesterday = new Date(nowmilli - (1000*24*60*60));

        $('#start-time').datepicker( "setDate", yesterday );
        $('#end-time').datepicker('setDate', now);
}
function initialiseDateTimeBoxes(){
        $('#start-time').datetimepicker();
	$('#end-time').datetimepicker(); 
        $('#start-time').datepicker( "option", "dateFormat", "dd-mm-yy");
        $('#end-time').datepicker( "option", "dateFormat", "dd-mm-yy");

}
function displaySelectedGraph(){
 	var graph =$('#graphType').val();
        displayGraph([graphData[graph]]);
        updateDuration(graphData[graph].duration/1000);                        
}
function updateDuration(secs){
    var mins = secs/60;
    var hours = mins/60;
    if (mins < 1){
       duration = to3dp(secs).toString() + " Seconds";
    } else if(hours < 1){
       duration = to3dp(mins).toString () + " Minutes";
    }else{
       duration = to3dp(hours).toString() + " Hours";
    }   
    $("#duration").val(duration);
}
function to3dp(num){
     return Math.round( num * 1000) / 1000;
}

function refreshGraph(){
      setDateTimeBoxes();
      getFriendlyNames();
}
function initialiseRefreshButton(){
     $("#btn_refresh").on('click',getGraphData);
}
function getFriendlyNames(){
     $.ajax({url:"getFriendlyNames.php",success:gotFriendlyNames});
} 
function getGraphData(){
        
        var startTime=$('#start-time').datepicker('getDate');
        var endTime=$('#end-time').datepicker('getDate');
        var startSecs=startTime.getTime()/1000;
        var endSecs=endTime.getTime()/1000;

        //Format of data expected is as follows:
        //{'data': {'MadeleiesiPhone': '192.168.1.67',  'Windows-Phone': '192.168.1.119'}, 'time': {'utc': '02-10-2016 05:36:03', 'epoch': 1475386563}}
	$.ajax({url:"getHistoricalData.php?&start=" + startSecs + "&end=" + endSecs,success:gotGraphData});


}
function gotFriendlyNames(data){
     var obj = $.parseJSON(data);
     friendlyNames=[];
     for (var j=0;j<obj.data.length;j++){
	friendlyNames.push(obj.data[j]);
     }
     getGraphData();
}
function getFriendlyName(id, defaultName){
     for (var j=0;j<friendlyNames.length;j++){
        if(friendlyNames[j].id==id){
            return friendlyNames[j].name;
        }
     }
     return defaultName;
}
function setFriendlyName(id, name){
     for (var j=0;j<friendlyNames.length;j++){
        if(friendlyNames[j].id==id){
            friendlyNames[j].name=name
            return;
        }
     }
     //If here it must be a new name
      friendlyNames.push({'id':id,'name':name});
}

function gotGraphData(data){
        rawData=data;
        processData(data);
        calculateDurations();
        populateDropDown();
	displaySelectedGraph();
}
function populateDropDown(){
    $('#graphType').children().remove();
    for (var i=0;i<hosts.length;i++){
        var itemval= '<option value="' + i +'">' + hosts[i].name + '</option>';
       $("#graphType").append(itemval);
    }
}
function displayGraph(data){
	$.plot("#placeholder", data, {xaxes: [{mode: "time"}] ,yaxes:[{},{alignTicksWithAxis: 1, position: "right"}]});
}
function calculateDurations(){
  for(var i=0;i<graphData.length;i++){
      graphData[i].duration =0;
      for (var j=0;j<graphData[i].data.length;j++){
            if(j>0){
                if(graphData[i].data[j-1][1] == 1) {
                    var fac =0.5;
                    if(graphData[i].data[j][1] == 1) fac=1.0
                    var delta = graphData[i].data[j][0]- graphData[i].data[j-1][0];
                    graphData[i].duration =  graphData[i].duration + (delta*fac);
                }
            }
      }  
  }
}
function processData(data){
    //SInce there can be alot of time between records (since we only record when there are changes)
    //We need to input fake data to make the step change more realistic
    var obj = $.parseJSON(data);
    //Populate list of known hosts
    getHostsList(obj);
    initGraphData();
    $.each(obj,function(index,item){
        if(item.hasOwnProperty('time') && item.hasOwnProperty('data')){
           var time=item.time;
           var data=item.data;
           var epoch=time['epoch'];
           //Times in graph are in millisecs
           var milli=parseInt(epoch*1000);
           for(var i=0;i<hosts.length;i++){
              var lastIdx =  graphData[i].data.length-1;
              var found = false;
              for (var j=0;j<data.length;j++){
                  if(data[j].id==hosts[i].id){
                      found = true;
                      break;
                  }
              }
              if(found){
                       if(lastIdx>=0 && graphData[i].data[lastIdx][1] == 0){
                          //Just switched so need to fill in gaps between records to make graph square
                          var start_tim=graphData[i].data[lastIdx][0] + SIX_MINS;
                          for(var tim=start_tim + SIX_MINS;tim<milli;tim+=SIX_MINS){
                              graphData[i].data.push([tim,0]);
                          }
                       }
                       graphData[i].data.push([milli,1]);                  
               }else{
                       if(lastIdx>=0 && graphData[i].data[lastIdx][1] == 1){
                          //Just switched so need to fill in gaps between records to make graph square
                          var start_tim=graphData[i].data[lastIdx][0] + SIX_MINS;
                          for(var tim=start_tim;tim<milli;tim+=SIX_MINS){                
                                graphData[i].data.push([tim,1]);
                          }
                       }
                       graphData[i].data.push([milli,0]);
              }//end else
           }//end for hosts
         }//end if          
    });
      
}
function initGraphData(){
   graphData=[];
   for (var i=0;i<hosts.length;i++){
        graphData.push({data:[], label:hosts[i].name, duration:0});    
   }
}
function getHostsList(data){
    hosts=[];
    $.each(data,function(index,item){
       if(item.hasOwnProperty('data')){
          var row=item['data'];
          for (var i=0; i<row.length;i++) {
             if (row[i].hasOwnProperty("name") && row[i].hasOwnProperty("id")) {
                  if(!is_already_in_array(row[i],"id",hosts)) {
                     var niceName=getFriendlyName(row[i]['id'],row[i]['name']);
                     hosts.push({'id':row[i]['id'],'name': niceName});
                  }
             }//end if
          }//end for          
       }//end if        
    });   
}
function is_already_in_array(item,property,list){
  for(var i=0;i<list.length;i++){
     if(list[i][property]==item[property]){
        return true;
     }
  }
  return false;
}
