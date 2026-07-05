const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const trainRoute = require("./routes/trainRoute");
const predictRoute = require("./routes/predictRoute");

const app = express();

app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

const testSchema = new mongoose.Schema({
  name: String
});

const Test = mongoose.model("Test", testSchema);


app.use("/train", trainRoute);
app.use("/predict", predictRoute);

app.get("/",(req,res)=>{
    res.send("Backend running successfully");
})

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});