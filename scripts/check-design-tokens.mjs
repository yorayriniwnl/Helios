import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const tokenPath = resolve(process.cwd(), 'design/yor-tokens.json')
const tokens = JSON.parse(await readFile(tokenPath, 'utf8'))
const requiredColors = {
  void: '#000000',
  panel: '#050505',
  crimson: '#e84b4b',
  deepCrimson: '#671515',
  signal: '#ff8a7f',
  paper: '#f5eaea',
  muted: '#c4c4c4',
}

for (const [key, expected] of Object.entries(requiredColors)) {
  if (tokens.color?.[key]?.toLowerCase() !== expected) {
    throw new Error(`design/yor-tokens.json color.${key} must be ${expected}`)
  }
}

if (!Array.isArray(tokens.signal?.states) || tokens.signal.states.join(',') !== 'BOOT,ACQUIRE,TRANSMIT,LOCK,FAULT,IDLE') {
  throw new Error('design/yor-tokens.json signal states are out of contract')
}

console.log(`YOR token contract valid: ${tokenPath}`)
