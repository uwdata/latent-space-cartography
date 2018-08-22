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
    this.lineWidth = styles.lineWidth || 2
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

  _drawCurve (vector, group, id = '') {
    let scales = this._scales

    let line = d3.line()
      .x((d) => scales.x(d.x))
      .y((d) => scales.y(d.y))
      .curve(d3.curveCatmullRom)

    // line background
    this._drawLine(line, vector, group)
      .classed('vector-background', true)
      .style('stroke', this.background)
      .style('stroke-opacity', 0.9)
      .style('stroke-linecap', 'round')
      .style('stroke-width', 6)

    // the actual line
    let l = this._drawLine(line, vector, group)
      .classed('vector-curve', true)
      .style('stroke', '#f00')
      .style('stroke-linecap', 'round')
      .style('stroke-width', this.lineWidth)

    if (id) {
      l.attr('id', id)
    }
  }

  _drawLine (line, vector, container) {
    return container.append('path')
      .datum(vector)
      .classed('line', true)
      .attr('d', line)
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
        this._drawCurve(path.coordinates, group, path.id)
      })
    }
  }

  hoverVector (vid) {
    let g = d3.select('.global-vector-group')

    g.selectAll('.line.vector-curve')
      .style('stroke', '#f00')

    g.selectAll('#' + vid)
      .style('stroke', '#0ff')
  }
}

export default GlobalVectors
