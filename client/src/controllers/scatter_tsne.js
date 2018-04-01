import * as d3 from 'd3'
import _ from 'lodash'

const margin = {
  top: 10,
  right: 0,
  bottom: 10,
  left: 0
}
const outerWidth = 864 - 200
const outerHeight = 400
const width = outerWidth - margin.left - margin.right
const height = outerHeight - margin.top - margin.bottom

let data = []
let callback = () => {}

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

function brushstart() {
  d3.selectAll('.dot').classed('muted', false)
  callback([])
}

function brushing (x, y) {
  if (!d3.event.selection) return // empty selection

  // x0, y0, x1, y1
  let sel = _.flatten(d3.event.selection)
  let scales = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

  // change color of selected points
  d3.selectAll('.dot')
    .classed('muted', (p) => {
      let inside = p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
      return !inside
    })
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
function draw (parent, dot_size) {
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

  let boundBrushend = brushended.bind(window, x, y)
  let boundBrushing = brushing.bind(window, x, y)
  let boundBrushstart = brushstart.bind(window)

  let brush = d3.brush()
    .on('start', boundBrushstart)
    .on('brush', boundBrushing)
    .on("end", boundBrushend)

  svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  // Blank
  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", '#fff')

  // X Axis
  svg.append("g")
    .classed("x axis", true)
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)

  // Y Axis
  svg.append("g")
    .classed("y axis", true)
    .attr("transform", "translate(20 ,0)")
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
    .attr("transform", "translate(0 ,0)")
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
    .attr('r', () => dot_size)
    .attr('cx', (d) => x(d.x))
    .attr('cy', (d) => y(d.y))
    .style("fill", (d) => d['mean_color'])

  // Brush
  objects.append("g")
    .attr("class", "brush")
    .call(brush)
}

export {draw, setData, setCb}
