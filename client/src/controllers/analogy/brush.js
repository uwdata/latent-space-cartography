import * as d3 from 'd3'
import _ from 'lodash'

/**
 * @fileOverview
 * A brush for dots.
 */
class DotBrush {
  /**
   * Constructor
   * @param data
   * @param scales
   * @param emitter
   */
  constructor (data, scales, emitter) {
    /**
     * Brush behavior
     */
    this.behavior = this.init(data, scales, emitter)
  }

  /**
   * Initialize
   * @param data
   * @param scales
   * @param emitter
   */
  init (data, scales, emitter) {
    function brushstart () {
      d3.selectAll('.dot').classed('muted', false)
      emitter.onSelected([])
    }

    function brushing () {
      // empty selection
      if (!d3.event.selection) return

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let bounds = _.map(sel, (s, idx) => idx % 2 ? scales.y.invert(s) : scales.x.invert(s))
      bounds = label_bounds(bounds)

      // change color of selected points
      d3.selectAll('.dot')
        .classed('muted', (p) => {
          let inside = scales.getRawX(p) >= bounds.x0 &&
            scales.getRawX(p) <= bounds.x1 &&
            scales.getRawY(p) >= bounds.y0 &&
            scales.getRawY(p) <=bounds.y1
          return !inside
        })
    }

    function brushended () {
      // empty selection
      if (!d3.event.selection) return

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let bounds = _.map(sel, (s, idx) => idx % 2 ? scales.y.invert(s) : scales.x.invert(s))
      bounds = label_bounds(bounds)

      let pts = _.filter(data, (p) => {
        return scales.getRawX(p) >= bounds.x0 &&
          scales.getRawX(p) <= bounds.x1 &&
          scales.getRawY(p) >= bounds.y0 &&
          scales.getRawY(p) <=bounds.y1
      })

      emitter.onSelected(pts)
    }

    return d3.brush()
      .on('start', brushstart)
      .on('brush', brushing)
      .on("end", brushended)
  }

  /**
   * Clear current brush selection
   */
  clear () {
    d3.select('.brush').call(this.behavior.move, null)
  }

  /**
   * Remove brush div
   */
  remove () {
    d3.selectAll('.brush')
      .call(this.behavior.move, null)
      .remove()
  }

  /**
   * Attach the brush to the parent svg as the top-most layer
   * @param svg
   */
  attach (svg) {
    svg.append('g').attr('class', 'brush').call(this.behavior)
  }
}

/**
 * Helper function converting bounds array to an object.
 * @param arr
 * @returns {{x0: number, x1: number, y0: number, y1: number}}
 */
function label_bounds (arr) {
  return {
    x0: Math.min(arr[0], arr[2]),
    x1: Math.max(arr[0], arr[2]),
    y0: Math.min(arr[1], arr[3]),
    y1: Math.max(arr[1], arr[3])
  }
}

export default DotBrush
