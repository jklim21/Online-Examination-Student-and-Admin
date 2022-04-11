$(document).ready(function() {
    // timer function
    function startTimer(duration, display, session_id) {
        var timer = duration, hours, minutes, seconds;

        var refresh = setInterval(function () {
            hours = parseInt(timer / 3600, 10)
            minutes = parseInt((timer % 3600) / 60, 10)
            seconds = parseInt(timer % 60, 10);
            
            hours = hours < 10 ? "0" + hours : hours;
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            var output = hours + " : " + minutes + " : " + seconds;
            display.text(output);
            //$("title").html(output + " - TimerTimer");

            if (--timer < 0) {
                display.text("Time's Up!");
                clearInterval(refresh);  // exit refresh loop
                var music = $("#over_music")[0];
                music.play();
                //alert("Time's Up!");
                //window.location.href = "http://127.0.0.1:5000/script";   // METHOD 1
                //window.location.href = "http://localhost:5000/script";      // METHOD 2

                // THIS WAS USED TO TEST FORCE DIRECT TO PENDING PAGE FROM THE EXAM PAGE
                //window.location.href = 'http://localhost:5000/student/pending/' + session_id; 

                window.location.href = "http://localhost:5000/student/upload_page";
            }
        }, 1000);
    }

    // start timer
    jQuery(function ($) {
        var display = $('#time');
        startTimer(Seconds, display, session_id);
    });
})