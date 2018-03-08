import * as d3 from 'd3'
import d3Tip from 'd3-tip'
import _ from 'lodash'

const margin = {
  top: 20,
  right: 70,
  bottom: 50,
  left: 70
}
const outerWidth = 1050
const outerHeight = 600
const width = outerWidth - margin.left - margin.right
const height = outerHeight - margin.top - margin.bottom

let data = []

function zoom (svg, x, y, xAxis, yAxis) {
  // create new scales
  let new_xScale = d3.event.transform.rescaleX(x)
  let new_yScale = d3.event.transform.rescaleY(y)

  // update axes
  svg.select(".x.axis").call(xAxis.scale(new_xScale))
  svg.select(".y.axis").call(yAxis.scale(new_yScale))

  // update dots
  svg.selectAll(".dot")
    .attr('cx', (d) => new_xScale(d.x))
    .attr('cy', (d) => new_yScale(d.y))
}

/**
 * Change data.
 * @param points
 */
function setData (points) {
  data = points
}

/**
 * Entry point.
 */
function draw (parent) {
  let x = d3.scaleLinear()
    .range([0, width]).nice()

  let y = d3.scaleLinear()
    .range([height, 0]).nice()

  let xAxis = d3.axisBottom(x).tickSize(-height)

  let yAxis = d3.axisLeft(y).tickSize(-width)

  let xMax = d3.max(data, (d) => d.x) * 1.05
  let xMin = d3.min(data, (d) => d.x) * 1.05
  let yMax = d3.max(data, (d) => d.y) * 1.05
  let yMin = d3.min(data, (d) => d.y) * 1.05

  x.domain([xMin, xMax])
  y.domain([yMin, yMax])

  let svg = d3.select(parent)
    .append("svg")
    .attr("width", outerWidth)
    .attr("height", outerHeight)

  // Hookup tooltip and zoom
  let tip = d3Tip()
    .attr("class", "d3-tip")
    .offset([-10, 0])
    .html(function(d) {
      let str = `<img src="/data/logos/${d.i}.jpg" alt="Logo Image"/>`
      return str
      // return `x: ${d.x}, y: ${d.y}, i: ${d.i}`
    })

  let boundZoom = zoom.bind(window, svg, x, y, xAxis, yAxis)

  let zoomBeh = d3.zoom()
    .on("zoom", boundZoom)

  svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoomBeh)
    .call(tip)

  // Blank
  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", '#fff')
    .call(zoomBeh)

  // X Axis
  svg.append("g")
    .classed("x axis", true)
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    // .append("text")
    // .classed("label", true)
    // .attr("x", width)
    // .attr("y", margin.bottom - 10)
    // .style("text-anchor", "end")
    // .text("X Axis")

  // Y Axis
  svg.append("g")
    .classed("y axis", true)
    .call(yAxis)
    // .append("text")
    // .classed("label", true)
    // .attr("transform", "rotate(-90)")
    // .attr("y", -margin.left)
    // .attr("dy", "1.5em")
    // .style("text-anchor", "end")
    // .text("Y Axis")

  // Axes Lines
  let objects = svg.append("svg")
    .classed("objects", true)
    .attr("width", width)
    .attr("height", height)
  objects.append("svg:line")
    .classed("axisLine hAxisLine", true)
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", width)
    .attr("y2", 0)
    .attr("transform", "translate(0," + height + ")")
  objects.append("svg:line")
    .classed("axisLine vAxisLine", true)
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", 0)
    .attr("y2", height)

  // Dots
  objects.selectAll(".dot")
    .data(data)
    .enter()
    .append("circle")
    .classed("dot", true)
    .attr('r', () => 5)
    .attr('cx', (d) => x(d.x))
    .attr('cy', (d) => y(d.y))
    .style("fill", () => '#000')
    .on("mouseover", tip.show)
    .on("mouseout", tip.hide)
}

export {draw, setData}
