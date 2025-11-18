// frontend/src/index.tsx
import './index.css';
import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import Main from './Main.tsx';

const container = document.getElementById('root')!; 


const root = createRoot(container);
root.render(
  <StrictMode>
    <Main />
  </StrictMode>
);