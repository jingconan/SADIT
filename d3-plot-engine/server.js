var io = require('socket.io').listen(3000);

io.sockets.on('connection', function (socket) {

    socket.on('SADIT', function (data) {
        console.log("Got data : " + data.value);
        io.sockets.emit('recv_data', data);
    });
});
