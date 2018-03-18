import * as d3 from 'd3'
import d3Tip from 'd3-tip'
import _ from 'lodash'

const margin = {
  top: 10,
  right: 70,
  bottom: 10,
  left: 70
}
const outerWidth = 1050
const outerHeight = 600
const width = outerWidth - margin.left - margin.right
const height = outerHeight - margin.top - margin.bottom

let data = []
let callback = () => {}

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

// TODO: fix these
function setCb (fn) {
  callback = fn
}

function brushing (x, y) {
  if (!d3.event.selection) return // empty selection

  // x0, y0, x1, y1
  let sel = _.flatten(d3.event.selection)
  let scales = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

  // change color of selected points
  d3.selectAll('.dot')
    .style('fill', () => '#000')
    .filter((p) => {
      return p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
    })
    .style('fill', () => '#f00')
}

function brushended (x, y) {
  if (!d3.event.selection) return // empty selection

  // x0, y0, x1, y1
  let sel = _.flatten(d3.event.selection)
  let scales = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

  let pts = _.filter(data, (p) => {
    return p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
  })

  let images = _.map(pts, (p) => `/data/logos/${p.i}.jpg`)

  callback(images)
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
      return `<img src="/data/logos/${d.i}.jpg" alt="Logo Image"/>`
    })

  let boundZoom = zoom.bind(window, svg, x, y, xAxis, yAxis)
  let boundBrushend = brushended.bind(window, x, y)
  let boundBrushing = brushing.bind(window, x, y)

  let zoomBeh = d3.zoom()
    .on("zoom", boundZoom)

  svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoomBeh)

  // Blank
  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", '#fff')
    .call(zoomBeh)
    .call(tip)

  // Brush
  svg.append("g")
    .attr("class", "brush")
    .call(d3.brush()
      .on('brush', boundBrushing)
      .on("end", boundBrushend))

  // X Axis
  svg.append("g")
    .classed("x axis", true)
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)

  // Y Axis
  svg.append("g")
    .classed("y axis", true)
    .attr("transform", "translate(10 ,0)")
    .call(yAxis)

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
    .attr("transform", "translate(10 ,0)")
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
    // .on('mouseover', tip.show)
    // .on("mouseout", tip.hide)
}

export {draw, setData, setCb}
