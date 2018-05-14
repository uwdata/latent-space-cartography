/**
 * Move D3 selection elements to the front.
 * @param selection
 */
function moveToFront (selection) {
  selection.each(function () {
    this.parentNode.appendChild(this)
  })
}

export {moveToFront}
