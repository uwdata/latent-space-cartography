import * as d3 from 'd3'
import _ from 'lodash'

/**
 * Histogram for pairwise angles
 */
class Histogram {
  constructor () {
    /**
     * Public, styles
     */
    this.outerWidth = 300
    this.outerHeight = 80

    /**
     * Private
     * @private
     */
    this._parent = null

    /**
     * Data
     */
    this.data = []
    this.background = []
    this.mean = -2
    this.effect = 0
    this.unit = 1
  }

  /**
   * Entry point
   * @param parent
   */
  draw (parent) {
    this._parent = parent

    let width = this.outerWidth
    let height = this.outerHeight - 20
    let p_top = 15

    let c_red = '#dc3545'

    let svg = d3.select(parent)
      .append('svg')
      .attr('width', this.outerWidth)
      .attr('height', this.outerHeight)

    // scales
    let x = d3.scaleBand().range([0, width]).paddingInner(0.1)
      .domain(this.data.map((d) => d.x0))
    let y = d3.scaleLinear().range([height, p_top])
      .domain([0, d3.max(this.data, (d) => d.y)])
    // scales for area chart
    let xx = d3.scaleBand().range([0, width])
      .domain(this.background.map((d) => d.x))
    let yy = d3.scaleLinear().range([height, p_top])
      .domain([0, d3.max(this.background, (d) => d.y)])
    // scales for x-axis
    let bo = x.bandwidth() * 0.5
    let xr = d3.scaleLinear().range([x('-1.0') + bo, x('1.0') + bo])
      .domain([-1 / this.unit, 1 / this.unit])

    let g = svg.append('g')
      .classed('hist', true)

    let x_axis = d3.axisBottom(xr)

    function custom_x (g) {
      g.call(x_axis)

      g.selectAll('text')
        .attr('fill', '#6c757d')
    }

    // axis
    g.append('g')
      .attr('class', 'axis axis--x')
      .attr('transform', `translate(0,${height})`)
      .call(custom_x)

    // area chart
    let area = d3.area()
      .x((d) => xx(d.x))
      .y1((d) => yy(d.y))
      .y0(yy(0))
    g.append('path')
      .datum(this.background)
      .attr('fill', '#ddd')
      .attr('d', area)

    // bars
    g.selectAll('.bar')
      .data(this.data)
      .enter()
      .append('rect')
      .classed('bar', true)
      .attr('x', (d) => x(d.x0) + x.bandwidth() * 0.5)
      .attr('y', (d) => y(d.y))
      .attr('width', x.bandwidth())
      .attr('height', (d) => height - y(d.y))
      .attr('fill', '#aaa')

    // the average line
    if (this.mean > -1 && this.mean < 1) {
      let bin = (Math.floor(this.mean * 10) * 0.1).toFixed(1)
      let x0 = x(bin) + (this.mean - Number(bin)) * 10 * x.bandwidth()
        + x.bandwidth() * 0.5

      g.append('line')
        .attr('x1', x0)
        .attr('x2', x0)
        .attr('y1', p_top)
        .attr('y2', height)
        .attr('stroke', c_red)
        .attr('stroke-width', 2)

      g.append('text')
        .text(`Effect Size: ${(this.mean / this.unit).toFixed(2)}`)
        .attr('x', x0)
        .attr('y', 10)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .attr('fill', c_red)
    }

    // effect size
    // g.append('text')
    //   .text(`Effect Size: ${this.effect.toFixed(2)}`)
    //   .attr('x', 0)
    //   .attr('y', 50)
    //   .style('font-size', '10px')
    //   .attr('fill', 'black')
  }

  setData (data, background, mean = -2, effect = 0, unit = 1) {
    this.data = data
    this.background = background
    this.mean = mean
    this.effect = effect
    this.unit = unit
  }
}

export default Histogram
