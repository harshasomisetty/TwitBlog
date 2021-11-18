import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
const axios = require("axios");

export default function Author() {
  const [search, setSearch] = useState({ searchTerm: "" });
  let params = useParams();

  useEffect(() => {
    const url = "http://localhost:5000/author/" + params.authorName;
    console.log(url);
    axios
      .get(url)
      .then((res) => setSearch({ searchTerm: res.data.title }))
      .catch(function (error) {
        console.log(error);
      })
      .then(function () {
        console.log("api call done");
      });

    console.log(search);
  }, []);
  return <p> {search.searchTerm} </p>;
}