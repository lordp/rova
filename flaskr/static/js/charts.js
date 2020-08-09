function safe_split(list) {
  try {
    return list.split(",");
  } catch {
    return list;
  }
}

$(document).ready(function() {
  var daily_plays = safe_split($("#daily_plays").data("plays"));
  var daily_labels = safe_split($("#daily_plays").data("labels"));
  if (daily_plays) {
    var daily_chart = c3.generate({
      bindto: "#chart-daily-plays",
      size: {
        height: 200
      },
      legend: {
        show: false
      },
      data: {
        x: "x",
        columns: [["x"].concat(daily_labels), ["Plays"].concat(daily_plays)],
        type: "area"
      },
      point: {
        show: false
      },
      tooltip: {
        format: {
          title: function(value, index) {
            var options = {
              weekday: "short",
              year: "numeric",
              month: "long",
              day: "numeric"
            };
            return value.toLocaleDateString("en-nz", options);
          }
        }
      },
      axis: {
        x: {
          type: "timeseries",
          tick: {
            format: "%m-%d"
          }
        }
      },
      padding: {
        right: 10
      }
    });
  }

  var hourly_plays = safe_split($("#hourly_plays").data("plays"));
  var hourly_labels = safe_split($("#hourly_plays").data("labels"));
  if (hourly_plays) {
    var hourly_chart = c3.generate({
      bindto: "#chart-hourly-plays",
      size: {
        height: 200
      },
      legend: {
        show: false
      },
      data: {
        columns: [["Plays"].concat(hourly_plays)],
        type: "bar"
      },
      tooltip: {
        format: {
          title: function(hour, index) {
            var am_pm = hour >= 12 ? "pm" : "am";
            hour = hour % 12 || 12;

            return hour + am_pm;
          }
        }
      },
      padding: {
        right: 10
      }
    });
  }

  var music = $('#music_ratio').data('music');
  var other = $('#music_ratio').data('other');
  if (music) {
    var music_ratio = c3.generate({
        bindto: '#chart-music-ratio',
        size: {
        height: 200
        },
        data: {
        columns: [
            ['Music', music],
            ['Other', other]
        ],
        type: 'pie'
        }
    })
  }
});
