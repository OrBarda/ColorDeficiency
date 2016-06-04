$(function() {
    $( "#sortable" ).sortable();
    $( "#sortable" ).disableSelection();
  });

function done() {
    $("#sortable").hide();
    $("#label").html("<p align='center'><b> You have <u> Protan </u> color deficiency! </p><p align='center'> Please go back to the main window and select Protan deficiency. </b></p>");
    $("#clear").hide();
}