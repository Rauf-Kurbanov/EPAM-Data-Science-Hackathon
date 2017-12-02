

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
        console.log(idx);

        paragraph = data[idx];

        console.log(typeof(paragraph));
        console.log(paragraph);
        console.log(paragraph['text']);

        table.row.add({
                        'Information': {
                                        'text': paragraph['text'],
                                        'indices': paragraph['indices']
                                        }
                      }).draw()
    }    
}


function process_text(data) {
    var text = data['text'];
    var indices = data['indices'];

    var left = "<span class='highlight'>";
    var right = "</span>";

    var offset = (left + right).length;
    var cur_offset = 0;
    var start = 0;
    var end = 0;

    for (pair in indices) {
        start = indices[pair][0];
        end = indices[pair][1];
        start += cur_offset;
        end += cur_offset;
        text = text.slice(0, start) + left + text.slice(start, end) + right + text.slice(end);
        cur_offset += offset;
    }

        return text
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