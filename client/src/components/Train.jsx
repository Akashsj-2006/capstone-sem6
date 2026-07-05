import { useState } from "react"
import axios from "axios"

function Train() {

  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)

  const handleUpload = async () => {

    const formData = new FormData()
    formData.append("file", file)

    const response = await axios.post(
      "http://localhost:5000/train",
      formData
    )

    setResult(response.data)
  }

  return (
    <div>
      <h2>Train Model</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>
        Train
      </button>

      {result && (
        <div>
          <h3>Training Result</h3>
          <p>Accuracy: {result.accuracy}</p>
        </div>
      )}

    </div>
  )
}

export default Train