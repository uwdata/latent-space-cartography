import * as d3 from 'd3'

/**
 * Distribution on initial axes
 */
class InitialAxes {
  constructor (styles = {}) {
    /**
     * Public, styles
     */
    this.outerWidth = styles.outerWidth || 220
    this.outerHeight = 0
    this.lineHeight = 5

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
    let data = this.data

    // width and height
    let p_top = 20
    this.outerHeight = this.data.length * this.lineHeight + p_top
    let width = this.outerWidth

    // scales
    let x = d3.scaleLinear().range([0, width])
      .domain([d3.min(data, (d) => d.x0), d3.max(data, (d) => d.x3)])

    let svg = d3.select(parent)
      .append('svg')
      .attr('width', this.outerWidth)
      .attr('height', this.outerHeight)

    let g = svg.append('g')
      .classed('lines', true)

    let x_axis = d3.axisTop(x).ticks(3)

    function custom_x (g) {
      g.call(x_axis)

      g.selectAll('text')
        .attr('fill', '#aaa')

      g.selectAll('.tick line')
        .style('stroke', '#aaa')

      g.selectAll('.domain').remove()
    }

    // axis
    g.append('g')
      .attr('class', 'axis axis--x')
      .attr('transform', `translate(0, ${p_top - 3})`)
      .call(custom_x)

    // min to max
    g.selectAll('.line-dash')
      .data(this.data)
      .enter()
      .append('line')
      .classed('line-dash', true)
      .attr('x1', (d) => x(d.x0))
      .attr('y1', (d, i) => i * this.lineHeight + p_top)
      .attr('x2', (d) => x(d.x3))
      .attr('y2', (d, i) => i * this.lineHeight + p_top)
      .style('stroke', '#444')
      .style('stroke-opacity', '0.5')
      .style('stroke-dasharray', '2,2')
      .style('stroke-width', 2)

    // Q1 to Q3
    g.selectAll('.line-solid')
      .data(this.data)
      .enter()
      .append('line')
      .classed('line-solid', true)
      .attr('x1', (d) => x(d.x1))
      .attr('y1', (d, i) => i * this.lineHeight + p_top)
      .attr('x2', (d) => x(d.x2))
      .attr('y2', (d, i) => i * this.lineHeight + p_top)
      .style('stroke', '#444')
      .style('stroke-width', 2)
  }

  /**
   * Change data
   * @param data
   */
  setData (data) {
    this.data = data
  }
}

export default InitialAxes
