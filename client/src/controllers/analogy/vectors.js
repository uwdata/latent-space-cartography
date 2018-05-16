import * as d3 from 'd3'
import _ from 'lodash'

const NEIGHBOR_BIN = [0, 10, 100, 500]

class Vectors {
  constructor (scales, parent) {
    /**
     * Private
     */
    this._scales = scales
    this._parent = parent
  }

  drawOne (vector) {
    let scales = this._scales

    let line = d3.line()
      .x((d) => scales.x(d.x))
      .y((d) => scales.y(d.y))

    // background
    this._drawLine(line, vector)
      .style('stroke', '#fff')
      .style('stroke-linecap', 'round')
      .style('stroke-width', 20)

    // draw lines with different textures
    _.each(NEIGHBOR_BIN, (num, j) => {
      let bin = _.filter(vector, (d) => d.neighbors > num)
      let path = this._drawLine(line, bin)
      this._styleTexture(path, j)
    })
  }

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
          .style('stroke-width', 4)
      case 2:
        return path
          .style('stroke', '#888')
          .style('stroke-width', 4)
      case 3:
        return path
          .style('stroke', '#222')
          .style('stroke-width', 4)
    }
  }

  _drawLine (line, vector) {
    return this._parent.append('path')
      .datum(vector)
      .classed('line', true)
      .attr('d', line)
  }
}

export default Vectors
