import resolve from 'rollup-plugin-node-resolve'

export default [{
  input: 'index.js',
  output: {
    file: './build/scatter.js',
    format: 'umd',
    name: 'scatter' // this is the moduleName
  },
  plugins: [ resolve() ]
}]
