$("#delNotification").click(function (e) {
    e.preventDefault();
    $('#notificationDeleteModal').modal('show')
});

$("#addNotification").click(function (e) {
    e.preventDefault();
    $('#addNewNotification').modal('show')
});