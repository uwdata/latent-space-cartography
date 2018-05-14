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

      // change color of selected points
      d3.selectAll('.dot')
        .classed('muted', (p) => {
          let inside = p.x >= bounds[0] && p.x <= bounds[2] && p.y >= bounds[3] && p.y <=bounds[1]
          return !inside
        })
    }

    function brushended () {
      // empty selection
      if (!d3.event.selection) return

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let bounds = _.map(sel, (s, idx) => idx % 2 ? scales.y.invert(s) : scales.x.invert(s))

      let pts = _.filter(data, (p) => {
        return p.x >= bounds[0] && p.x <= bounds[2] && p.y >= bounds[3] && p.y <=bounds[1]
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

export default DotBrush
