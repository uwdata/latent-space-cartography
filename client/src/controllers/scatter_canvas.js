import * as d3 from 'd3'
import _ from 'lodash'

const width = 800
const height = 500

const synthetic = _.map(_.range(100), (i) => {
  return {x: _.random(width), y: _.random(height), index: i}
})

/**
 * Entry point.
 */
function draw (parent) {
  let canvas = d3.select(parent)
    .append('canvas')
    .attr('width', width)
    .attr('height', height)

  let ctx = canvas.node().getContext('2d')

  // create the hidden DOM ...
  let customDom = document.createElement('custom')
  let custom = d3.select(customDom)

  // bind data
  bindData(synthetic, custom)

  // Render
  redraw(ctx, custom)
}

/**
 * Enter a redraw loop until duration is reached
 * @param ctx
 * @param custom
 * @param duration
 */
function redraw (ctx, custom, duration = 500) {
  let t = d3.timer((elapsed) => {
    console.log('render')
    render (ctx, custom)

    if (elapsed > duration) {
      t.stop()
    }
  })
}

/**
 * All data manipulation goes here.
 * @param data
 * @param custom
 */
function bindData (data, custom) {
  let join = custom.selectAll('custom.dot').data(data)

  // Enter ...
  join.enter()
    .append('custom')
    .attr('class', 'dot')
    .attr('x', (d) => d.x)
    .attr('y', (d) => d.y)
    .attr('radius', 5)
}

/**
 * Draw things on the canvas exactly once.
 * @param ctx
 * @param custom
 */
function render (ctx, custom) {
  // clear canvas
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, width, height)

  // draw each element
  let elements = custom.selectAll('custom.dot')

  elements.each(function () {
    let node = d3.select(this)
    let r = node.attr('radius')
    ctx.fillStyle = '#000'
    ctx.fillRect(node.attr('x'), node.attr('y'), r, r)
  })
}

export {draw}
