import * as d3 from 'd3'
import {moveToFront} from './util'
import _ from 'lodash'

class GlobalPaths {
  /**
   * Constructor
   * @param scales
   * @param parent
   * @param dispatch
   * @param styles
   */
  constructor (scales, parent, dispatch, styles = {}) {
    /**
     * Public
     */
    // 0 - vector, 1 - pair
    this.line_style = styles.line_style || 0

    // 0 - combined, 1 - label start and end separately
    this.label_style = styles.label_style || 0

    this.id = styles.id || 'global-vector'
    this.background = styles.background || '#fff'
    this.hide = styles.hide

    /**
     * Private
     */
    this._scales = scales
    this._parent = parent
    this._dispatch = dispatch

    /**
     * Data
     */
    this.paths = []

    /**
     * Initialization
     */
    this._registerCallback()
  }

  /**
   * Register callbacks to dispatcher.
   * @private
   */
  _registerCallback () {
    if (!this._dispatch.on('toggle-background.vector')) {
      this._dispatch.on('toggle-background.vector', (color) => {
        this.background = color
        d3.selectAll('.vector-background')
          .style('stroke', color)
      })
    }
  }

  _drawCurve (vector, group, id = '', label = '') {
    let scales = this._scales

    const styles = [
      {
        lineWidth: 3,
        strokeColor: 'red',
        padding: 3
      },
      {
        lineWidth: 1,
        strokeColor: '#343a40',
        dash: '2,2',
        padding: 1
      }
    ]

    let style = styles[this.line_style]

    let line = d3.line()
      .x((d) => scales.getX(d))
      .y((d) => scales.getY(d))
      .curve(d3.curveCatmullRom.alpha(0.5))

    // line background
    this._drawLine(line, vector, group)
      .classed('vector-background', true)
      .style('stroke', this.background)
      .style('stroke-opacity', 0.9)
      .style('stroke-linecap', 'round')
      .style('stroke-width', style.lineWidth + style.padding * 2)

    // the actual line
    let l = this._drawLine(line, vector, group)
      .classed('vector-curve', true)
      .style('stroke', style.strokeColor)
      .style('stroke-linecap', 'round')
      .style('stroke-width', style.lineWidth)
    if (style.dash) {
      l.style('stroke-dasharray', style.dash)
    }

    // text label
    const font_size = 10
    const font_color = '#343a40'
    if (this.label_style === 0) {
      label = label || 'Untitled'
      let words = label.split('-')
      let x0 = scales.getX(vector[0]) + 5
      let y0 = scales.getY(vector[0])

      let txt = group.append('text')
        .text(null)
        .attr('x', x0)
        .attr('y', y0)
        .attr('fill', font_color)
        .style('font-size', `${font_size}px`)
        .classed('outlined-text', true)

      _.each(words, (word, idx) => {
        txt.append('tspan')
          .text(word)
          .attr('x', x0)
          .attr('y', y0)
          .attr('dy', idx * font_size)
      })
    } else {
      let words = label.split('-')
      _.each(words, (word, idx) => {
        idx = idx ? 0 : vector.length - 1
        let x_offset = word.length * font_size * 0.25

        group.append('text')
          .text(word)
          .attr('x', scales.getX(vector[idx]) - x_offset)
          .attr('y', scales.getY(vector[idx]) - font_size * 0.5)
          .attr('fill', font_color)
          .style('font-size', `${font_size}px`)
          .classed('outlined-text', true)
      })
    }

    if (id) {
      l.attr('id', id)
    }
  }

  _drawLine (line, vector, container) {
    return container.append('path')
      .datum(vector)
      .classed('line', true)
      .attr('d', line)
      .attr('fill', 'none')
  }

  /**
   * Set data.
   * @param {array} paths
   */
  setData (paths) {
    this.paths = paths
  }

  /**
   * Clear previous plot and draw current data.
   */
  redraw () {
    // remove previous vector
    d3.selectAll(`.${this.id}-group`).remove()

    // hide flag on: do not draw anything
    if (this.hide) {
      return
    }

    // draw curves
    if (this.paths && this.paths.length) {
      // group
      let group = this._parent.append('g')
        .classed(`${this.id}-group`, true)
        .on('mouseover', () => {moveToFront(group)})

      _.each(this.paths, (path) => {
        this._drawCurve(path.coordinates, group, path.id, path.label)
      })
    }
  }

  /**
   * Clear data and remove previous plots.
   */
  clear () {
    this.setData([])
    this.redraw()
  }

  /**
   * Ask the chart to highlight a vector.
   * @param {string} vid - DOM id of the vector to be highlighted.
   */
  hoverVector (vid) {
    let g = d3.select(`.${this.id}-group`)

    g.selectAll('.line.vector-curve')
      .style('stroke', 'red')

    g.selectAll('#' + vid)
      .style('stroke', '#0ff')
  }
}

export default GlobalPaths
