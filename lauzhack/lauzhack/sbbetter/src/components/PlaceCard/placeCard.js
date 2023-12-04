import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './placeCard.css'

const PlaceCard = ({name, description, image, coordinates, date}) => {
    const navigate = useNavigate();

    const goToTrips = () => {
        console.log("go to trips");
        navigate("../route", {state: {name: name, coordinates: coordinates, date: date}});
    }

    return (
        <sbb-card size="xxxl" color="milk">
            <div className="place-card">
                <div className='place-infos'>
                    <sbb-title level="4" className="place-infos-title">{name}</sbb-title>
                    <span class="sbb-text-m">{description}</span>
                    <sbb-link variant="block" size="m" icon-name="chevron-small-right-small" icon-placement="end" type="button" name="Button name" onClick={() => goToTrips()}>Travel  there</sbb-link>
                </div>
                <img src={image} alt={name} className="place-image"/>
            </div>
        </sbb-card>
     );
}
 
export default PlaceCard;