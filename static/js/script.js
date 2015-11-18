$(document).ready(function() {

  // Set formatting rules
  $("#topic_input").focusin(function() {
    $(".topic_box").css("border", "1px solid steelblue")
    $(".go_button").css("background", "steelblue")
  });

  $("#topic_input").focusout(function() {
    $(".topic_box").css("border", "1px solid #ccc")
    $(".go_button").css("background", "gray")
  });

  $(".go_button").hover(function() {
    $(".go_button").css("background", "#325c80")
  }, function() {
    if ($("#topic_input").is(":focus")) {
      $(".go_button").css("background", "steelblue")
    } else {
      $(".go_button").css("background", "gray")
    }
  });

  $(".topic_box").hover(function() {
    $(".topic_box").css("border", "1px solid steelblue")
  }, function() {
    if ($("#topic_input").is(":focus")) {
      $(".topic_box").css("border", "1px solid steelblue")
    } else {
      $(".topic_box").css("border", "1px solid #ccc")
    }
  });

  // Initalize page
  $("#summary_box").hide();
  $("#loading_gif").hide();
  $("#more_info_link").hide();
  $("#topic_input").focus()

  to_title_case = function(str) {
    /*
    IN:
      str = String to convert to title case

    OUT:
      String in title case, e.g. "This Is A String In Title Case"

    EXAMPLES:
      "this is a string in title case" --> "This Is A String In Title Case"
      "THIS IS A STRING IN TITLE CASE" --> "This Is A String In Title Case"
    */
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
  }

  var topic = ""

  send_topic = function(topic){
    /*
    IN:
      topic = String entered by user into the input bar topic to summarize

    OUT:
      Wikipeida article summarized and output to page
    */
    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/summarize",
      dataType: "json",
      async: true,
      data: "{\"topic\": \"" + topic + "\"}",

      success: function(data) {
        var summary_text = data["summary"];
        var wiki_topic = data["wiki_topic"];

        if (topic == "") {
          $("#summarized_topic").html("");
          $("#summary_p").html("");
        } else {
          $("#summarized_topic").html(to_title_case(topic));
          $("#summary_p").html(summary_text);
          var wiki_href_base = "https://en.wikipedia.org/wiki/"
          $("#more_info_link").attr("href", wiki_href_base + wiki_topic);

          $("#loading_gif").hide();
          $("#summarized_topic").show();
          $("#summary_p").show();
          $("#more_info_link").show();
        }
      },
      error: function(result) {}
    })
  }

  go = function() {
    // Get topic from input bar and pass to send_topic to send to server
    var topic = $("#topic_input").val();
    if (topic != "") {
      send_topic(topic);

      // Prep page formatting for summary to be output
      $("#title_topic_box").css("margin-top", "0%");
      $("#summarized_topic").hide();
      $("#summary_p").hide();
      $("#more_info_link").hide();
      $("#loading_gif").show();
      $("#summary_box").show();
    }
  }

});
