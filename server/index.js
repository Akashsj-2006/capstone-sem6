const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const trainRoute = require("./routes/trainRoute");
const predictRoute = require("./routes/predictRoute");

const app = express();

app.use(cors());
app.use(express.json());

mongoose.connect("mongodb://127.0.0.1:27017/classifier_db")
.then(()=>console.log("MongoDB connected"))
.catch(err=>console.log(err));


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