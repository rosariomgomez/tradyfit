function messages(type) {
  $.post('/notifications', {
      type: type,
  }).done(function(data) {
    var messages = data['msgs']
    var $msg_ul = $('#messages');
    $msg_ul.empty(); // empty ul content
    // iterate over the messages
    messages.forEach(function (msg) {
      // create a new li and append it
      var $li = $('<li class="msg" id="msg-' + msg.id + '"">')
      // create the link to the message
      $('<a>',{
        text: msg.subject,
        href: Flask.url_for('msg.message', {id: msg.id})
      }).appendTo($li)
      .appendTo($msg_ul);
    });
  });
}