import { useState } from 'react';
import './tripCard.css'

const TripCard = ({from, to, time, selected = false, onClick, legs, carbon, price, distance}) => {
    const modes = new Set(legs.map((leg) => leg.mode))
    return (
        <div className={selected ? "selected" : ""}>
            <sbb-card size="xxxl" color="milk" class={`trip-item-card`} onClick={() => onClick()}>
                <div className="trip-card">
                    <p class="sbb-text-xs co-consumption">{carbon} g <sbb-icon name="cloud-co2-small"></sbb-icon></p>
                    <sbb-journey-header origin={from} destination={to} level="1" size="m"></sbb-journey-header>
                    <p class="sbb-text-s supplements">{distance} km | {Math.floor(time / 60)}h {time % 60}m | {price} CHF</p>
                    <sbb-pearl-chain-time class="timeline" arrival-time={new Date(legs[legs.length - 1].end.time * 1000).toISOString()} departure-time={new Date(legs[0].start.time * 1000).toISOString()} ></sbb-pearl-chain-time>
                    <div className="modes">
                        <sbb-icon name='bike-profile-power-plug-small' style={{display: modes.has('BIKE') ? 'contents' : 'none'}}></sbb-icon>
                        <sbb-icon name='car-small'  style={{display: modes.has('CAR') ? 'contents' : 'none'}}></sbb-icon>
                        <sbb-icon name='bus-sbb-small'  style={{display: modes.has('BUS') || modes.has('TRAIN') || modes.has('METRO') ? 'contents' : 'none'}}></sbb-icon>
                        <sbb-icon name='walk-small'  style={{display: modes.has('FOOT') ? 'contents' : 'none'}}></sbb-icon>
                    </div>
                </div>
            </sbb-card>
        </div>
     );
}
 
export default TripCard;