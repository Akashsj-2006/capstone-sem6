const express = require("express");
const multer = require("multer");
const path = require("path");
const { exec } = require("child_process");
const Result = require("../models/Result");

const router = express.Router();

/* STORAGE CONFIG */

const storage = multer.diskStorage({
  destination: "uploads/",
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const upload = multer({ storage });

/* ROUTE */

router.post("/", upload.single("file"), (req, res) => {

  const filePath = req.file.path;

  exec(`python ml/test.py ${filePath}`, async (error, stdout, stderr) => {

    if (error) {
      console.log("ERROR:", stderr);
      return res.status(500).json({ error: "Prediction failed" });
    }

    try {
      const result = JSON.parse(stdout);

      console.log("Parsed Result:", result);  // debug

      /* 🔥 SAVE TO MONGODB */

      if (result.accuracy !== undefined) {
        await Result.create({
          fileName: req.file.originalname,
          accuracy: result.accuracy
        });

        console.log("Saved to DB ✅");
      } else {
        console.log("⚠️ No accuracy found");
      }

      res.json(result);

    } catch (err) {
      console.log("JSON Parse Error:", err);
      res.status(500).json({ error: "Invalid response from Python" });
    }

  });

});

module.exports = router;