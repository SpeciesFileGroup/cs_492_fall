var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

svg.call(d3.zoom().on('zoom', zoomed));

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink())
    .force("charge", d3.forceManyBody().strength([-120]).distanceMax([30]))
    .force("center", d3.forceCenter(width / 2, height / 2));

var container = svg.append('g');

// Toggle for ego networks on click (below).
var toggle = 0;

d3.json("http://localhost:9000/graph.json", function(error, graph) {
  if (error) throw error;

  var linkedByIndex = {};
  graph.links.forEach(function(d) {
    linkedByIndex[d.source + ',' + d.target] = 1;
    linkedByIndex[d.target + ',' + d.source] = 1;
  });

  // A function to test if two nodes are neighboring.
  function neighboring(a, b) {
    return linkedByIndex[a.index + ',' + b.index];
  }

  var link = container.append("g")
    .selectAll("line")
    .data(graph.links, function(d) { return d.source + ", " + d.target;})
    .enter().append("line")
    .attr('class', 'link');

  var node = container.append("g")
    .attr("class", "node")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
    .attr("fill", function(d) { return "red"; })
    .attr("r", 5)
    .attr("cx", function(d) { return d.x; })
    .attr("cy", function(d) { return d.y; })
    .attr('class', 'node')
      // On click, toggle ego networks for the selected node.
      .on('click', function(d, i) {
        if (toggle == 0) {
          // Ternary operator restyles links and nodes if they are adjacent.
          d3.selectAll('.link').style('stroke-opacity', function (l) {
            return l.target == d || l.source == d ? 1 : 0.1;
          });
          d3.selectAll('.node').style('opacity', function (n) {
            return neighboring(d, n) ? 1 : 0.1;
          });
          d3.select(this).style('opacity', 1);
          toggle = 1;
        }
        else {
          // Restore nodes and links to normal opacity.
          d3.selectAll('.link').style('stroke-opacity', '0.6');
          d3.selectAll('.node').style('opacity', '1');
          toggle = 0;
        }
      })
      .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

  node.append("title")
      .text(function(d) { return "Journal: " + d.journal + "\n" + "Number of pages: " + d.num_pages });

  simulation
      .nodes(graph.nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(graph.links);

  function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  }
});

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

function zoomed() {
    container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
}
