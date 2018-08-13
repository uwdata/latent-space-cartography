import * as d3 from 'd3'
import _ from 'lodash'
import {store} from '../../controllers/config'
import {moveToFront, tableau10, tableau20} from './util'

/**
 * @fileOverview
 * Drawing and interaction of the scatter plot dots (and their labels).
 */
class Dots {
  /**
   * Constructor
   * @param scales
   * @param parent
   * @param style
   */
  constructor (scales, parent, style) {
    /**
     * Styling
     */
    this.radius = style.dot_radius
    this.color = style.dot_color
    this.mark_type = style.mark_type
    this.parent_width = style.outerWidth
    this.parent_height = style.outerHeight

    /**
     * Communicate with parent
     */
    this._parent = parent
    this._scales = scales
    this._data = []

    /**
     * State data
     */
    this.hull = []

    /**
     * Other private properties
     */
    this.need_legend = false
    this.palette = null
  }

  /**
   * Draw the dots and define interaction.
   * @param data
   * @param emitter
   * @param dispatch
   */
  draw (data, emitter, dispatch) {
    this._data = data
    this.hull = []
    let scales = this._scales
    let parent = this._parent
    let that = this

    let inside = this._isInsideView(data)
    let mark_type = inside.length > 500 ? 1 : this.mark_type

    this._createPalette(data)
    if (mark_type === 1) {
      parent
        .append('g')
        .classed('dot-group', true)
        .selectAll('.dot')
        .data(data)
        .enter()
        .append('circle')
        .classed('dot', true)
        .attr('r', () => this.radius)
        .attr('cx', (d) => scales.x(d._x))
        .attr('cy', (d) => scales.y(d._y))
        .style('fill', (d) => this._colorDot(d))
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
        .attr('x', (d) => scales.x(d._x) - img_size * 0.5)
        .attr('y', (d) => scales.y(d._y) - img_size * 0.5)
        .attr('width', () => img_size)
        .attr('height', () => img_size)
        .attr('xlink:href', (d) => store.getImageUrl(d.i))
        .on('click', dotClick)
        .on('mouseover', imgMouseOver)
        .on('mouseout', imgMouseOut)
    } else if (mark_type === 3) {
      let font_size = 12

      // draw text
      let t = parent
        .selectAll('.dot-text')
        .data(data)
        .enter()
        .append('text')
        .classed('dot-text', true)
        .text((d) => d.name)
        .style('font-size', () => `${font_size}px`)
        .style('filter', 'url(#text-bg)')

      this._positionText(t, font_size)
    }

    // draw color legend
    if (this.need_legend) {
      this._drawColorLegend(parent)
    }

    function dotMouseover(d) {
      that._focusDot(d, d3.select(this), true)
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
      .attr('cx', (d) => scales.x(d._x))
      .attr('cy', (d) => scales.y(d._y))
    this._parent.selectAll('.halo')
      .attr('cx', (d) => scales.x(d._x))
      .attr('cy', (d) => scales.y(d._y))
    this._positionTextLabel(this._parent.selectAll('.focus-label'))
    this._positionText(this._parent.selectAll('.dot-text'))

    let img = this._parent.select('.mark-img')

    if (!img.empty()) {
      let img_size = img.attr('width')
      this._parent.selectAll('.mark-img')
        .attr('x', (d) => scales.x(d._x) - img_size * 0.5)
        .attr('y', (d) => scales.y(d._y) - img_size * 0.5)
    }

    this._drawHull()
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
        .attr('x', (d) => this._scales.x(d._x) - img_size * 0.5)
        .attr('y', (d) => this._scales.y(d._y) - img_size * 0.5)
        .attr('width', () => img_size)
        .attr('height', () => img_size)
    }
  }

  /**
   * Draw a legend for the categorical palette.
   * @param parent
   * @private
   */
  _drawColorLegend (parent) {
    // prepare data
    let names = this.palette.domain()
    let data = []
    for (let i = 0; i < names.length; i++) {
      data.push({'i': i, 'name': names[i], 'color': this.palette(names[i])})
    }
    let title = _.capitalize(this.color.split('_').join(' '))

    // calculate width and height
    const ver_padding = 15
    const hor_paddding = 10
    const inner_padding = 10
    const mark_size = 4
    const font_size = 10

    // find the longest word
    let max = 0
    _.each(names.concat([title]), (name) => {
      max = Math.max(max, name.length)
    })

    // assuming vertical layout
    let width = hor_paddding * 3 + inner_padding + mark_size + font_size * max * 0.5
    let height = ver_padding * 2 + font_size * names.length

    // we want to place the legend in lower right
    let x0 = this.parent_width - width
    let y0 = this.parent_height - height

    // background
    let bg = parent.append('g')
      .attr('class', 'color-legend')
      .attr('transform', `translate(${x0},${y0})`)

    bg
      .append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', '#fff')

    // title
    bg.append('text')
      .text(title)
      .attr('x', hor_paddding)
      .attr('y', ver_padding)
      .style('font-weight', '500')
      .style('font-size', `${font_size}px`)

    // the mark
    bg.selectAll('.legend-mark')
      .data(data)
      .enter()
      .append('circle')
      .classed('legend-mark', true)
      .attr('r', () => mark_size)
      .attr('cx', () => hor_paddding + mark_size)
      .attr('cy', (d) => ver_padding * 2 + d.i * font_size - mark_size)
      .style('fill', (d) => d.color)

    // the text
    bg.selectAll('.legend-label')
      .data(data)
      .enter()
      .append('text')
      .classed('legend-label', true)
      .text((d) => {
        let name = d.name || 'Unknown'
        return _.toUpper(name[0]) + name.substr(1)
      })
      .attr('x', () => hor_paddding + mark_size + inner_padding)
      .attr('y', (d) => ver_padding * 2 + d.i * font_size)
      .style('font-size', () => font_size + 'px')
      .attr('fill', '#343a40')
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
    let x = [d3.min(inside, (d) => d._x), d3.max(inside, (d) => d._x)]
    let y = [d3.min(inside, (d) => d._y), d3.max(inside, (d) => d._y)]
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

    return _.filter(data, (p) => p._x >= x[0] && p._x <= x[1] && p._y >=y[0] && p._y <= y[1])
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
        .attr('cx', (d) => this._scales.x(d._x))
        .attr('cy', (d) => this._scales.y(d._y))
        .style('fill', () => '#ebdef3')
    }
  }

  _drawHull () {
    let layer = this._parent.select('.halo_layer')
    let pts = this.hull

    layer.selectAll('.hull').remove()

    if (pts && pts.length) {
      let vertices = _.map(pts, (p) => [this._scales.x(p._x), this._scales.y(p._y)])
      layer.append('path')
        .attr('class', 'hull')
        .datum(d3.polygonHull(vertices))
        .attr('d', (d) => 'M' + d.join('L') + 'Z')
        .attr('stroke-linejoin', 'round')
        .attr('stroke-width', '20px')
        .attr('stroke', '#ebdef3')
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
      this._positionTextLabel(t)
    }
  }

  _positionText (text, font_size = 12) {
    let font_width = font_size * 0.45

    text
      .attr('x', (d) => this._scales.x(d._x) - font_width * d.name.length * 0.5)
      .attr('y', (d) => this._scales.y(d._y))
  }

  _positionTextLabel (text) {
    text
      .attr('x', (d) => Math.max(this._scales.x(d._x) - 30, 15))
      .attr('y', (d) => Math.max(this._scales.y(d._y) - 15, 15))
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
      .style('fill', () => '#ccc')

    this.hull = pts
    this._drawHull()
  }

  /**
   * Remove the focus on a set of dots.
   * @private
   */
  _unfocusSet () {
    this.hull = []
    this._drawHull()
    d3.selectAll('.dot')
      .style('fill', (d) => this._colorDot(d))
    d3.selectAll('.dot.focused-set').attr('r', this.radius)
  }

  /**
   * Decide which palette to use.
   * @param data
   * @private
   */
  _createPalette (data) {
    if (this.color && this.color !== 'mean_color') {
      let values = _.uniqBy(data, (d) => d[this.color])

      if (values.length > 10) {
        this.palette = d3.scaleOrdinal(tableau20)
      } else {
        this.palette = d3.scaleOrdinal(tableau10)
      }
    }
  }

  /**
   * Given a D3 datum, color it according to the current color attribute.
   * @param d
   * @returns {*}
   * @private
   */
  _colorDot (d) {
    let c = this.color

    if (c === 'mean_color') {
      return d['mean_color']
    } else if (c) {
      this.need_legend = true
      return this.palette(d[c])
    }

    return '#9467bd'
  }
}

export default Dots
