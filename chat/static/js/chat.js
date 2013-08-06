$(function() {
    "use strict";

    var content = $('#content');
    var input = $('#input');
    var status = $('#status');

    var myColor = false;
    var myName = false;

    var socket = io.connect('/chat');
    
    socket.on('connect', function () {
        input.removeAttr('disabled');
        status.text('Choose name:');
    });

    socket.on('disconnect', function () {
        status.text('Error');
        input.attr('disabled', 'disabled').val('Unable to communicate');
    });
    

    socket.on('message', function (message) {
        try {
            var json = JSON.parse(message);
        } catch (e) {
            console.log('This doesn\'t look like a valid JSON: ', message);
            return;
        }

        if (json.type === 'color') {
            myColor = json.data;
            status.text(myName + ': ').css('color', myColor);
            input.removeAttr('disabled').focus();
        } else if (json.type === 'history') {
            for (var i=0; i < json.data.length; i++) {
                addMessage(json.data[i].author, json.data[i].text, json.data[i].color, json.data[i].time);
            }
        } else if (json.type === 'message') {
            input.removeAttr('disabled');
            addMessage(json.data.author, json.data.text, json.data.color, json.data.time);
        } else {
            console.log('Hmm..., I\'ve never seen JSON like this: ', json);
        }
    });

    input.keydown(function(e) {
        if (e.keyCode === 13) {
            var msg = $(this).val();
            if (!msg) {
                return;
            }

            socket.send(msg);
            $(this).val('');
            input.attr('disabled', 'disabled');

            if (myName === false) {
                myName = msg;
            }
        }
    });

    function addMessage(author, message, color, dt) {
        content.prepend('<p><span style="color:' + color + '">' + author + '</span> @ ' +
             + dt + ': ' + message + '</p>');
    }
});
