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
 * Helper function to chop string into a proper array of hex codes.
 * @param specifier
 * @returns {Array}
 */
function colors (specifier) {
  let n = specifier.length / 6 | 0
  let c = new Array(n)
  let i = 0
  while (i < n) {
    c[i] = "#" + specifier.slice(i * 6, ++i * 6);
  }
  return c;
}

/**
 * Tableau categorical color palette of 10 categories
 */
const tableau10 = colors(
  '4c78a8f58518e4575672b7b254a24beeca3bb279a2ff9da69d755dbab0ac'
)

/**
 * Tableau categorical color palette of 20 categories
 */
const tableau20 = colors(
  '4c78a89ecae9f58518ffbf7954a24b88d27ab79a20f2cf5b43989483bcb6e45756ff9d9879706ebab0acd67195fcbfd2b279a2d6a5c99e765fd8b5a5'
)

export {
  moveToFront,
  tableau10,
  tableau20
}
