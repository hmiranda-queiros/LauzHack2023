import './home.css'
import illustration from '../../assets/undraw_travel_booking_re_6umu.svg'
import { useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from 'react';

import request from '../../utils/request';

const Home = () => {
    const navigate = useNavigate();
    const refDate = useRef();
    const refHour = useRef();
    const [value, setValue] = useState()
    const [locationObj, setLocationObj] = useState({})
    const [autocomplete, setAutocomplete] = useState([])

    useEffect(() => {
        console.log(value);
        if (value && value !== "") {
            setAutocomplete([]);
            request(`/places/${value}/5`, "GET", "", (data) => {
                console.log(data);
                setAutocomplete(data);
            })
        } else {
            setAutocomplete([]);
        }
    }, [value]);

    useEffect(() => {
        console.log(locationObj);
    }, [locationObj]);

    const goToPrompt = () => {
        navigate("suggestions", { state: { value: value, date: changeTime() } });
    }

    const goToTrip = () => {
        if (Object.hasOwn(locationObj, "id")) {
            navigate("route", { state: { ...locationObj, date: changeTime() }});
        } else {
            goToPrompt();
        }
    }

    const changeTime = () => {
        const dateVal = refDate.current.value;
        const hour = refHour.current.value;
        console.log(dateVal);
        console.log(hour);
        // Tu, 12.12.2023
        // regex to split dateVal to day, month, year
        var regex = /(\d{2})\.(\d{2})\.(\d{4})/;
        // regex to split hour to hour, minute
        var regex2 = /(\d{2}):(\d{2})/;

        var dateArray = regex.exec(dateVal);
        var hourArray = regex2.exec(hour);
        console.log(dateArray);
        console.log(hourArray);
        // create date object
        let date = new Date(dateArray[3], dateArray[2]-1, dateArray[1], hourArray[1], hourArray[2]);
        console.log(date);
        return date.getTime();
    }

    return (
        <div className="page-center main-container">
            <img src={illustration} alt="SBB" className="main-image" />
            <sbb-title level="1" class="main-title text-center">Plan your trip easily</sbb-title>
            <sbb-title level="4" class="main-subtitle text-center">Tell us where you want to go</sbb-title>
            <div class="main-field">
                <sbb-form-field error-space="none" size="l" class="main-field-custom">
                    <input placeholder="Where do you want to go?" onChange={(e) => { setValue(e.target.value); setLocationObj({}) }}></input>
                    <sbb-autocomplete>
                        <sbb-optgroup label="Suggestions">
                            {autocomplete.map((item) => {
                                console.log(item.name);
                                return (<sbb-option icon-name="city-small" value={item.name} onClick={() => setLocationObj(item)}>{item.name}</sbb-option>)
                            })}
                        </sbb-optgroup>
                        <sbb-optgroup>
                            <sbb-option icon-name="globe-locomotive-small" onClick={() => goToPrompt()}>Inspire me with destinations</sbb-option>
                        </sbb-optgroup>
                    </sbb-autocomplete>
                </sbb-form-field>
                <sbb-button variant="primary" size="l" icon-name="arrow-right-small" type="button" name="Button Name" onClick={() => goToTrip()}></sbb-button>
            </div>
            <div className='secondary-field'>
                <sbb-form-field><input ref={refDate}/><sbb-datepicker></sbb-datepicker><sbb-datepicker-toggle data-testid="toggle"></sbb-datepicker-toggle></sbb-form-field>
                <sbb-form-field size="m" width="collapse">
                    <sbb-icon slot="prefix" name="clock-small"></sbb-icon>
                    <sbb-time-input>
                    </sbb-time-input>
                    <input id="input-id" placeholder='hh:mm' style={{marginRight: 20}} ref={refHour}>
                    </input>
                </sbb-form-field>
            </div>
            <p class="sbb-text-s main-instructions">You can enter a city, an address, or describe a place you want to go to.</p>
            <div class="credits">
                <p class="sbb-text-xxs">@LauzHack 2023 - With Help of</p>
                <sbb-logo protective-room="ideal" style={{ width: 150 }}></sbb-logo>
            </div>
        </div>
    );
}

export default Home;