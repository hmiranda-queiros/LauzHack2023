import { useContext, useEffect, useRef, useState } from "react";
import "./places.css";
import { useLocation } from "react-router-dom";
import PlaceCard from "../../components/PlaceCard/placeCard";
import illustration from "../../assets/undraw_location_search_re_ttoj.svg";

import LocationContext from "../../context/LocationContext";

const Places = () => {
  let location = useLocation();
  const coords = useContext(LocationContext);

  const [prompt, setPrompt] = useState(location.state.value ?? "");
  const [inputField, setInputField] = useState(location.state.value ?? "");
  const [places, setPlaces] = useState([]);
  const date = location.state.date;

  var loadingIndicator = document.getElementsByClassName("loading-indicator");

  var noPrompt = document.getElementsByClassName("no_prompt");

  useEffect(() => {
    if (window.localStorage.getItem("prompt/{" + prompt + "}") != null) {
      setPlaces(
        JSON.parse(window.localStorage.getItem("prompt/{" + prompt + "}"))
      );
      loadingIndicator[0].style.display = "none";
      noPrompt[0].style.display = "none";
    }
  }, []);

  useEffect(() => {
    if (prompt && prompt !== "") {
      if (window.localStorage.getItem("prompt/{" + prompt + "}") != null) {
        return;
      }
      // call api
      console.log("calling api");
      console.log(prompt);
      // remove all place cards from htmlCollection
      var placeContainer = document.getElementsByClassName(
        "places-card-container"
      );

      console.log(placeContainer);
      setPlaces([]);
      loadingIndicator[0].style.display = "block";
      noPrompt[0].style.display = "none";
      var link = "/suggest/" + prompt;
      if (coords) {
        console.log(coords);
        link += "/" + coords[0] + "/" + coords[1];
      }

      fetch(link).then((response) => {
        response.json().then((data) => {
          // data is a list of json. for each of them, create a place card and add it to the htmlCollection
          console.log(data);
          setPlaces(data);
          window.localStorage.setItem(
            "prompt/{" + prompt + "}",
            JSON.stringify(data)
          );
          // hide loading indicator
          loadingIndicator[0].style.display = "none";
        });
      });
    } else {
      loadingIndicator[0].style.display = "none";
      setPlaces([]);
    }
  }, [prompt]);

  return (
    <div className="page-center places-container">
      <sbb-link
        variant="block"
        size="xs"
        icon-name="chevron-small-left-small"
        icon-placement="start"
        href="/"
        type="button"
        name="Button name"
        class="backButton"
      >
        Back
      </sbb-link>
      <sbb-title level="3" class="places-title text-center">
        Find the perfect location in Switzerland
      </sbb-title>
      <div class="places-field">
        <sbb-form-field error-space="none" size="l" class="main-field-custom">
          <input
            placeholder="Where do you want to go?"
            onChange={(e) => setInputField(e.target.value)}
            value={inputField}
          ></input>
        </sbb-form-field>
        <sbb-button
          variant="primary"
          size="l"
          icon-name="magnifying-glass-small"
          type="button"
          name="Button Name"
          onClick={() => setPrompt(inputField)}
        ></sbb-button>
      </div>
      <sbb-loading-indicator
        class="loading-indicator"
        variant="window"
        size="large"
        color="default"
        display="none"
      ></sbb-loading-indicator>

      <div class="no_prompt">
        <img src={illustration} alt="SBB" class="main-image" />
        <p class="sbb-text-s no_prompt">
          Please describe a place you want to go to.
        </p>
      </div>

      <div className="places-card-container">
        {places.map((place) => (
          <PlaceCard
            name={place.name}
            description={place.description}
            image={place.image}
            location={place.address}
            date={date}
            coordinates={place.coordinates}
          />
        ))}
      </div>
      <div class="credits">
        <p class="sbb-text-xxs">@LauzHack 2023 - With Help of</p>
        <sbb-logo protective-room="ideal" style={{ width: 150 }}></sbb-logo>
      </div>
    </div>
  );
};

export default Places;
