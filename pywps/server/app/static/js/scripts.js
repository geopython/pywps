function pywps_pause_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "GET"
	}).done(function(data) {
		console.log("DONE pause " + uuid);

		//data = jQuery.parseJSON(data);

		//console.log(data)

		//if (!data.error) {
			$("#pause-btn-" + uuid).removeClass("display-block");
			$("#resume-btn-" + uuid).addClass("display-block");
		//} 
		/*else{
			alert("Error - " + data.error);
		}*/
	});
}


function pywps_stop_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "POST"
	}).done(function(data) {
	 	console.log("DONE stop " + uuid);

		//data = jQuery.parseJSON(data);

		//console.log(data)

		//if (!data.error) {
			$("#pause-btn-" + uuid).removeClass("display-block");
			$("#resume-btn-" + uuid).removeClass("display-block");
			$("#stop-btn-" + uuid).removeClass("display-block");

			$("#action-btn-" + uuid).html("-");

		//} else{
		//	alert("Error - " + data.error);
		//}
	});
}

function pywps_resume_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "PUT"
	}).done(function(data) {
		console.log("DONE resume " + uuid);

		//data = jQuery.parseJSON(data);

		//console.log(data)

		//if (!data.error) {
			$("#pause-btn-" + uuid).addClass("display-block");
			$("#resume-btn-" + uuid).removeClass("display-block");
		//} 
	});
}