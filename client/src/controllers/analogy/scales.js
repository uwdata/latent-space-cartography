import * as d3 from 'd3'
import _ from 'lodash'

/**
 * @fileOverview
 * Creates and holds the shared scales in analogy scatter plot.
 */
class Scales {
  /**
   * Constructor
   * @param data
   * @param params
   */
  constructor (data, params) {
    /**
     * Public parameters
     */
    this.outerWidth = params.outerWidth
    this.outerHeight = params.outerHeight
    this.margin = params.margin
    this.chart_type = params.chart_type
    this.y_field = params.y_field

    /**
     * Scales
     */
    this.initialX = null
    this.initialY = null

    this.x = null
    this.y = null

    // categorical y scale for strip chart
    // note that this might remain null
    this.y_band = null
    this.initialYBand = null

    /**
     * Initialize
     */
    this.init(data)
  }

  /**
   * Initialize the scales for scatter plot
   * @param data
   * @private
   */
  _initScatterScales (data) {
    // create x and y plotting fields so we can unify the code
    for (let i = 0; i < data.length; i++) {
      data[i]._x = data[i].x
      data[i]._y = data[i][this.y_field]
    }

    // create the scales
    let x = d3.scaleLinear()
      .range([0, this.width()]).nice()

    let y = d3.scaleLinear()
      .range([this.height(), 0]).nice()

    let xMax = d3.max(data, (d) => d._x) * 1.05
    let xMin = d3.min(data, (d) => d._x) * 1.05
    let yMax = d3.max(data, (d) => d._y) * 1.05
    let yMin = d3.min(data, (d) => d._y) * 1.05

    x.domain([xMin, xMax])
    y.domain([yMin, yMax])

    this.x = x
    this.y = y
  }

  /**
   * Initialize the scales for bee swarm plots
   * @param data
   * @private
   */
  _initSwarmScales (data) {
    // make a "identity" y scale for interfacing purpose
    this.y = d3.scaleLinear()
      .range([0, this.height()])
      .domain([0, this.height()])

    // x is still a continuous scale
    this.x = d3.scaleLinear()
      .range([0, this.width()]).nice()
      .domain(d3.extent(data, (d) => d.x))

    // y scale for drawing, which maps category to height
    let y = d3.scaleBand().rangeRound([0, this.height()]).padding(0.1)
      .domain(data.map((d) => d[this.y_field]))
    this.y_band = y
    this.initialYBand = y.copy()

    let max_bw = 80
    if (y.bandwidth() > max_bw) {
      let h = max_bw * y.domain().length
      let h0 = (this.height() - h) * 0.5
      y.rangeRound([h0, h0 + h])
    }

    // add random offsets to y position
    for (let i = 0; i < data.length; i++) {
      data[i]._x = data[i].x
      data[i]._y = y(data[i][this.y_field]) + _.random(0, y.bandwidth(), true)
    }
  }

  /**
   * Initialize: create the scales
   * @param data
   */
  init (data) {
    if (this.chart_type === 1) {
      this._initScatterScales(data)
    } else {
      this._initSwarmScales(data)
    }

    this.initialX = this.x.copy()
    this.initialY = this.y.copy()
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
