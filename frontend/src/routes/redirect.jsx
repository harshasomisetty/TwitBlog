import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { positions } from "react-alert";
import { useAlert } from "react-alert";
import Loading from "../components/Loading.js";
/*
 * This function always redirects the base url to /home
 * Needed because Router calls base first, and /home is another location
 */
export default function Redir({ text = "" }) {
  const navigate = useNavigate();
  const alert = useAlert();

  function RedirAlert() {
    alert.error(text, {
      timeout: 4000,
      offset: "100px",
      position: positions.TOP_CENTER,
      containerStyle: {
        zIndex: 100,
        width: 160,
      },
    });
  }

  if (text) {
    RedirAlert();
  }

  useEffect(() => {
    setTimeout(() => {
      navigate("/home");
    }, 0);
    // eslint-disable-next-line
  }, []);

  return <Loading />;
}
