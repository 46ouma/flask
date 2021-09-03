function CircleBar(e) {
  $(e)
    .circleProgress({ fill: { color: "#fe53bb" } })
    .on("circle-animation-progress", function(_event, _progress, stepValue) {
      $(this)
        .find("strong")
        .text(String(parseInt(stepValue)) + "%");
    });
}
CircleBar(".round");
