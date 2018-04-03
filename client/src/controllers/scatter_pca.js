import * as d3 from 'd3'
import _ from 'lodash'

/**
 * Handles drawing a scatter plot for 2-dimensional PCA data.
 */
class ScatterPca {
  /**
   * Constructor
   */
  constructor () {
    /**
     * Related to drawing
     */
    this.outerWidth = 1050
    this.outerHeight = 600
    this.margin = {
      top: 10,
      right: 70,
      bottom: 10,
      left: 70
    }
    this.background = '#fff'
    this.dot_radius = 4
    this.axis = true

    /**
     * Interactions
     */
    this.drag = true
    this.hover = false
    this.dispatch = d3.dispatch('focus-one')

    /**
     * Related to PCA
     */
    this.data = []

    /**
     * Callbacks
     */
    this.onSelected = () => {}
    this.onProbed = () => {}
  }

  /**
   * Entry point.
   * @param parent
   */
  draw (parent) {
    let outerWidth = this.outerWidth
    let outerHeight = this.outerHeight
    let margin = this.margin
    let width = outerWidth - margin.left - margin.right
    let height = outerHeight - margin.top - margin.bottom
    let that = this

    let data = this.data

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

    let boundZoom = zoom.bind(window, svg, x, y, xAxis, yAxis)
    let zoomBeh = d3.zoom()
      .on("zoom", boundZoom)

    let dragger = d3.drag()
      .on('start', function () {
        d3.select(this)
          .classed('highlight', true)
          .style('fill', '#f00')
      })
      .on('drag', function (d) {
        d.x += d3.event.dx
        d.y += d3.event.dy
        d3.select(this).attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")"
        })
      })
      .on('end', function () {
        let x = d3.event.sourceEvent.offsetX
        let y = d3.event.sourceEvent.offsetY

        x = xMin + x / width * (xMax - xMin)
        y = yMin + (1 - y / height) * (yMax - yMin)

        let i = d3.event.subject.i

        that.onProbed(x, y, i)

        // TODO: turn back style?
        d3.select(this)
          .style('fill', '#000')
      })

    svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .call(zoomBeh)

    // Blank
    svg.append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", this.background)
      .call(zoomBeh)

    // Brush
    svg.append("g")
      .attr("class", "brush")
      .call(d3.brush()
        .on('start', brushstart)
        .on('brush', brushing)
        .on("end", brushended))

    if (this.axis) {
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
    }

    // Axes Lines
    let objects = svg.append("svg")
      .classed("objects", true)
      .attr("width", width)
      .attr("height", height)

    if (this.axis) {
      objects.append("svg:line")
        .classed("axisLine hAxisLine", true)
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", width)
        .attr("y2", 0)
        .attr("transform", "translate(0," + height + ")")
      objects.append("svg:line")
        .classed("axisLine vAxisLine", true)
        .attr("transform", "translate(20 ,0)")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", 0)
        .attr("y2", height)
    }

    // Dots
    let dots = objects.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .classed("dot", true)
      .attr('r', () => this.dot_radius)
      .attr('cx', (d) => x(d.x))
      .attr('cy', (d) => y(d.y))
      .style("fill", (d) => d['mean_color'])

    if (this.drag) {
      dots.call(dragger)
    } else if (this.hover) {
      dots.on('mouseover', dotMouseover)
        .on('mouseout', dotMouseout)
    }

    this.dispatch.on('focus-one.dot', (p) => {
      if (!p) {
        unfocusDot()
      } else {
        focusDot(p, d3.selectAll('.dot').filter((d) => d.i === p.i))
      }
    })

    function focusDot (d, dot) {
      dot.attr('r', () => that.dot_radius * 2)
        .classed('focused', true)
      objects.append('text')
        .attr('x', () => Math.max(x(d.x) - 30, 15))
        .attr('y', () => Math.max(y(d.y) - 15, 15))
        .classed('focus-label', true)
        .text(() => d.name)
    }

    function unfocusDot () {
      d3.selectAll('.dot.focused').attr('r', that.dot_radius)
      d3.select('.focus-label').remove()
    }

    function dotMouseover(d) {
      focusDot(d, d3.select(this))
    }

    function dotMouseout () {
      unfocusDot()
    }

    function brushstart() {
      d3.selectAll('.dot').classed('muted', false)
      that.onSelected([])
    }

    function brushing () {
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

    function brushended () {
      if (!d3.event.selection) return // empty selection

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let scales = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

      let pts = _.filter(data, (p) => {
        return p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
      })

      that.onSelected(pts)
    }
  }

  focusDot (point) {
    this.dispatch.call('focus-one', this, point)
  }

  /**
   * Change data.
   * @param points
   */
  setData (points) {
    this.data = points
  }
}

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

export default ScatterPca
