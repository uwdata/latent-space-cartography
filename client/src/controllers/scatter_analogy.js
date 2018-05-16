import * as d3 from 'd3'

import Scales from './analogy/scales'
import DotBrush from './analogy/brush'
import Dots from './analogy/dots'
import Vectors from './analogy/vectors'

/**
 * Handles drawing a scatter plot for 2-dimensional data.
 */
class Scatter {
  /**
   * Constructor
   */
  constructor () {
    /**
     * Related to drawing
     */
    this.outerWidth = 1050
    this.outerHeight = 600
    this.margin = {
      top: 10,
      right: 70,
      bottom: 10,
      left: 70
    }
    this.background = '#fff'
    this.dot_radius = 4
    this.dot_color = 'mean_color'
    this.mark_type = 1 //FIXME: create a new file

    /**
     * Interactions
     */
    this.dispatch = d3.dispatch(
      'dot-focus-one',
      'dot-focus-set',
      'toggle-background',
      'toggle-brushing',
      'zoom-view')
    this.mode_brush = false // whether we are in brushing mode

    /**
     * Related to PCA
     */
    this.data = []

    /**
     * Callbacks
     */
    this.emitter = {
      onSelected: () => {},
      onDotClicked: () => {},
      onDotHovered: () => {}
    }

    /**
     * Private
     */
    this._scales = null
    this._vectors = null
  }

  /**
   * Entry point.
   * @param parent
   */
  draw (parent) {
    let outerWidth = this.outerWidth
    let outerHeight = this.outerHeight
    let margin = this.margin
    let that = this

    let data = this.data
    let emitter = this.emitter

    let scales = new Scales(data, outerWidth, outerHeight, margin)
    this._scales = scales

    let svg = d3.select(parent)
      .append("svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)

    // Zoom, brush and drag
    let zoomBeh = d3.zoom()
      .scaleExtent([0.5, 3])
      .on("zoom", zoom)
    let dot_brush = new DotBrush(data, scales, emitter)

    svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    // Blank
    let rect = svg.append("rect")
      .attr("width", scales.width())
      .attr("height", scales.height())
      .attr("fill", this.background)

    // Brush & Zoom
    rect.call(zoomBeh)
    toggleBrushing()

    // Object Container
    let objects = svg.append("svg")
      .classed("objects", true)
      .attr("width", scales.width())
      .attr("height", scales.height())

    // Dots
    let dots = new Dots(scales, objects, this.dot_radius,
      this.dot_color, this.mark_type)
    dots.draw(data, emitter, this.dispatch)

    // Lines
    this._vectors = new Vectors(scales, objects)

    /**
     * =========================
     * Register event handlers for dispatcher, to communicate with outside.
     */
    this.dispatch.on('toggle-background', () => {
      rect.attr("fill", this.background)
    })

    this.dispatch.on('zoom-view', (factor) => {
      rect.transition().duration(1000).call(zoomBeh.scaleBy, factor)
    })

    this.dispatch.on('toggle-brushing', () => {
      toggleBrushing()
    })

    /**
     * =========================
     * Event handlers
     */
    function toggleBrushing () {
      if (that.mode_brush) {
        // create brush that is on top of everything
        dot_brush.attach(svg)
      } else {
        // remove brush
        dot_brush.remove()
      }
    }

    function zoom () {
      // create new scales
      scales.x = d3.event.transform.rescaleX(scales.initialX)
      scales.y = d3.event.transform.rescaleY(scales.initialY)

      // update dots
      svg.selectAll(".dot")
        .attr('cx', (d) => scales.x(d.x))
        .attr('cy', (d) => scales.y(d.y))

      // clear brush
      dot_brush.clear()
    }
  }

  /**
   * Focus one dot (when mouse hovering on top of it, for example)
   * @param point
   */
  focusDot (point) {
    this.dispatch.call('dot-focus-one', this, point)
  }

  focusSet (points) {
    this.dispatch.call('dot-focus-set', this, points)
  }

  /**
   * Toggle brushing.
   * @param on Whether to turn brushing on.
   */
  toggleBrushing (on) {
    this.mode_brush = on
    this.dispatch.call('toggle-brushing', this)
  }

  /**
   * Change background without re-draw.
   * @param color Background color.
   */
  toggleBackground (color) {
    this.background = color
    this.dispatch.call('toggle-background', this)
  }

  /**
   * Zoom.
   * @param factor
   */
  zoomView (factor) {
    this.dispatch.call('zoom-view', this, factor)
  }

  /**
   * Change data.
   * @param points
   */
  setData (points) {
    this.data = points
  }
}

export default Scatter
