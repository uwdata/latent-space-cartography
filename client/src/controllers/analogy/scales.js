import * as d3 from 'd3'

/**
 * @fileOverview
 * Creates and holds all the scales in analogy scatter plot.
 */
class Scales {
  /**
   * Constructor
   * @param data
   * @param outerWidth
   * @param outerHeight
   * @param margin
   */
  constructor (data, outerWidth, outerHeight, margin) {
    /**
     * Width and height
     */
    this.outerWidth = outerWidth
    this.outerHeight = outerHeight
    this.margin = margin

    /**
     * Scales
     */
    this.initialX = null
    this.initialY = null

    this.x = null
    this.y = null

    /**
     * Initialize
     */
    this.init(data)
  }

  /**
   * Initialize: create the scales
   * @param data
   */
  init (data) {
    let x = d3.scaleLinear()
      .range([0, this.width()]).nice()

    let y = d3.scaleLinear()
      .range([this.height(), 0]).nice()

    let xMax = d3.max(data, (d) => d.x) * 1.05
    let xMin = d3.min(data, (d) => d.x) * 1.05
    let yMax = d3.max(data, (d) => d.y) * 1.05
    let yMin = d3.min(data, (d) => d.y) * 1.05

    x.domain([xMin, xMax])
    y.domain([yMin, yMax])

    this.x = x
    this.y = y
    this.initialX = x.copy()
    this.initialY = y.copy()
  }

  /**
   * A helper function to get the canvas width (outer minus margin)
   */
  width () {
    return this.outerWidth - this.margin.left - this.margin.right
  }

  /**
   * A helper function to get the canvas height (outer minus margin)
   */
  height () {
    return this.outerHeight - this.margin.top - this.margin.bottom
  }
}

export default Scales
