import {render, screen} from '@testing-library/react';
import App from './App';

test('render app', () => {
  render(<App />);
  const linkElement = screen.getByText(/ink/i);
  expect(linkElement).toBeInTheDocument();
});
