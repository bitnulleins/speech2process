//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						// stream from getUserMedia()
var recorder; 						// WebAudioRecorder object
var input; 							// MediaStreamAudioSourceNode  we'll be recording
var encodingType; 					// holds selected encoding for resulting audio (file)
var encodeAfterRecord = true;       // when to encode
var stepcounter	= 1;				// step counter

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record

var encodingTypeSelect = document.getElementById("encodingTypeSelect");
var bpmnDiv = document.getElementById("bpmn");
var eventLogDiv = document.getElementById("eventlog");
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var generateButton = document.getElementById("generateButton")

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
generateButton.addEventListener("click", generateProcess);

// Global data container for session
var data = new FormData()

function uuidv4() {
	return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
	  (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
	);
  }


function generateProcess() {
	// Query parameter for endpoint
	data.set('body_request_type','audio')

	fetch('/process/create', {
		method: 'POST',
		body: data
	})
	.then(response => response.json())
	.then(json => {
		console.log(json)

		// Preview image
		bpmnDiv.innerHTML = '<img src="./static/assets/images/process.png?id='+uuidv4()+'" />';
		bpmnDiv.innerHTML += '<a target="_blank" href="./static/assets/bpmn/process.bpmn">Download BPMN</a>';

		// Preview Eventlog
		eventLogDiv.innerHTML = json['activity_log_html']
		eventLogDiv.innerHTML += '<a target="_blank" href="./static/assets/bpmn/process.xes">Download XES Log</a>';
	}).catch((error) => {
		console.error(error)
	})
}

function startRecording() {
	console.log("STEP" + stepcounter + " StartRecording...");

	/*
		Simple constraints object, for more advanced features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
		audioContext = new AudioContext();

		//update the format 
		document.getElementById("formats").innerHTML="Format: 2 channel "+encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value+" @ "+audioContext.sampleRate/1000+"kHz"

		//assign to gumStream for later use
		gumStream = stream;
		
		// use the stream
		input = audioContext.createMediaStreamSource(stream);
		
		//stop the input from playing back through the speakers
		//input.connect(audioContext.destination)

		//get the encoding 
		encodingType = encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value;
		
		//disable the encoding selector
		encodingTypeSelect.disabled = true;

		recorder = new WebAudioRecorder(input, {
		  workerDir: "static/js/", // must end with slash
		  encoding: encodingType,
		  numChannels:2, //2 is the default, mp3 encoding supports only 2
		  onEncoderLoading: function(recorder, encoding) {
		    // show "loading encoder..." display
		    console.log("STEP" + stepcounter + " Loading "+encoding+" encoder...");
		  },
		  onEncoderLoaded: function(recorder, encoding) {
		    // hide "loading encoder..." display
		    console.log("STEP" + stepcounter + " " + encoding+" encoder loaded");
		  }
		});

		recorder.onComplete = function(recorder, blob) { 
			console.log("STEP" + stepcounter + " Encoding complete");

			createStep(blob,recorder.encoding);

			// Append to global file list for later request
			data.append('file', blob , 'step'+stepcounter)

			stepcounter++;
			generateButton.disabled = false
			encodingTypeSelect.disabled = false;
		}

		recorder.setOptions({
		  timeLimit:120,
		  encodeAfterRecord:encodeAfterRecord,
	      ogg: {quality: 0.5},
	      mp3: {bitRate: 160}
	    });

		//start the recording process
		recorder.startRecording();

		 console.log("STEP" + stepcounter + "Recording started");

	}).catch(function(err) {
		console.log(err)
	  	//enable the record button if getUSerMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;

	});

	//disable the record button
    recordButton.disabled = true;
    stopButton.disabled = false;
}

function stopRecording() {	
	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//disable the stop button
	stopButton.disabled = true;
	recordButton.disabled = false;
	
	//tell the recorder to finish the recording (stop recording + encode the recorded audio)
	recorder.finishRecording();

	console.log('STEP' + stepcounter + ' Recording stopped');
}

function createStep(blob,encoding) {
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var text = document.createElement('span');

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;

	text.textContent = "Step " + stepcounter + ":"

	//add the new audio and a elements to the li element
	li.appendChild(text);
	li.appendChild(au);

	//add the li element to the ordered list
	recordingsList.appendChild(li);

	return url;
}