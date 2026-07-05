import { Link } from "react-router-dom"

function Navbar() {
  return (
    <div className="navbar">

      <div className="logo">
        EGG Classifier
      </div>

      <div className="nav-links">
        <Link to="/">Predict</Link>
        <Link to="/train">Train Model</Link>
      </div>

    </div>
  )
}

export default Navbar