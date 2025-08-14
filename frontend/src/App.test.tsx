import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders chat placeholder', () => {
    render(<App />)
    expect(screen.getByText(/Chat placeholder/i)).toBeInTheDocument()
  })
})


