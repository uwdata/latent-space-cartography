import * as d3 from 'd3'
import _ from 'lodash'
import {store} from '../../controllers/config'
import {moveToFront} from './util'

/**
 * @fileOverview
 * Drawing and interaction of the scatter plot dots (and their labels).
 */
class Dots {
  /**
   * Constructor
   * @param scales
   * @param parent
   * @param radius
   * @param mark_type
   * @param color
   */
  constructor (scales, parent, radius, color, mark_type) {
    /**
     * Styling
     */
    this.radius = radius
    this.color = color
    this.mark_type = mark_type

    /**
     * Communicate with parent
     */
    this._parent = parent
    this._scales = scales
    this._data = []
  }

  /**
   * Draw the dots and define interaction.
   * @param data
   * @param emitter
   * @param dispatch
   */
  draw (data, emitter, dispatch) {
    this._data = data
    let scales = this._scales
    let parent = this._parent
    let that = this

    let inside = this._isInsideView(data)
    let mark_type = inside.length > 500 ? 1 : 2

    if (mark_type === 1) {
      parent.selectAll('.dot')
        .data(data)
        .enter()
        .append('circle')
        .classed('dot', true)
        .attr('r', () => this.radius)
        .attr('cx', (d) => scales.x(d.x))
        .attr('cy', (d) => scales.y(d.y))
        .style('fill', (d) => this._colorDot(d, scales.palette))
        .on('click', dotClick)
        .on('mouseover', dotMouseover)
        .on('mouseout', dotMouseout)
    } else if (mark_type === 2) {
      let img_size = this._computeImageSize(inside)

      // draw logos directly
      parent
        .append('g')
        .classed('mark-img-group', true)
        .selectAll('.mark-img')
        .data(data)
        .enter()
        .append('image')
        .classed('mark-img', true)
        .attr('x', (d) => scales.x(d.x) - img_size * 0.5)
        .attr('y', (d) => scales.y(d.y) - img_size * 0.5)
        .attr('width', () => img_size)
        .attr('height', () => img_size)
        .attr('xlink:href', (d) => store.getImageUrl(d.i))
        .on('click', dotClick)
        .on('mouseover', imgMouseOver)
        .on('mouseout', imgMouseOut)
    }

    function dotMouseover(d) {
      that._focusDot(d, d3.select(this), true)
      // emitter.onDotHovered(d, scales.x(d.x), scales.y(d. y))
      emitter.onDotHovered(d, d3.event.clientX, d3.event.clientY)
    }

    function dotMouseout () {
      that._unfocusDot()
      emitter.onDotHovered(null)
    }

    function imgMouseOver (d) {
      emitter.onDotHovered(d, d3.event.clientX, d3.event.clientY)
    }

    function imgMouseOut () {
      emitter.onDotHovered(null)
    }

    function dotClick (d) {
      emitter.onDotClicked(d)
    }


    this._registerCallbacks(dispatch)
  }

  /**
   * Zooming callback.
   */
  zoom () {
    let scales = this._scales
    this._parent.selectAll('.dot')
      .attr('cx', (d) => scales.x(d.x))
      .attr('cy', (d) => scales.y(d.y))
    this._parent.selectAll('.halo')
      .attr('cx', (d) => scales.x(d.x))
      .attr('cy', (d) => scales.y(d.y))
    this._positionText(this._parent.selectAll('text'))

    let img = this._parent.select('.mark-img')

    if (!img.empty()) {
      let img_size = img.attr('width')
      this._parent.selectAll('.mark-img')
        .attr('x', (d) => scales.x(d.x) - img_size * 0.5)
        .attr('y', (d) => scales.y(d.y) - img_size * 0.5)
    }
  }

  /**
   * Zoom end callback.
   */
  zoomEnd () {
    let img = this._parent.select('.mark-img')
    if (img.empty()) {
      return
    }

    let inside = this._isInsideView(this._data)
    let img_size = this._computeImageSize(inside)
    let prev_size = img.attr('width')

    // alleviate jitter
    if (Math.abs(img_size - prev_size) > 2) {
      let t = this._parent.transition().duration(200)

      this._parent.selectAll('.mark-img').transition(t)
        .attr('x', (d) => this._scales.x(d.x) - img_size * 0.5)
        .attr('y', (d) => this._scales.y(d.y) - img_size * 0.5)
        .attr('width', () => img_size)
        .attr('height', () => img_size)
    }
  }

  /**
   * Register callbacks to the shared dispatcher, so dots can respond to outside events.
   * @param dispatch
   * @private
   */
  _registerCallbacks (dispatch) {
    dispatch.on('dot-focus-one', (p) => {
      if (!p) {
        this._unfocusDot()
      } else {
        this._focusDot(p, d3.selectAll('.dot').filter((d) => d.i === p.i))
      }
    })

    dispatch.on('dot-focus-set', (points) => {
      if (points) {
        this._focusSet(points)
      } else {
        this._unfocusSet()
      }
    })
  }

  /**
   * Compute optimal image size based on # of images in view and their bounding box.
   * @param inside
   * @returns {number} Size in pixels.
   * @private
   */
  _computeImageSize (inside) {
    let x = [d3.min(inside, (d) => d.x), d3.max(inside, (d) => d.x)]
    let y = [d3.min(inside, (d) => d.y), d3.max(inside, (d) => d.y)]
    x = _.map(x, (d) => this._scales.x(d))
    y = _.map(y, (d) => this._scales.y(d))

    let view_size = Math.min(Math.abs(x[0] - x[1]), Math.abs(y[0] - y[1]))
    let img_size = Math.floor(view_size * 0.5 / Math.sqrt(inside.length))
    img_size = _.clamp(img_size, 4, 26)

    return img_size
  }

  /**
   * Get the points inside view.
   * @param data
   * @private
   */
  _isInsideView (data) {
    let scales = this._scales

    let x = _.sortBy([scales.x.invert(0), scales.x.invert(scales.width())])
    let y = _.sortBy([scales.y.invert(0), scales.y.invert(scales.height())])

    return _.filter(data, (p) => p.x >= x[0] && p.x <= x[1] && p.y >=y[0] && p.y <= y[1])
  }

  /**
   * Draw a halo in the background layer around a dot.
   * @param d Object The data point.
   * @private
   */
  _drawHalo (d) {
    let layer = this._parent.select('.halo_layer')
    if (!d) {
      layer.selectAll('.halo').remove()
    } else {
      layer.selectAll('.halo')
        .data([d])
        .enter()
        .append('circle')
        .classed('halo', true)
        .attr('r', () => 20)
        .attr('cx', (d) => this._scales.x(d.x))
        .attr('cy', (d) => this._scales.y(d.y))
        .style('fill', () => '#ebdef3')
    }
  }

  /**
   * Focus one dot.
   * @param d
   * @param dot
   * @param minimal Boolean Whether we'll use elaborate strategy to draw attention.
   * @private
   */
  _focusDot (d, dot, minimal) {
    dot.attr('r', () => this.radius * 2)
      .classed('focused', true)
    moveToFront(dot)

    if (!minimal) {
      this._drawHalo(d)
    }

    if (!minimal) {
      let t = this._parent.selectAll('.focus-label')
        .data([d])
        .enter()
        .append('text')
        .classed('focus-label', true)
        .text((dd) => dd.name)
      this._positionText(t)
    }
  }

  _positionText (text) {
    text
      .attr('x', (d) => Math.max(this._scales.x(d.x) - 30, 15))
      .attr('y', (d) => Math.max(this._scales.y(d.y) - 15, 15))
  }

  /**
   * Remove the focus on one dot.
   * @private
   */
  _unfocusDot () {
    this._drawHalo()
    d3.selectAll('.dot.focused').attr('r', this.radius)
    d3.selectAll('.focus-label:not(.focused-set)').remove()
    d3.selectAll('.focus-label').classed('focus-label', false)
  }

  /**
   * Focus a set of dots.
   * @param pts
   * @private
   */
  _focusSet (pts) {
    let indices = {}
    _.each(pts, (pt) => indices[pt.i] = true)

    let grapes = d3.selectAll('.dot')
      .filter((d) => indices[d.i])
      .classed('focused-set', true)
    moveToFront(grapes)

    d3.selectAll('.dot')
      .filter((d) => !indices[d.i])
      .style('fill', (d) => '#ccc')
  }

  /**
   * Remove the focus on a set of dots.
   * @private
   */
  _unfocusSet () {
    d3.selectAll('.dot')
      .style('fill', (d) => this._colorDot(d, this._scales.palette))
    d3.selectAll('.dot.focused-set').attr('r', this.radius)
  }

  /**
   * Given a D3 datum, color it according to the current color attribute.
   * @param d
   * @param palette
   * @returns {*}
   * @private
   */
  _colorDot (d, palette) {
    let c = this.color

    if (c === 'mean_color') {
      return d['mean_color']
    } else if (c === 'industry' || c === 'source') {
      return palette(d[c])
    }

    return '#9467bd'
  }
}

export default Dots
