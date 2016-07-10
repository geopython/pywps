function pywps_pause_process(uuid) {
	
	var xhr = $.ajax( {
	  url: "/processes/" + uuid,
	  method: "POST",

	} );

	xhr.done( function (data) {
		console.log("DONE pause " + uuid);

		if (!data.error) {
			$("#pause-btn-" + uuid).removeClass("display-block");
			$("#resume-btn-" + uuid).addClass("display-block");

			$("#status-text-" + uuid).html("Paused");

		} else{
			alert("Error - " + data.error);

		}

	} );

	xhr.fail( function () {
		alert("error");

	} );

}


function pywps_stop_process(uuid) {
	var xhr = $.ajax( {
	  url: "/processes/" + uuid,
	  method: "POST"

	} ); 

	xhr.done( function( data ) {
	 	console.log("DONE stop " + uuid);

		if (!data.error) {
			$("#pause-btn-" + uuid).removeClass("display-block");
			$("#resume-btn-" + uuid).removeClass("display-block");
			$("#stop-btn-" + uuid).removeClass("display-block");

			$("#action-btn-" + uuid).html("-");

			$("#status-text-" + uuid).html("Stopped");

		} else{
			alert("Error - " + data.error);

		}

	} ); 

	xhr.fail( function () {
		alert("error");

	} );

}

function pywps_resume_process(uuid) {
	var xhr = $.ajax( {
	  url: "/processes/" + uuid,
	  method: "PUT"

	} );

	xhr.done(function (data) {
		console.log("DONE resume " + uuid);

		if (!data.error) {
			$("#pause-btn-" + uuid).addClass("display-block");
			$("#resume-btn-" + uuid).removeClass("display-block");

			$("#status-text-" + uuid).html("Running");

		} else {
			alert("Error - " + data.error);

		}

	} );

	xhr.fail( function() {
		alert("error");
	} );

}

function pywps_refresh_processes_table () {
	var xhr = $.ajax( {
	  url: "/processes/table-entries",
	  method: "POST"

	} );

	xhr.done(function (data) {
		console.log("DONE processes_table");

		$('#processes_table').html(data);

	} );

	xhr.fail( function() {
		console.log("Error - processes table refresh");
	} );
}

//setTimeout(pywps_refresh_processes_table, 2000);

window.setInterval(pywps_refresh_processes_table, 5000);
