c$(document).ready(function() {
    $('#customForm').on('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission

        var formData = $(this).serializeArray();
        var data = {};
        $(formData).each(function(index, obj){
            data[obj.name] = obj.value;
        });

        // Replace the URL with your actual Flask API endpoint
        $.ajax({
            url: 'http://97.107.128.112:5000/predict', // Flask API endpoint
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                // Success: Display the response or take action
                $('#formResponse').html('Submission successful! Response: ' + JSON.stringify(response));
            },
            error: function(xhr, status, error) {
                // Error: Display an error message or take action
                $('#formResponse').html('Error submitting form.');
                console.error('Error:', error);
            }
        });
    });
});
