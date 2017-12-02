

if (!String.format) {
  String.format = function(format) {
    var args = Array.prototype.slice.call(arguments, 1);
    return format.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number] 
        : match
      ;
    });
  };
}


function add_search_results(data)
{
    table = $('#search_table').DataTable();

    table.clear();

    for(idx in data)
    {
        paragraph = data[idx];

        table.row.add({
                        'Information': {
                                        'first': paragraph['first'],
                                        'second': paragraph['second'],
                                        'third': paragraph['third']
                                        }
                      }).draw()
    }    
}


function process_text(data) {
    var first = data['first'];
    var second = data['second'];
    var third = data['third'];

    var left = "<span class='highlight'>";
    var right = "</span>";

    return first + left + second + right + third;
}



$(document).ready(function() {
  $('#search_table').DataTable( {
      select: true,
      "searching": false,
      "bInfo": false,
      "lengthChange": false,
      "columns": [
                    {
                       "data": "Information",
                       "render": function(data, type, row, meta)
                       {
                           return process_text(data)
                       }

                    }
                 ]
  });
});


function process_query() {
    var value = $('#query_text').val();

    if(value.length == 0)
    {
        alert("The query is empty!");
        return;
    }

    $.ajax({
      type: 'GET',
      url: '/process_query',
      data: {text: value},
      contentType: 'application/json',
      success: function(data)
      {
            if($("#search_div").is(':hidden'))
            {
                $("#search_div").show();
            }
            add_search_results(JSON.parse(data))
      },
      error: function(XMLHttpRequest, textStatus, errorThrown)
      {
        alert("Status: " + textStatus); alert("Error: " + errorThrown);
      }
    });
}


$("#query_submit_btn").click(function ()
    {
        process_query()
    }
);


$("#query_text").on("keyup", function (e)
    {
        var key = e.which;
        if (key != 13) {
            return;
        }

        process_query()
    }
)