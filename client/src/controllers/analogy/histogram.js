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
    this.outerHeight = 100

    /**
     * Private
     * @private
     */
    this._parent = null

    /**
     * Data
     */
    this.data = []
  }

  /**
   * Entry point
   * @param parent
   */
  draw (parent) {
    this._parent = parent

    let width = this.outerWidth
    let height = this.outerHeight - 20

    let svg = d3.select(parent)
      .append('svg')
      .attr('width', this.outerWidth)
      .attr('height', this.outerHeight)

    let x = d3.scaleBand().range([0, width])
      .domain(this.data.map((d) => d.x0))
    let y = d3.scaleLinear().range([height, 0])
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
  }

  setData (data) {
    this.data = data
  }
}

export default Histogram
