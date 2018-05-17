import * as d3 from 'd3'
import _ from 'lodash'
import {moveToFront} from './util'

const NEIGHBOR_BIN = [0, 10, 100, 500]
const MAX_NEIGHBORS = 1000

class Vectors {
  constructor (scales, parent, dispatch, styles = {}) {
    /**
     * Public
     */
    this.lineWidth = styles.lineWidth || 2
    this.background = styles.background || '#fff'

    /**
     * Private
     */
    this._scales = scales
    this._parent = parent
    this._dispatch = dispatch

    this._max_neighbors = MAX_NEIGHBORS

    /**
     * Initialization
     */
    this._registerCallback()
  }

  drawOne (vector, main = false) {
    let scales = this._scales
    let img_size = 20
    let img_padding = 10
    let chart_height = img_size + img_padding + 5

    let line = d3.line()
      .x((d) => scales.x(d.x))
      .y((d) => scales.y(d.y))

    // group
    let group = this._parent.append('g')
      .datum(vector) // so we can retrieve later
      .classed('vector-group', true)
      .on('mouseover', () => {moveToFront(group)})

    // background
    this._drawLine(line, vector, group)
      .classed('vector-background', true)
      .style('stroke', this.background)
      .style('stroke-opacity', 0.8)
      .style('stroke-linecap', 'round')
      .style('stroke-width', chart_height * 2)

    // draw lines with different textures
    _.each(NEIGHBOR_BIN, (num, j) => {
      let bin = _.filter(vector, (d) => d.neighbors >= num)
      let path = this._drawLine(line, bin, group)
      this._styleTexture(path, j)
    })

    // area chart
    if (main) {
      this._max_neighbors = Math.max(d3.max(vector, (d) => d.neighbors), MAX_NEIGHBORS)
    }
    let yy = d3.scaleLinear()
      .range([0, chart_height])
      .domain([0, this._max_neighbors])
    let area = d3.area()
      .x((d) => scales.x(d.x))
      .y0((d) => scales.y(d.y) + 1)
      .y1((d) => scales.y(d.y) + yy(d.neighbors))
    group.append('path')
      .datum(vector)
      .classed('nb-area', true)
      .attr('d', area)
      .style('fill', '#eee')
      .style('opacity', 0.8)

    // connector
    let link = d3.linkVertical()
      .source((d) => [scales.x(d.x), scales.y(d.y) + yy(d.neighbors)])
      .target((d) => [scales.x(d.x), scales.y(d.y) - img_padding])

    group.selectAll('.vector-connector')
      .data(vector)
      .enter()
      .append('path')
      .classed('vector-connector', true)
      .attr('d', link)
      .on('mouseover', _focusLoc)
      .on('mouseout', _unfocusLoc)

    // dot at each sampled location
    group.selectAll('.vector-dot')
      .data(vector)
      .enter()
      .append('circle')
      .classed('vector-dot', true)
      .attr('r', 3)
      .attr('cx', (d) => scales.x(d.x))
      .attr('cy', (d) => scales.y(d.y))
      .style('fill', '#fff')
      .style('stroke', (d) => d.neighbors > NEIGHBOR_BIN[3] ? '#222' : '#888')
      .style('stroke-width', 2)
      .on('mouseover', _focusLoc)
      .on('mouseout', _unfocusLoc)

    // images
    let images = group.selectAll('.vector-img')
      .data(vector)
      .enter()
      .append('image')
      .classed('vector-img', true)
      .attr('xlink:href', (d) => `/build/${d.image}`)
      .on('mouseover', _focusLoc)
      .on('mouseout', _unfocusLoc)
    _styleImage(images, img_size, img_padding)

    function _focusLoc (which) {
      match('.vector-dot', which).classed('focused', true)
      match('.vector-connector', which).classed('focused', true)
      // _styleImage(match('.vector-img', which), 64, img_padding)
    }

    function _unfocusLoc (which) {
      match('.vector-dot', which).classed('focused', false)
      match('.vector-connector', which).classed('focused', false)
      // _styleImage(match('.vector-img', which), img_size, img_padding)
    }

    function _styleImage(img, size, padding) {
      return img
        .attr('x', (d) => scales.x(d.x) - size * 0.5)
        .attr('y', (d) => scales.y(d.y) - size - padding)
        .attr('width', () => size)
        .attr('height', () => size)
    }
  }

  /**
   * Redraw everything (e.g. because scale is updated)
   */
  redraw () {
    let vectors = []
    d3.selectAll('.vector-group')
      .each((vector) => {
        vectors.push(vector)
      })
      .remove()

    _.each(vectors, (vector) => this.drawOne(vector))
  }

  /**
   * Remove a vector with matching data.
   * @param vector
   */
  removeOne (vector) {
    // FIXME: d may be undefined
    d3.selectAll('.vector-group')
      .filter((d) => d[0].x === vector[0].x && d[0].y === vector[0].y)
      .remove()
  }

  /**
   * Register callbacks to dispatcher.
   * @private
   */
  _registerCallback () {
    this._dispatch.on('toggle-background.vector', (color) => {
      this.background = color
      d3.selectAll('.vector-background')
        .style('stroke', color)
    })
  }

  /**
   * Style an SVG path according to the category
   * @param path
   * @param category
   * @private
   */
  _styleTexture (path, category) {
    switch (category) {
      case 0:
        return path
          .style('stroke', '#aaa')
          .style('stroke-dasharray', '4, 4')
          .style('stroke-width', 1)
      case 1:
        return path
          .style('stroke', '#888')
          .style('stroke-dasharray', '4, 4')
          .style('stroke-width', this.lineWidth)
      case 2:
        return path
          .style('stroke', '#888')
          .style('stroke-width', this.lineWidth)
      case 3:
        return path
          .style('stroke', '#222')
          .style('stroke-width', this.lineWidth)
    }
  }

  _drawLine (line, vector, container) {
    return container.append('path')
      .datum(vector)
      .classed('line', true)
      .attr('d', line)
  }
}

function match (name, which) {
  return d3.selectAll(name)
    .filter((d) => d.x === which.x && d.y === which.y)
}

export default Vectors
