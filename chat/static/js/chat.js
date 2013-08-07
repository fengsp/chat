$(function() {
    "use strict";

    var content = $('#Chat');
    var input = $('#input');

    var myColor = false;
    var myName = false;

    var socket = io.connect('/chat');
    
    socket.on('connect', function () {
        sysMessage('上线成功，输入名字按回车发送...');
        input.removeAttr('disabled').val('请输入名字...回车发送');
    });

    socket.on('disconnect', function () {
        sysMessage('你已经离线，请检查网络...');
        input.attr('disabled', 'disabled').val('未连接');
    });
    
    socket.on('message', function (message) {
        var json = message;

        if (json.type === 'color') {
            myColor = json.data;
            sysMessage('你可以开始聊天啦...');
            input.removeAttr('disabled').focus();
        } else if (json.type === 'history') {
            for (var i=0; i < json.data.length; i++) {
                addMessage(json.data[i].type, json.data[i].author, json.data[i].text, json.data[i].color, json.data[i].time);
            }
        } else if (json.type === 'message') {
            input.removeAttr('disabled');
            addMessage(json.data.type, json.data.author, json.data.text, json.data.color, json.data.time);
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
    
    input.click(function(e) {
        $(this).val('');
    });

    function addMessage(type, author, message, color, dt) {
        if (color == 'red') {
            var buddy = 'sys';
        } else {
            var buddy = type;
        }
        content.append('<div class="item message ' + type + ' ' + color + '-theme">'
            + '<img alt="avatar" src="../static/img/buddy_' + buddy + '.png" class="avatar ' + type + '" />'
             + '<span class="name">' + author + '</span>'
             + '<span class="body ' + color + '">' + message + '</span>'
              +  '<span class="time">' +dt + '</span>'
            + '</div>');
    }
    
    function sysMessage(message) {
        var currentTime = new Date();
        var time = currentTime.getHours() + ':' + (currentTime.getMinutes() < 10 ? '0' + currentTime.getMinutes() : currentTime.getMinutes());
        addMessage('out', '系统消息', message, 'red', time)
    }
});
