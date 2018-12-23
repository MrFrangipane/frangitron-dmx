$(document).ready(function() {

    namespace = '/frangitron-dmx';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // Update the Ui
    socket.on('update_ui', function(message) {
        // RESET STYLES
        $('input').each(function() {
            $(this).removeClass('active');
        });

        // SELECTED PROGRAM
        var selected_program = $('#' + message.ui_status.selected_program);
        if ( !selected_program.hasClass('active') ) {
            selected_program.addClass('active')
        }
    });

    // Interval function that tests message latency by sending ping
    var ping_pong_times = [];
    var start_time;
    window.setInterval(
        function() {
            start_time = (new Date).getTime();
            socket.emit('ping');
        },
        1000
    );

    // Handler for pong
    socket.on('pong', function() {
        var latency = (new Date).getTime() - start_time;
        ping_pong_times.push(latency);
        ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
        var sum = 0;

        for (var i = 0; i < ping_pong_times.length; i++)
            sum += ping_pong_times[i];

        $('#latency-avg').text(Math.round(10 * sum / ping_pong_times.length) / 10);
        $('#latency').text((10 * latency) / 10);
    });

    // Program clicked
    $('form').submit(function(event) {
        socket.emit(
            'program_clicked',
            {program_name: $(this).find("input")[0].id}
        );

        return false;
    });
});
