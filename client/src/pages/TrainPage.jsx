import { useState } from "react"
import axios from "axios"

function TrainPage() {

  const [file,setFile] = useState(null)
  const [result,setResult] = useState(null)

  const trainModel = async () => {

    const formData = new FormData()
    formData.append("file",file)

    const res = await axios.post("https://egg-classifier.onrender.com/train", formData)

    setResult(res.data)

  }

  return (

    <div className="page">

      <h1>EGG Classifier - Train</h1>

      <p>(Upload labelled dataset to train classifier)</p>

      <input type="file"
        onChange={(e)=>setFile(e.target.files[0])}
      />

      <button onClick={trainModel}>Train Model</button>

      {result && (

        <div className="result">

          <h3>Training Complete</h3>

        </div>

      )}

    </div>

  )

}

export default TrainPage