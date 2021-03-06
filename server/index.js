const express = require("express");
const app = express();
const cors = require("cors");
const assert = require("assert");
const port = process.env.PORT || 5000;
app.use(cors());

var MongoClient = require("mongodb").MongoClient;
require("dotenv").config({path: ".env"});

const database = process.env.MONGO_URI || "test_uri";
MongoClient.connect(database, function (err, client) {
  if (process.env.DATABASE_HOST) {
    var dbHost = process.env.DATABASE_HOST;
  }
  assert.equal(null, err);
  app.locals.twitter = client.db("Twitter");
});

const searchRouter = require("./routes/search");
const authorRouter = require("./routes/author");
const threadRouter = require("./routes/thread");
const latestRouter = require("./routes/latest");

app.use("/search", searchRouter);
app.use("/author", authorRouter);
app.use("/thread", threadRouter);
app.use("/latest", latestRouter);

app.get("/", function (req, res) {
  res.send("Express Backend for Twitblog!");
});

app.listen(port, () => {
  console.log(`Server listening at port ${port}`);
});
