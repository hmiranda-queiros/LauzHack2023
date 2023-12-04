import { createContext } from 'react';

const DateContext = createContext(Date.now());

export default DateContext;