import * as d3 from 'd3'
import _ from 'lodash'

import Scales from './analogy/scales'
import DotBrush from './analogy/brush'
import Dots from './analogy/dots'
import Vectors from './analogy/vectors'
import DotAxis from './analogy/axis'
import GlobalVectors from './analogy/global_vectors'

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
    this.mark_type = 1 // 1 - dot, 2 - image, 3 - text
    this.chart_type = 1 // 1 - scatter, 2 - bee swarm
    this.y_field = 'y' // which field is the y axis

    /**
     * Interactions
     */
    this.dispatch = d3.dispatch(
      'dot-focus-one',
      'dot-focus-set',
      'dot-center',
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
    this._dots = null
    this._vectors = null
    this._global_vectors = null
    this._axis = null
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

    let scales = new Scales(data, _.pick(this, ['outerWidth', 'outerHeight',
      'margin', 'chart_type', 'y_field']))
    this._scales = scales

    let svg = d3.select(parent)
      .append('svg')
      .attr('width', outerWidth)
      .attr('height', outerHeight)

    // Define filters for later use
    let defs = svg.append('defs')

    this._defineFilters(defs)

    // Zoom, brush and drag
    let zoomBeh = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', zoom)
      .on('end', zoomEnd)
    let dot_brush = new DotBrush(data, scales, emitter)

    // Blank
    let rect = svg.append('rect')
      .attr('width', scales.width())
      .attr('height', scales.height())
      .attr('fill', this.background)

    // Brush & Zoom
    svg.call(zoomBeh)
    toggleBrushing()

    // Object Container
    let objects = svg.append('svg')
      .classed('objects', true)
      .attr('width', scales.width())
      .attr('height', scales.height())

    // Halo Layer
    objects.append('g')
      .classed('halo_layer', true)

    // Dots
    this._dots = new Dots(scales, objects, _.pick(this, ['dot_color', 'dot_radius',
      'mark_type', 'outerWidth', 'outerHeight']))
    this._dots.draw(data, emitter, this.dispatch)

    // Axis
    this._axis = new DotAxis(objects, scales, _.pick(this, ['chart_type', 'y_field']))
    this._axis.draw()

    // Lines
    let vector_style = {background: this.background}
    if (!this._vectors) {
      this._vectors = new Vectors(scales, objects, this.dispatch, vector_style)
      this._vectors.hide = this.y_field !== 'y'
    } else {
      this._vectors.hide = this.y_field !== 'y'
      this._vectors._scales = scales
      this._vectors._parent = objects
      this._vectors.redraw()
    }

    // Multiple vectors in global projection
    if (!this._global_vectors) {
      this._global_vectors = new GlobalVectors(scales, objects, this.dispatch,
        vector_style)
    } else {
      this._global_vectors._scales = scales
      this._global_vectors._parent = objects
      this._global_vectors.redraw()
    }

    /**
     * =========================
     * Register event handlers for dispatcher, to communicate with outside.
     */
    this.dispatch.on('toggle-background', () => {
      rect.attr('fill', this.background)
    })

    this.dispatch.on('zoom-view', (factor) => {
      svg.call(zoomBeh.scaleBy, factor)
    })

    this.dispatch.on('toggle-brushing', () => {
      toggleBrushing()
    })

    this.dispatch.on('dot-center', (d) => {
      if (d) {
        centerPoint(d)
      }
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

    /**
     * @deprecated
     */
    function centerPoint (d) {
      let xc = scales.width() / 2 - scales.x(d._x)
      let yc = scales.height() / 2 - scales.y(d._y)

      let rangeX = scales.x.range().map((n) => n - xc)
      let rangeY = scales.y.range().map((n) => n - yc)

      scales.x = scales.x.copy().domain(rangeX.map(scales.x.invert))
      scales.y = scales.y.copy().domain(rangeY.map(scales.y.invert))

      // update dots
      that._dots.zoom()

      // clear brush
      dot_brush.clear()
    }

    function zoom () {
      // create new scales
      scales.x = d3.event.transform.rescaleX(scales.initialX)
      scales.y = d3.event.transform.rescaleY(scales.initialY)
      if (scales.y_band) {
        scales.y_band.range(scales.initialYBand.range().map((d) => d3.event.transform.applyY(d)))
      }

      // update dots and axis
      that._dots.zoom()
      that._axis.zoom()

      // update vectors
      that._vectors.redraw()
      that._global_vectors.redraw()

      // clear brush
      dot_brush.clear()
    }

    function zoomEnd () {
      // update dots
      that._dots.zoomEnd()
    }
  }
  
  _defineFilters (defs) {
    // Drop shadow
    let filter = defs.append('filter')
      .attr('id', 'shadow')
      .attr('height', '200%')

    filter.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', 1.7)
      .attr('result', 'blur')

    filter.append('feOffset')
      .attr('in', 'blur')
      .attr('dx', 0)
      .attr('dy', 0)
      .attr('result', 'offsetBlur')

    filter.append('feFlood')
      .attr('flood-color', '#3D4574')
      .attr('flood-opacity', '0.5')
      .attr('result', 'offsetColor')

    filter.append('feComposite')
      .attr('in', 'offsetColor')
      .attr('in2', 'offsetBlur')
      .attr('operator', 'in')
      .attr('result', 'offsetBlur')

    // Background behind text
    filter = defs.append('filter')
      .attr('id', 'text-bg')

    filter.append('feFlood')
      .attr('flood-color', '#fff')

    filter.append('feComposite')
      .attr('in', 'SourceGraphic')
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
   * Center around the point.
   * @param point
   */
  centerDot (point) {
    this.dispatch.call('dot-center', this, point)
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
    this.dispatch.call('toggle-background', this, color)
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
