import * as d3 from 'd3'
import _ from 'lodash'
import {moveToFront} from './util'

const NEIGHBOR_BIN = [0, 10, 100, 500]

class Vectors {
  constructor (scales, parent) {
    this.lineWidth = 2

    /**
     * Private
     */
    this._scales = scales
    this._parent = parent
  }

  drawOne (vector, name = 'v-main') {
    let scales = this._scales
    let img_size = 20
    let img_padding = 10
    let chart_height = img_size + img_padding + 5

    let line = d3.line()
      .x((d) => scales.x(d.x))
      .y((d) => scales.y(d.y))

    // group
    let group = this._parent.append('g')
      .classed(name, true)
      .on('mouseover', () => {moveToFront(group)})

    // background
    this._drawLine(line, vector, group)
      .style('stroke', '#ffffff')
      .style('stroke-opacity', 0.8)
      .style('stroke-linecap', 'round')
      .style('stroke-width', chart_height * 2)

    // draw lines with different textures
    _.each(NEIGHBOR_BIN, (num, j) => {
      let bin = _.filter(vector, (d) => d.neighbors > num)
      let path = this._drawLine(line, bin, group)
      this._styleTexture(path, j)
    })

    // area chart
    let yy = d3.scaleLinear()
      .range([0, chart_height])
      .domain([0, d3.max(vector, (d) => d.neighbors)])
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

  clearByName (name) {
    this._parent.selectAll(`.${name}`)
      .remove()
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
