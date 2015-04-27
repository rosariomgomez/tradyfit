function messages(type) {
  $.post('/notifications', {
      type: type,
  }).done(function(data) {
    var messages = data['msgs'];
    $('#title').text(data['type']);
    $('#num-unread').text(data['num-unread']);
    $('#num-sent').text(data['num-sent']);
    $('#num-received').text(data['num-received']);
    var $msg_ul = $('#messages');
    $msg_ul.empty(); // empty ul content
    // iterate over the messages
    messages.forEach(function (msg) {
      // create a new li and append it
      var $li = $('<li class="list-group-item msg" id="msg-' + msg.id + '"">')
      // create the link to the message
      $li.append($('<a>',{
        text: msg.subject,
        href: Flask.url_for('msg.message', {id: msg.id})
      }))
      .appendTo($msg_ul);
    });
  });
}