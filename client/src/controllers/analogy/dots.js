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
    this.active_category = null // for interactive legend
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
        .attr('cx', (d) => scales.getX(d))
        .attr('cy', (d) => scales.getY(d))
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
        .attr('x', (d) => scales.getX(d) - img_size * 0.5)
        .attr('y', (d) => scales.getY(d) - img_size * 0.5)
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
      let shift = d3.event.shiftKey
      emitter.onDotClicked(d, shift)
    }

    this._registerCallbacks(dispatch)
  }

  /**
   * Zooming callback.
   */
  zoom () {
    let scales = this._scales
    this._parent.selectAll('.dot')
      .attr('cx', (d) => scales.getX(d))
      .attr('cy', (d) => scales.getY(d))
    this._parent.selectAll('.halo')
      .attr('cx', (d) => scales.getX(d))
      .attr('cy', (d) => scales.getY(d))
    this._positionTextLabel(this._parent.selectAll('.focus-label'))
    this._positionText(this._parent.selectAll('.dot-text'))

    let img = this._parent.select('.mark-img')

    if (!img.empty()) {
      let img_size = img.attr('width')
      this._parent.selectAll('.mark-img')
        .attr('x', (d) => scales.getX(d) - img_size * 0.5)
        .attr('y', (d) => scales.getY(d) - img_size * 0.5)
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
        .attr('x', (d) => this._scales.getX(d) - img_size * 0.5)
        .attr('y', (d) => this._scales.getY(d) - img_size * 0.5)
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
      .on('click', legendUnclick)
      .on('dblclick', stopped)

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
      .on('click', legendClick)
      .on('dblclick', stopped)

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
      .on('click', legendClick)
      .on('dblclick', stopped)

    let that = this

    function legendClick(d) {
      d3.event.stopPropagation()
      if (!d || d.name === that.active_category) {
        that.active_category = null
        that._unfocusSet()
      } else {
        that.active_category = d.name
        let active = _.filter(that._data, (dd) => dd[that.color] === d.name)
        that._focusSet(active, false)
      }
      that._styleLegend()
    }
    
    function legendUnclick() {
      d3.event.stopPropagation()
      that.active_category = null
      that._styleLegend()
      that._unfocusSet()
    }

    // intercept the double click to zoom event
    function stopped () {
      d3.event.stopPropagation()
    }
  }

  /**
   * Change the legend style in reaction to events
   * @private
   */
  _styleLegend () {
    let bg = this._parent.select('.color-legend')

    if (this.active_category !== null) {
      bg.selectAll('.legend-mark')
        .filter((d) => d.name !== this.active_category)
        .classed('muted', true)

      bg.selectAll('.legend-label')
        .filter((d) => d.name !== this.active_category)
        .classed('muted', true)

      bg.selectAll('.legend-mark')
        .filter((d) => d.name === this.active_category)
        .classed('muted', false)

      bg.selectAll('.legend-label')
        .filter((d) => d.name === this.active_category)
        .classed('muted', false)
    } else {
      bg.selectAll('.legend-mark')
        .classed('muted', false)

      bg.selectAll('.legend-label')
        .classed('muted', false)
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
      // focus-set and interactive legend are in conflicts
      this.active_category = null
      this._styleLegend()

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
    let scales = this._scales
    let x = [d3.min(inside, (d) => scales.getRawX(d)), d3.max(inside, (d) => scales.getRawX(d))]
    let y = [d3.min(inside, (d) => scales.getRawY(d)), d3.max(inside, (d) => scales.getRawY(d))]
    x = _.map(x, (d) => scales.x(d))
    y = _.map(y, (d) => scales.y(d))

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

    return _.filter(data, (p) => scales.getRawX(p) >= x[0] &&
      scales.getRawX(p) <= x[1] && scales.getRawY(p) >=y[0] && scales.getRawY(p) <= y[1])
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
        .attr('cx', (d) => this._scales.getX(d))
        .attr('cy', (d) => this._scales.getY(d))
        .style('fill', () => '#ebdef3')
    }
  }

  _drawHull () {
    let layer = this._parent.select('.halo_layer')
    let pts = this.hull

    layer.selectAll('.hull').remove()

    if (pts && pts.length) {
      let vertices = _.map(pts, (p) => [this._scales.getX(p), this._scales.getY(p)])
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
      .attr('x', (d) => this._scales.getX(d) - font_width * d.name.length * 0.5)
      .attr('y', (d) => this._scales.getY(d))
  }

  _positionTextLabel (text) {
    text
      .attr('x', (d) => Math.max(this._scales.getX(d) - 30, 15))
      .attr('y', (d) => Math.max(this._scales.getY(d) - 15, 15))
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
   * @param show_hull
   * @private
   */
  _focusSet (pts, show_hull = true) {
    let indices = {}
    _.each(pts, (pt) => indices[pt.i] = true)

    let grapes = d3.selectAll('.dot')
      .filter((d) => indices[d.i])
      .classed('focused-set', true)
      .style('fill', (d) => this._colorDot(d))
    moveToFront(grapes)

    d3.selectAll('.dot')
      .filter((d) => !indices[d.i])
      .style('fill', () => '#ccc')

    if (show_hull) {
      this.hull = pts
      this._drawHull()
    }
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
