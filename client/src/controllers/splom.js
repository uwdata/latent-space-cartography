import * as d3 from 'd3'
import _ from 'lodash'

// ugly global
let brushCell

/**
 * Handles drawing a scatter plots matrix for PCA data.
 */
class Splom {
  /**
   * Constructor
   */
  constructor (pca_dim) {
    /**
     * Related to drawing
     */
    this.width = 1000
    this.size = 120
    this.padding = 20

    /**
     * Related to PCA
     */
    this.pca_dim = pca_dim
    this.data = []
    this.variation = []

    /**
     * Callbacks
     */
    this.onSelected = () => {}
  }

  /**
   * Entry point.
   * @param parent
   */
  draw (parent) {
    let width = this.width
    let size = this.size
    let padding = this.padding
    let data = this.data
    let onSelected = this.onSelected.bind(this)

    let x = d3.scaleLinear()
      .range([padding / 2, size - padding / 2]).nice()

    let y = d3.scaleLinear()
      .range([size - padding / 2, padding / 2]).nice()

    let xAxis = d3.axisTop(x).ticks(6)

    let yAxis = d3.axisLeft(y).ticks(6)

    let traits = _.map(_.range(this.pca_dim), (i) => `PC${i}`)
    let domainByTrait = {}
    let n = traits.length

    _.forEach(traits, (trait) => {
      domainByTrait[trait] = d3.extent(data, (d) => d[trait])
    })

    xAxis.tickSize(-size * n)
    yAxis.tickSize(-size * n)

    // brush
    let brush = d3.brush()
      .extent([[x.range()[0], y.range()[1]], [x.range()[1], y.range()[0]]])
      .on("start", brushstart)
      .on("brush", brushing)
      .on("end", brushend)

    // canvas
    let svg = d3.select(parent)
      .append("svg")
      .attr("width", size * n + padding)
      .attr("height", size * n + padding)
      .append('g')
      .attr("transform", "translate(" + padding + "," + padding / 2 + ")")

    // draw x axis
    svg.selectAll(".x.axis")
      .data(traits)
      .enter().append("g")
      .attr("class", "x axis")
      .attr("transform", (d, i) => "translate(" + (n - i - 1) * size + ",0)")
      .each(function (d) {
        x.domain(domainByTrait[d])
        d3.select(this).call(xAxis)
      })

    // draw y axis
    svg.selectAll(".y.axis")
      .data(traits)
      .enter().append("g")
      .attr("class", "y axis")
      .attr("transform", (d, i) => "translate(0," + i * size + ")")
      .each(function (d) {
        y.domain(domainByTrait[d])
        d3.select(this).call(yAxis)
      })

    // draw rectangular cells
    let cell = svg.selectAll(".cell")
      .data(_cross(traits, traits))
      .enter().append("g")
      .attr("class", "cell")
      .attr("transform", (d) => "translate(" + (n - d.i - 1) * size + "," + d.j * size + ")")
      .each(plot)

    // titles for the diagonal.
    cell.filter((d) => d.i === d.j)
      .append("text")
      .attr("x", padding)
      .attr("y", padding)
      .attr("dy", ".71em")
      .text((d) => `${d.x}: ${(this.variation[d.i] * 100).toFixed(1)}%`)
      // .fill('#000')
      // .attr('font-size', '20px')

    cell.filter((d) => d.i >= d.j).call(brush)

    function plot(p) {
      // skip half of the matrix
      if (p.i < p.j) return
      let cell = d3.select(this)

      x.domain(domainByTrait[p.x])
      y.domain(domainByTrait[p.y])

      cell.append("rect")
        .attr("class", "frame")
        .attr("x", padding / 2)
        .attr("y", padding / 2)
        .attr("width", size - padding)
        .attr("height", size - padding)

      cell.selectAll("circle")
        .data(data)
        .enter().append("circle")
        .attr("cx", (d) => x(d[p.x]))
        .attr("cy", (d) => y(d[p.y]))
        .attr("r", 3)
    }

    function brushstart(p) {
      if (brushCell !== this) {
        d3.select(brushCell).call(brush.move, null)
        x.domain(domainByTrait[p.x])
        y.domain(domainByTrait[p.y])
        brushCell = this
      }
    }

    function brushing(p) {
      if (!d3.event.selection) return // empty selection

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let e = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

      svg.selectAll("circle").classed("highlight", (d) => {
        return d[p.x] >= e[0] && d[p.x] <= e[2]
          && d[p.y] >= e[3] && d[p.y] <= e[1]
      })
    }

    function brushend(p) {
      if (d3.event.selection === null) {
        svg.selectAll("circle").classed("highlight", false)
        onSelected([])
        return
      }

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let e = _.map(sel, (s, idx) => idx % 2 ? y.invert(s) : x.invert(s))

      let pts = _.filter(data, (d) => {
        return d[p.x] >= e[0] && d[p.x] <= e[2]
          && d[p.y] >= e[3] && d[p.y] <= e[1]
      })

      let images = _.map(pts, (p) => `/data/logos/${p.i}.jpg`)

      onSelected(images)
    }
  }

  /**
   * Change data.
   * @param points
   */
  setData (points) {
    this.data = points
  }
}

/**
 * Utility function
 * @param a
 * @param b
 * @returns {Array}
 */
function _cross(a, b) {
  let c = []
  let n = a.length
  let m = b.length

  for (let i = -1; ++i < n;) {
    for (let j = -1; ++j < m;) {
      c.push({
        x: a[i],
        i: i,
        y: b[j],
        j: j
      })
    }
  }
  return c
}

export default Splom
