import * as d3 from 'd3'

/**
 * A heatmap showing arbitrary vector value, e.g. gene expression profile.
 */
class Heatmap {
  constructor () {
    /**
     * Public, styles
     */
    this.outerWidth = 300
    this.outerHeight = 0
    this.radius = 3
    this.background = '#fff'

    /**
     * Private
     * @private
     */
    this._color_scale = null
    this._ctx = null
    this._custom = null
    this._parent = null

    /**
     * Data
     */
    this.data = []
  }

  /**
   * Entry point
   * @param parent
   */
  draw (parent) {
    this._parent = parent
    this.clearData()

    // compute height
    let r = this.radius
    this.outerHeight = this.data.length * r * r / this.outerWidth

    // create a canvas
    let canvas = d3.select(parent)
      .append('canvas')
      .attr('width', this.outerWidth)
      .attr('height', this.outerHeight)

    let ctx = canvas.node().getContext('2d')

    // create the hidden DOM ...
    let customDom = document.createElement('custom')
    let custom = d3.select(customDom)

    this._ctx = ctx
    this._custom = custom

    // binding data to element
    this.bindData()

    // drawing the elements
    this.render()
  }

  /**
   * Remove previous drawing
   */
  clearData () {
    if (this._custom) {
      let node = this._custom.node()
      while (node.firstChild) {
        node.removeChild(node.firstChild)
      }
      node.remove()
      this._custom = null
    }
    if (this._ctx && this._parent) {
      let node = d3.select(this._parent).node()
      while (node.firstChild) {
        node.removeChild(node.firstChild)
      }
      this._ctx = null
    }
  }

  /**
   * Create the virtual DOM
   */
  bindData () {
    // create scale
    let d_max = d3.max(this.data, (d) => d.value)
    let d_min = d3.min(this.data, (d) => d.value)
    this._color_scale = d3.scaleSequential(d3.interpolateInferno)
      .domain([d_min, d_max])

    let r = this.radius
    let n_row = Math.floor(this.outerWidth / this.radius)
    this._custom.selectAll('custom.square').data(this.data)
      .enter()
      .append('custom')
      .attr('class', 'square')
      .attr('x', (d) => (d.i % n_row) * r)
      .attr('y', (d) => Math.floor(d.i / n_row) * r)
      .attr('radius', () => this.radius)
      .attr('color', (d) => this._color_scale(d.value))
      .exit().remove()
  }

  /**
   * Actually render the virtual DOM to canvas
   */
  render () {
    let ctx = this._ctx

    // clear canvas
    ctx.fillStyle = this.background
    ctx.fillRect(0, 0, this.outerWidth, this.outerHeight)

    // draw each element
    let elements = this._custom.selectAll('custom.square')

    elements.each(function () {
      let node = d3.select(this)
      let r = node.attr('radius')
      ctx.fillStyle = node.attr('color')
      ctx.fillRect(node.attr('x'), node.attr('y'), r, r)
    })
  }

  /**
   * Change data
   * @param data
   */
  setData (data) {
    this.data = data
  }
}

export default Heatmap
