function createJSON(c,r) 
{
    json = [];        
    for(i=0;i<r;i++)
        for(j=0;j<c;j++)
        {
            item = {}
            item [r+"_"] = 0;
            json.push(item);            
        }
    return json;
}

function fill(c,r) 
{
    var machines_number=$("#inputX").val();
    var jobs_number=$("#inputY").val(); 
    
    if(machines_number!="" || jobs_number!="")  
    {   
        var tbl=document.getElementById("input_data");
        while(tbl.hasChildNodes())
        {
            tbl.removeChild(tbl.firstChild);
        }
        var header=document.createElement("tr");
        var empty_th=document.createElement("th")
        
        var btn=document.createElement("button")
        btn.innerHTML="Calcular";
        btn.setAttribute("type","button")
        
        btn.addEventListener("click", function(){
        var forGoogle = [];
        var rows = document.getElementById("input_data").getElementsByTagName("tr");
        for(var i = 0; i < rows.length; i++) {
            var array=[]
            var cols=rows[i].getElementsByTagName("td")
            for(var j=0;j<cols.length;j++){
            if(cols[j].innerHTML!="" && cols[j].innerHTML!="0"){
                array.push(cols[j].innerHTML);
            }
            }
            forGoogle.push(array)
    }
    var infos={data:forGoogle};
    $.ajax({
        dataType: 'json',
        type:'post',
        url: "http://127.0.0.1:5000/simul",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(infos),
        success: function(resp){
        var time=resp["time"]
            var xy=resp["data"]
            chart_data=[]
            for(l=0;l<xy.length;l++) {
            for(n=0;n<xy[l].length;n++)
            {
                if(parseInt(xy[l][n][3],10)!=0)
                { 
                var element=[]
            var dt=new Date(0,0,0,0,0,0)
            
            var labJob=+xy[l][n][0]+ +1 -1
            element.push("Trabalho "+ labJob)
            
            var indmach=xy[l][n][1].replace("Mach","")
            var labmach=+indmach+ +1 -1
                element.push("M" + "(" + labJob + "," + labmach + ")");
                
                var dt1=new Date(0,0,0,0,0,0)                  
                var start=dt1.getSeconds() + parseInt(xy[l][n][2],10);
                dt1.setSeconds(start)
                element.push(dt1);
                
                var dt2=new Date(0,0,0,0,0,0)
                var end=parseInt(xy[l][n][3],10);
                dt2.setSeconds(start+end)
                element.push(dt2);
                chart_data.push(element);
            }
            }
            }
                $("#opt_time").html(time)
                drawChart(chart_data)}});});
        empty_th.appendChild(btn);
        header.appendChild(empty_th);
        for(i=0;i<machines_number;i++)
        {
            var aux=document.createElement("th");
            aux.setAttribute("scope","col");
            var k=i;
            aux.innerHTML="Máquina "+k;
            header.appendChild(aux);
        }            
        tbl.appendChild(header);
        for(i=0;i<jobs_number;i++)
        {
            var tr=document.createElement("tr");
            var th=document.createElement("th");
            th.setAttribute("scope","row");
            var k=i;
            th.innerHTML="Trabalho "+k;
            tr.appendChild(th);
            for(j=0;j<machines_number;j++)
            {
                var td=document.createElement("td");
                tr.appendChild(td);
            }
            tbl.appendChild(tr);
        }
        $('#input_data').find('td').each(function(){
        $(this).click(function() {
            $('table td').not($(this)).prop('contenteditable', false);
            $(this).prop('contenteditable', true);
        });
        $(this).blur(function() {
            $(this).prop('contenteditable', false);});});}
}     

google.charts.load("current", {packages:["timeline"]});
            google.charts.setOnLoadCallback(drawChart);
  function drawChart(datt) {
    var ccc=[]
    if(datt!=null)
    ccc=datt
var chartwidth = $('#chart').width;
    var container = document.getElementById('chart');
    var chart = new google.visualization.Timeline(container);
    var dataTable = new google.visualization.DataTable();    
    dataTable.addColumn({ type: 'string', id: 'Tabela' });
    dataTable.addColumn({ type: 'string', id: 'Nome' });
    dataTable.addColumn({ type: 'date', id: 'Inicio' });
    dataTable.addColumn({ type: 'date', id: 'Fim' });
    dataTable.addRows(ccc);

    var options = {
     width: chartwidth,
      timeline: { colorByRowLabel: false}
    };
    google.visualization.events.addListener(chart, 'onmouseover', function (obj) {

var startDate = dataTable.getValue(obj.row, 2);
var endDate   = dataTable.getValue(obj.row, 3);
var seconds = (startDate.getTime() - new Date(0,0,0,0,0,0).getTime()) / 1000;
var timeDiff = Math.abs(startDate.getTime() - endDate.getTime());
var diffDays = (timeDiff / (1000 * 3600 * 24)); 
var ed=+seconds+ +timeDiff/1000
    var ht="<table width='100%'><tr><th scope='row'>Inicio</th><td>"+seconds+
            "</td></tr><tr><th scope='row'>Fim</th><td>"+ed+
            "</td></tr><tr><th scope='row'>Duração</th><td>"+timeDiff/1000+
            "</td></tr></table>"

$(".google-visualization-tooltip").html(ht);
});

    chart.draw(dataTable, options);
}
