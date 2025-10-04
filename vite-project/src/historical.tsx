import React from "react";

export default function Historical() {
  return (
    <div style={{ padding: "2rem" }}>
      <h1>Historical Data</h1>
      <p>This is the Historical Data page.</p>

      <a href="/">
        <button
          style={{
            marginTop: "1rem",
            padding: "10px 20px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Back to Home
        </button>
      </a>
    </div>
  );
}
