import React, { useEffect } from 'react';
import { createContext } from 'react';
import '@sbb-esta/lyne-components/dist/lyne-components/lyne-components.css';
import './css/fonts.css';
import './App.css';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

// Pages
import Home from './pages/home/Home';
import Places from './pages/places/Places';
import Trip from './pages/trip/Trip';

import LocationContext from './context/LocationContext';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/suggestions",
    element: <Places />,
  },
  {
    path: "/route",
    element: <Trip />,
  },
]);

function App() {
  const [location, setLocation] = React.useState([6.6322734, 46.5196535]);

  useEffect(() => {
    if(navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        console.log(position.coords.longitude, position.coords.latitude);
        setLocation([position.coords.longitude, position.coords.latitude]);
      });
    } else {
      console.log("Geolocation is not supported by this browser.");
    }
  }, []);

  return (
    <LocationContext.Provider value={location}>
      <RouterProvider router={router} />
    </LocationContext.Provider>
  );
}

export default App;