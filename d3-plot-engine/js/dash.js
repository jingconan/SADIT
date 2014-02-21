/*jslint browser: true, vars:true, plusplus:true*/
/*global d3, io, FIG*/
"use strict";
var FIG = {};

FIG.initFigure = function (fig, xLim, yLim) {
    var width = fig.width,
        height = fig.height;

    var x = d3.scale.linear().domain(xLim)
        .range([0.1 * width, width]);

    var y = d3.scale.linear()
        .domain(yLim)
        .range([0.9 * height, 0]);

    /*jslint unparam: true*/
    var line = d3.svg.line()
        .x(function (d, i) { return x(i); })
        .y(function (d, i) { return y(d); });
    /*jslint unparam: true*/

    fig.xLim = xLim;
    fig.yLim = yLim;
    fig.x = x;
    fig.y = y;
    fig.line = line;
    fig.data = [];
    FIG.plotAxis(fig);
    fig.path = FIG.initPath(fig, fig.data);
    return fig;
};

FIG.plotAxis = function (fig) {
    var x = fig.x,
        y = fig.y,
        svg = fig.svg,
        width = fig.width,
        height = fig.height;
    // x axis
    var xAxis = d3.svg.axis().scale(x).tickSubdivide(true);
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + 0.9 * height + ")")
        .call(xAxis);

    // y axis
    var yAxis = d3.svg.axis().scale(y).ticks(4).orient("left");
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + 0.1 * width + ",0)")
        // .attr("transform", "translate(" + 200 + ",0)")
        .call(yAxis);

    // add x axis label
    svg.append("text")
        .attr("x", width / 2.0)
        .attr("y", height)
        .style("text-anchor", "middle")
        .text("time");

    // add y axis label
    var yLabelYPos = 0.5 * height,
        yLabelXPos = 0.05 * width;
    svg.append("text")
        .attr("transform", "rotate(-90, " + yLabelXPos + "," + yLabelYPos + ")")
        .attr("y", yLabelYPos)
        .attr("x", yLabelXPos)
        .style("text-anchor", "middle")
        .text("empirical measure");

    return fig;
};


FIG.createFigure = function (selector, width, height, margin) {
    var svg = d3.select(selector).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);
    return {
        svg: svg,
        width: width,
        height: height
    };
};

FIG.tick = function (fig, new_val) {
    var path = fig.path,
        line = fig.line,
        data = fig.data,
        xLim = fig.xLim;
    // push a new data point onto the back
    data.push(new_val);

    // pop the old data point off the front
    if (data.length > xLim[1] + 1) {
        data.shift();
    }

    // redraw the line, and slide it to the left
    // var diff = x(1) - x(2);
    path.attr("d", line); // redraw
        // .transition()
        // .duration(400)
        // .attr("transform", "translate(" + diff + ",0)"); // create animation of x offset
};

FIG.initPath = function (fig, data) {
    var svg = fig.svg,
        line = fig.line;
    return svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line);
};



FIG.margin = {
    top: 20,
    right: 20,
    bottom: 20,
    left: 40
};
// var width = 960 - margin.left - margin.right;
// var height = 500 - margin.top - margin.bottom;
FIG.fig = FIG.createFigure("#graph",
    960 - FIG.margin.left - FIG.margin.right,
    500 - FIG.margin.top - FIG.margin.bottom,
    FIG.margin);
FIG.fig = FIG.initFigure(FIG.fig, [0, 39], [0, 1]);


var socket = io.connect('http://localhost:3000');
socket.on('connect', function () {
    socket.on('recv_data', function (data) {
        if (data.type === 'FBAnoDetector') {
            FIG.tick(FIG.fig, data.entropy[0]);
        }
    });
});
