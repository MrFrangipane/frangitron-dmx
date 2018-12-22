$(document).ready(function() {

    namespace = '/frangitron-dmx';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('connection', {data: 'I\'m connected!'});
    });

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg) {
        if ( msg.type == 'broadcast' ) {
            // RESET STYLES
            $('form').each(function() {
                $('#' + this.id).removeClass('active');
            });
            // SET SENDER ACTIVE
            if ( !$('#' + msg.data).hasClass('active') ) {
                $('#' + msg.data).addClass('active')
            }
        }
    });

    // Interval function that tests message latency by sending a "ping"
    // message. The server then responds with a "pong" message and the
    // round trip time is measured.
    var ping_pong_times = [];
    var start_time;
    window.setInterval(function() {
        start_time = (new Date).getTime();
        socket.emit('ping');
    }, 1000);

    // Handler for the "pong" message. When the pong is received, the
    // time from the ping is stored, and the average of the last 30
    // samples is average and displayed.
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

    $('form').submit(function(event) {
        if ( this.id == "disconnect" ) {
            socket.emit('disconnect_request');
        }
        else {
            socket.emit('broadcast', {data: this.id});
        }

        return false;
    });
});
