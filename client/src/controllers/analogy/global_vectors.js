import * as d3 from 'd3'
import {moveToFront} from './util'
import _ from 'lodash'

class GlobalVectors {
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
    this.lineWidth = styles.lineWidth || 3
    this.background = styles.background || '#fff'
    this.hide = true

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
    this._dispatch.on('toggle-background.vector', (color) => {
      this.background = color
      d3.selectAll('.vector-background')
        .style('stroke', color)
    })
  }

  _drawCurve (vector, group, id = '', label = '') {
    let scales = this._scales

    let line = d3.line()
      .x((d) => scales.getX(d))
      .y((d) => scales.getY(d))
      .curve(d3.curveCatmullRom)

    // line background
    this._drawLine(line, vector, group)
      .classed('vector-background', true)
      .style('stroke', this.background)
      .style('stroke-opacity', 0.9)
      .style('stroke-linecap', 'round')
      .style('stroke-width', this.lineWidth + 6)

    // the actual line
    let l = this._drawLine(line, vector, group)
      .classed('vector-curve', true)
      .style('stroke', 'red')
      .style('stroke-linecap', 'round')
      .style('stroke-width', this.lineWidth)

    // text label
    label = label || 'Untitled'
    const font_size = 10
    let words = label.split('-')
    let x0 = scales.getX(vector[0]) + 5
    let y0 = scales.getY(vector[0])

    let txt = group.append('text')
      .text(null)
      .attr('x', x0)
      .attr('y', y0)
      .attr('fill', '#343a40')
      .style('font-size', `${font_size}px`)
      .classed('outlined-text', true)

    _.each(words, (word, idx) => {
      txt.append('tspan')
        .text(word)
        .attr('x', x0)
        .attr('y', y0)
        .attr('dy', idx * font_size)
    })

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

  setData (paths) {
    this.paths = paths
  }

  redraw () {
    // remove previous vector
    d3.selectAll('.global-vector-group').remove()

    // hide flag on: do not draw anything
    if (this.hide) {
      return
    }

    // draw curves
    if (this.paths && this.paths.length) {
      // group
      let group = this._parent.append('g')
        .classed('global-vector-group', true)
        .on('mouseover', () => {moveToFront(group)})

      _.each(this.paths, (path) => {
        this._drawCurve(path.coordinates, group, path.id, path.label)
      })
    }
  }

  hoverVector (vid) {
    let g = d3.select('.global-vector-group')

    g.selectAll('.line.vector-curve')
      .style('stroke', 'red')

    g.selectAll('#' + vid)
      .style('stroke', '#0ff')
  }
}

export default GlobalVectors
