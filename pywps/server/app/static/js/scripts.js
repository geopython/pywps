function pywps_pause_process(uuid) {
	$.ajax({
	  url: "/processes/pokus",
	  method: "GET"
	}).done(function() {
	  alert("done " + uuid);
	});
}


function pywps_stop_process(uuid) {
	$.ajax({
	  url: "/processes/pokus",
	  method: "POST"
	}).done(function() {
	  alert("done " + uuid);
	});
}

function pywps_resume_process(uuid) {
	$.ajax({
	  url: "/processes/pokus",
	  method: "PUT"
	}).done(function() {
	  alert("done " + uuid);
	});
}