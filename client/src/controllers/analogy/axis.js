import * as d3 from 'd3'
import {CONFIG, DTYPE} from '../config'
import _ from 'lodash'

/**
 * @fileOverview
 * Axis for the scatter plot.
 */
class DotAxis {
  constructor (parent, scales, styles) {
    /**
     * Public
     */
    this.show = styles.chart_type === 2
    this.y_field = styles.y_field

    /**
     * Private
     */
    this._parent = parent
    this._scales = scales

    this._y_axis = null
  }

  /**
   * Custom styling for the y axis
   * @private
   */
  _custom_y () {
    const font_size = 10
    const min_offset = 30

    let word = 0
    _.each(this._scales.y_band.domain(), (d) => {
      d = d || 'unknown'
      word = Math.max(word, d.length)
    })
    let offset = Math.max(min_offset, word * font_size * 0.5 + 10)

    let g = this._parent.select('.axis-y')
    g.call(this._y_axis)
    g.select('.domain').remove()
    g.selectAll('.tick line')
      .attr('stroke-dasharray', '2,2')
    g.selectAll('.tick text')
      .attr('dx', offset)
      .attr('dy', -4)
      .attr('fill', '#6c757d')
      .classed('outlined-text', true)
  }

  /**
   * Manually draw the attribute vector X axis
   * @param g
   * @private
   */
  _drawVectorX (g) {
    let scales = this._scales

    let loc = scales.height() * 0.5
    let ends = [{x: 0, y: loc}, {x: scales.width(), y: loc}]

    let line = d3.line()
      .x((d) => d.x)
      .y((d) => d.y)

    let gy = g.append('g')
      .classed('axis-x', true)

    // x axis line
    gy.append('path')
      .datum(ends)
      .classed('line', true)
      .attr('d', line)
      .style('stroke-width', 2)
      .style('stroke', '#000')

    // text background
    gy.append('rect')
      .attr('x', scales.width() - 155)
      .attr('y', loc - 20)
      .attr('width', 130)
      .attr('height', 18)
      .attr('fill', '#fff')

    // axis title
    gy.append('text')
      .text('Attribute Vector Axis')
      .attr('x', scales.width() - 150)
      .attr('y', loc - 5)
      .style('font-weight', '500')
      .style('font-size', `14px`)
  }

  /**
   * Draw the axis
   */
  draw () {
    if (!this.show) return

    let scales = this._scales

    // y axis
    this._y_axis = d3.axisLeft(scales.y_band)
      .tickSize(scales.width())
      .tickFormat((d) => {
        let type = CONFIG.schema.type
        if (type[this.y_field] === DTYPE.categorical) {
          let name = d || 'Unknown'
          return _.toUpper(name[0]) + name.substr(1)
        }

        return d
      })

    let g = this._parent.append('g')
      .classed('axis', true)

    g.append('g')
      .classed('axis-y', true)
      .attr('transform', `translate(${scales.width()}, 0)`)
      .call(this._custom_y.bind(this))

    this._drawVectorX(g)
  }

  /**
   * Handle zoom, assuming all scales are already updated
   */
  zoom () {
    if (!this.show) return
    this._y_axis.scale(this._scales.y_band)
    let g = this._parent.select('.axis-y')
    g.call(this._custom_y.bind(this))
  }
}

export default DotAxis
