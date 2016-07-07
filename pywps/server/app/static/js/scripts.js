function pywps_pause_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "GET"
	}).done(function() {
	  alert("done " + uuid);
	});
}


function pywps_stop_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "POST"
	}).done(function() {
	  alert("done " + uuid);
	});
}

function pywps_resume_process(uuid) {
	$.ajax({
	  url: "/processes/" + uuid,
	  method: "PUT"
	}).done(function() {
	  alert("done " + uuid);
	});
}