import { useContext, useEffect, useState } from 'react';

import '@sbb-esta/journey-maps/web-component';
import '@sbb-esta/journey-maps/web-component/styles.css';

import './trip.css';
import TripCard from '../../components/TripCard/tripCard';

import LocationContext from '../../context/LocationContext';
import { useLocation, useNavigate } from 'react-router-dom';
import request from '../../utils/request';

import colorTrip from '../../utils/colorTrip';

const Trip = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const coords = useContext(LocationContext);
    const [selectedTrip, setSelectedTrip] = useState(0);
    const [routePath, setRoutePath] = useState({});
    const [routeOptions, setRouteOptions] = useState({});
    const [trips, setTrips] = useState([]);

    var loadingIndicator = document.getElementsByClassName("loading-indicator");

    useEffect(() => {
        var client = document.createElement('sbb-journey-maps-wc');
        client.language = 'en';
        client.apiKey = '8ff1e3c393578b6463f8a24b6baf0fd6';

        // Pass object-type input parameter
        client.markerOptions = {
            markers: [
                {
                    id: 'Origin',
                    title: 'Your position',
                    position: trips[0] ? [trips[0].legs[0].start.coordinates[0], trips[0].legs[0].start.coordinates[1]] : coords,
                    category: 'NEUTRAL',
                },
                {
                    id: 'Destination',
                    title: 'Destination',
                    position: trips[0] ? [trips[0].legs[trips[0].legs.length - 1].end.coordinates[0], trips[0].legs[trips[0].legs.length - 1].end.coordinates[1]] : location.state.coordinates,
                    category: 'NEUTRAL',
                },
            ],
        };

        console.log(routePath);

        client.journeyMapsRoutingOption = {
            routes: routePath,
            routesMetaInformations: routeOptions,
        }

        // Register for event
        client.addEventListener('zoomLevelsChange', (event) =>
            console.log('Current zoom: ', event.detail.currentZoom)
        );
        
        document.getElementById('map').replaceChildren(client);
    }, [routePath]);

    useEffect(() => {
        let date = Math.floor(location.state.date/1000.0)
        request(`/trips/details/[${coords}]/[${location.state.coordinates}]/1000/1000/${date}/1/1/1`, "GET", "", (data) => {
            if (loadingIndicator.length > 0) 
                loadingIndicator[0].style.display = "none";
            console.log("data: ",data);
            console.log(data.trips);

            var best2_car = data.trips.filter((trip) => trip.legs[0].mode === "CAR").sort((a, b) => {
                let aDuration = a.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                let bDuration = b.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                return aDuration - bDuration;
            }).slice(0, 2);

            var best2_bikes = data.trips.filter((trip) => trip.legs[0].mode === "BIKE").sort((a, b) => {
                let aDuration = a.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                let bDuration = b.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                return aDuration - bDuration;
            }).slice(0, 2);

            var best10 = data.trips.sort((a, b) => {
                let aDuration = a.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                let bDuration = b.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                return aDuration - bDuration;
            }
            ).slice(0, 10);
            var final =[]

            var car_count = 0
            var bike_count = 0
            for (let i = 0; i < best10.length; i++) {
                if (best10[i].legs[0].mode === "CAR") {
                    car_count++
                } else if (best10[i].legs[0].mode === "BIKE") {                   
                    bike_count++
                } 
            }
            if (car_count < 2|| bike_count < 2) {
                for (let i = car_count; i < 2; i++) {
                    final.push(best2_car[i])
                }
                for (let i = bike_count; i < 2; i++) {
                    final.push(best2_bikes[i])
                }
            }
            for (let i = 0; i < best10.length; i++) {
                final.push(best10[i])
            }

            final = final.sort((a, b) => {
                let aDuration = a.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                let bDuration = b.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                return aDuration - bDuration;
            }
            );


            



            console.log("final: ", final)
            console.log(final)
            

            setTrips([ ...final ]);
        })
    }, []);

    useEffect(() => {
        if(trips.length > 0) getPath(0);
    }, [trips]);

    const getPath = (i) => {
        request(`/trace_path`, "POST", JSON.stringify(trips[i]), (data) => {
            const routeFromPath = data.map((item, index) => {
                return {
                    id: index.toString(),
                    isSelected: true,
                    type: 'FeatureCollection',
                    bbox: [6.6290796, 46.4899302, 7.4337461, 46.9520855],
                    features: [
                        {
                            type: 'Feature',
                            properties: {
                                station_from: {
                                  id: '8507000',
                                  latitude: 7.4391184769,
                                  longitude: 46.9488249864,
                                  name: 'Bern',
                                  platform: '',
                                  ident_source: 'sbb',
                                },
                                station_to: {
                                  id: '8504100',
                                  latitude: 7.1510364906,
                                  longitude: 46.8031416512,
                                  name: 'Fribourg/Freiburg',
                                  platform: '',
                                  ident_source: 'sbb',
                                },
                                external_node_id_to: '0874214b-bd22-4165-bd01-79fa80c206ab',
                                transportType: 'rail',
                                type: 'path',
                                pathType: 'transport',
                                external_node_id_from: '3e4c7bdc-9723-450a-bddc-4c2fca9bfdd3',
                                lines: [],
                              },
                          geometry: {
                            type: 'LineString',
                            coordinates: item.points
                          }
                        }
                    ]
                }
            })

            const routeOptionsFromPath = data.map((item, index) => {
                return {
                    id: index.toString(),
                    routeColor: colorTrip(item.mode),
                }
            })

            setRoutePath(routeFromPath);
            setRouteOptions(routeOptionsFromPath);
        })
    }

    return (
        <div className='trip-container'>
            <div className='trip-list'>
                <sbb-link variant="block" size="xs" icon-name="chevron-small-left-small" icon-placement="start" onClick={()=>navigate(-1)} type="button" name="Button name">Back</sbb-link>
                <sbb-title level="4" class="title-ride">Choose your ride</sbb-title>
                <div className='trip-list-container'>
                    {trips.map((trip, index) => {
                        const duration = trip.legs.reduce((acc, leg) => acc + parseInt(leg.duration), 0);
                        const carbon = trip.legs.reduce((acc, leg) => acc + parseInt(leg.co2g), 0);
                        const price = trip.legs.reduce((acc, leg) => acc + parseInt(leg.cost), 0);
                        const distance = trip.legs.reduce((acc, leg) => acc + parseInt(leg.distance), 0);

                        return (
                            <TripCard from={"Your position"} to={trip.legs[trip.legs.length - 1].end.name} time={duration} selected={selectedTrip === index} onClick={() => {getPath(index); setSelectedTrip(index)}} legs={trip.legs} price={price} carbon={carbon} distance={distance}/>
                        )
                    })}
                </div>
                    <sbb-loading-indicator
                        class="loading-indicator"
                        variant="window"
                        size="large"
                        color="default"
                    ></sbb-loading-indicator>
            </div>
            <div id='map' slot="map"></div>
        </div>
    );
}

export default Trip;