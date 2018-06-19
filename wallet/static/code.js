$(document).ready(function () {
    $.ajax({
        url: "/account",
        success: function(result) {
            $('#private_key').val(result.private_key);
            $('#public_key').val(result.public_key);
            $('#address').val(result.address);
        }
    });

    $("#new_account").click(function() {
        $.ajax({
            url: "/account",
            type: "POST",
            success: function(result) {
                $('#private_key').val(result.private_key);
                $('#public_key').val(result.public_key);
                $('#address').val(result.address);
            }
        });
    });

    $("#load_account").click(function() {
        account_id = $('#private_key').val();
        $.ajax({
            url: "/account/" + account_id,
            success: function(result) {
                $('#public_key').val(result.public_key);
                $('#address').val(result.address);
            }
        });
    });

    $("#logout").click(function() {
        $.ajax({
            url: "/account",
            type: "DELETE",
            success: function(result) {
                $('#private_key').val('');
                $('#public_key').val('');
                $('#address').val('');
            }
        });
    });


    $("#show_balance").click(function() {
        $.ajax({
            url: "/balance",
            success: function(result) {
                $('#balance').val(result.balance);
            }
        });
    });

    $("#sign_transaction").click(function() {
        var values = {};
        $('#transaction :input').each(function() {
            values[this.name] = $(this).val();
        });

        $.ajax({
            url: "/transactions/send",
            type: "POST",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data: JSON.stringify(values),
            success: function(result) {
                $('#signed_transaction').text(JSON.stringify(result, null, 4));
            }
        });
    });
});
