import * as dotenv from "dotenv";
dotenv.config();

import express from "express";
import { mongoConnect } from "./mongoConnect";

mongoConnect()
  .then(() => {
    const app = express();

    // Invoke the express.json() middleware
    app.use(express.json());

    app.get("/", (req, res) => res.send("Hi"));

    const PORT = 4000;

    app.listen(PORT, () => console.log("listening on port", PORT));
  })
  .catch((error: any) => {
    console.error("Unable to connect to the database", error);
  });
