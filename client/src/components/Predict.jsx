import { useState } from "react"
import axios from "axios"

function Predict() {

  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)

  const handleUpload = async () => {

    const formData = new FormData()
    formData.append("file", file)

    const response = await axios.post("https://egg-classifier.onrender.com/predict", formData)

    setResult(response.data)
  }

  return (
    <div>
      <h2>Test / Predict</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>
        Predict
      </button>

      {result && (
        <div>
          <h3>Prediction</h3>
          <pre>{JSON.stringify(result.predictions, null, 2)}</pre>
        </div>
      )}

    </div>
  )
}

export default Predict