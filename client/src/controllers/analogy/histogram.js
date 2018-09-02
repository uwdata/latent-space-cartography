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
    this.mean = -2
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

    let x = d3.scaleBand().range([0, width]).paddingInner(0.1)
      .domain(this.data.map((d) => d.x0))
    let y = d3.scaleLinear().range([height, p_top])
      .domain([0, d3.max(this.data, (d) => d.y)])

    let g = svg.append('g')
      .classed('hist', true)

    let x_axis = d3.axisBottom(x)
      // .tickValues(['-0.5', '0.0', '0.5'])

    let labels = _.keyBy(['-0.8', '-0.6', '-0.4', '-0.2',
      '0.0', '0.2', '0.4', '0.6', '0.8'])
    function custom_x (g) {
      g.call(x_axis)
      g.selectAll('text')
        .filter(function () {
          return !labels[d3.select(this).text()]
        })
        .remove()

      g.selectAll('text')
        .attr('fill', '#6c757d')
    }

    // axis
    g.append('g')
      .attr('class', 'axis axis--x')
      .attr('transform', `translate(0,${height})`)
      .call(custom_x)

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
        .text(`Average: ${this.mean.toFixed(2)}`)
        .attr('x', x0)
        .attr('y', 10)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .attr('fill', c_red)
    }
  }

  setData (data, mean = -2) {
    this.data = data
    this.mean = mean
  }
}

export default Histogram
