import { useState } from "react"
import axios from "axios"

function PredictPage(){

  const [file,setFile] = useState(null)
  const [predictions,setPredictions] = useState([])
  const [actual,setActual] = useState([])
  const [accuracy,setAccuracy] = useState(null)

  const predict = async () => {

    const formData = new FormData()
    formData.append("file",file)

    try{

      const res = await axios.post(
        "http://localhost:5000/predict",
        formData
      )

      setPredictions(res.data.predictions)

      // NEW: handle actual labels
      if(res.data.actual){
        setActual(res.data.actual)
      } else {
        setActual([])
      }

      // NEW: handle accuracy
      if(res.data.accuracy){
        setAccuracy(res.data.accuracy)
      } else {
        setAccuracy(null)
      }

    }catch(err){
      console.error(err)
    }
  }

  return(

    <div className="page">

      <h1>EGG Classifier - Predict</h1>

      <p>(Upload EGG feature dataset)</p>

      <input type="file"
        onChange={(e)=>setFile(e.target.files[0])}
      />

      <button onClick={predict}>Analyze</button>

      {/* SHOW ACCURACY */}
      {accuracy !== null && (
        <h3 style={{marginTop:"20px"}}>
          Accuracy: {accuracy.toFixed(3)}
        </h3>
      )}

      {predictions.length > 0 && (

        <div className="results">

          <h3>Prediction Results</h3>

          {predictions.map((p,i)=>(

            <div key={i} className="result-card">

              Sample {i+1} : 
              <b> Pred = {p}</b>

              {actual.length > 0 && (
                <>
                  {" | "} 
                  Actual = <b>{actual[i]}</b>

                  {" "}
                  {p === actual[i] ? "🟢" : "🔴"}
                </>
              )}

            </div>

          ))}

        </div>

      )}

    </div>

  )

}

export default PredictPage