import * as d3 from 'd3'
import _ from 'lodash'
import {store} from '../controllers/config'

/**
 * Move D3 selection elements to the front.
 * @param selection
 */
function moveToFront (selection) {
  selection.each(function () {
    this.parentNode.appendChild(this)
  })
}

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
    this.hover = true
    this.dispatch = d3.dispatch(
      'focus-one',
      'focus-set',
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
    this.onSelected = () => {}
    this.onProbed = () => {}
    this.onDotClicked = () => {}
    this.onDotHovered = () => {}
  }

  /**
   * Entry point.
   * @param parent
   */
  draw (parent) {
    let outerWidth = this.outerWidth
    let outerHeight = this.outerHeight
    let margin = this.margin
    let width = outerWidth - margin.left - margin.right
    let height = outerHeight - margin.top - margin.bottom
    let that = this

    let data = this.data

    let x = d3.scaleLinear()
      .range([0, width]).nice()

    let y = d3.scaleLinear()
      .range([height, 0]).nice()

    let currentX = x
    let currentY = y

    let palette = d3.scaleOrdinal(d3.schemeCategory10)

    let xMax = d3.max(data, (d) => d.x) * 1.05
    let xMin = d3.min(data, (d) => d.x) * 1.05
    let yMax = d3.max(data, (d) => d.y) * 1.05
    let yMin = d3.min(data, (d) => d.y) * 1.05

    x.domain([xMin, xMax])
    y.domain([yMin, yMax])

    let svg = d3.select(parent)
      .append("svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)

    // Zoom, brush and drag
    let zoomBeh = d3.zoom()
      .scaleExtent([0.5, 3])
      .on("zoom", zoom)
    let brushBeh = d3.brush()
      .on('start', brushstart)
      .on('brush', brushing)
      .on("end", brushended)

    svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    // Blank
    let rect = svg.append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", this.background)

    // Brush & Zoom
    rect.call(zoomBeh)
    toggleBrushing()

    // Object Container
    let objects = svg.append("svg")
      .classed("objects", true)
      .attr("width", width)
      .attr("height", height)

    // Dots
    if (this.mark_type === 1) {
      let dots = objects.selectAll(".dot")
        .data(data)
        .enter()
        .append("circle")
        .classed("dot", true)
        .attr('r', () => this.dot_radius)
        .attr('cx', (d) => x(d.x))
        .attr('cy', (d) => y(d.y))
        .style("fill", (d) => this._colorDot(d, palette))
        .on('click', dotClick)

      if (this.hover) {
        dots.on('mouseover', dotMouseover)
          .on('mouseout', dotMouseout)
      }
    } else if (this.mark_type === 2) {
      let img_size = 20

      // draw logos directly
      objects.selectAll(".mark-img")
        .data(data)
        .enter()
        .append("image")
        .classed("mark-img", true)
        .attr('x', (d) => x(d.x) - img_size * 0.5)
        .attr('y', (d) => y(d.y) - img_size * 0.5)
        .attr('width', () => img_size)
        .attr('height', () => img_size)
        .attr('xlink:href', (d) => store.getImageUrl(d.i))
        .on('click', dotClick)
    }

    /**
     * =========================
     * Register event handlers for dispatcher, to communicate with outside.
     */
    this.dispatch.on('focus-one.dot', (p) => {
      if (!p) {
        unfocusDot()
      } else {
        focusDot(p, d3.selectAll('.dot').filter((d) => d.i === p.i))
      }
    })

    this.dispatch.on('focus-set.dot', (points) => {
      if (points) {
        focusSet(points)
      } else {
        unfocusSet()
      }
    })

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
    function focusDot (d, dot, hideText) {
      dot.attr('r', () => that.dot_radius * 2)
        .classed('focused', true)
      moveToFront(dot)

      if (!hideText) {
        let t = null
        d3.selectAll('text')
          .each(function () {
            // really ugly hack because text has no binding data
            if (d3.select(this).text() === d.name) {
              t = d3.select(this)
            }
          })
        if (!t) {
          objects.append('text')
            .attr('x', () => Math.max(currentX(d.x) - 30, 15))
            .attr('y', () => Math.max(currentY(d.y) - 15, 15))
            .classed('focus-label', true)
            .text(() => d.name)
        } else {
          t.classed('focus-label', true)
        }
      }
    }

    function unfocusDot () {
      d3.selectAll('.dot.focused').attr('r', that.dot_radius)
      d3.selectAll('.focus-label:not(.focused-set)').remove()
      d3.selectAll('.focus-label').classed('focus-label', false)
    }

    function focusSet (pts) {
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

    function unfocusSet () {
      d3.selectAll('.dot')
        .style("fill", (d) => that._colorDot(d, palette))
      d3.selectAll('.dot.focused-set').attr('r', that.dot_radius)
    }

    function dotMouseover(d) {
      focusDot(d, d3.select(this), true)
      that.onDotHovered(d, currentX(d.x), currentY(d. y))
    }

    function dotMouseout () {
      unfocusDot()
      that.onDotHovered(null)
    }

    function dotClick (d) {
      that.onDotClicked(d)
    }

    function toggleBrushing () {
      if (that.mode_brush) {
        // create brush that is on top of everything
        svg.append('g').attr('class', 'brush').call(brushBeh)
      } else {
        // remove brush
        d3.selectAll('.brush')
          .call(brushBeh.move, null)
          .remove()
      }
    }

    function brushstart() {
      d3.selectAll('.dot').classed('muted', false)
      that.onSelected([])
    }

    function brushing () {
      // empty selection
      if (!d3.event.selection) return

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let scales = _.map(sel, (s, idx) => idx % 2 ? currentY.invert(s) : currentX.invert(s))

      // change color of selected points
      d3.selectAll('.dot')
        .classed('muted', (p) => {
          let inside = p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
          return !inside
        })
    }

    function brushended () {
      // empty selection
      if (!d3.event.selection) return

      // x0, y0, x1, y1
      let sel = _.flatten(d3.event.selection)
      let scales = _.map(sel, (s, idx) => idx % 2 ? currentY.invert(s) : currentX.invert(s))

      let pts = _.filter(data, (p) => {
        return p.x >= scales[0] && p.x <= scales[2] && p.y >= scales[3] && p.y <=scales[1]
      })

      that.onSelected(pts)
    }

    function zoom () {
      // create new scales
      currentX = d3.event.transform.rescaleX(x)
      currentY = d3.event.transform.rescaleY(y)

      // update dots
      svg.selectAll(".dot")
        .attr('cx', (d) => currentX(d.x))
        .attr('cy', (d) => currentY(d.y))

      // clear brush
      d3.select('.brush').call(brushBeh.move, null)
    }
  }

  /**
   * Given a D3 datum, color it according to the current color attribute.
   * @param d
   * @param palette
   * @returns {*}
   * @private
   */
  _colorDot (d, palette) {
    let c = this.dot_color

    if (c === 'mean_color') {
      return d['mean_color']
    } else if (c === 'industry' || c === 'source') {
      return palette(d[c])
    }

    return '#9467bd'
  }

  /**
   * Focus one dot (when mouse hovering on top of it, for example)
   * @param point
   */
  focusDot (point) {
    this.dispatch.call('focus-one', this, point)
  }

  focusSet (points) {
    this.dispatch.call('focus-set', this, points)
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
