import React, { useState } from "react";

function App() {
  const [form, setForm] = useState({
    patient_name: "",
    medication_name: "",
    diagnosis: "",
    provider_name: "",
    patient_records: "",
  });
  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setOrder(null);

    // 同步调用：这里会"卡"住 10-20 秒，直到后端返回结果
    const res = await fetch("http://localhost:8000/api/orders/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await res.json();

    setOrder(data);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Care Plan Generator (MVP)</h1>

      <form onSubmit={handleSubmit}>
        <input name="patient_name" placeholder="Patient Name" onChange={handleChange} /><br />
        <input name="medication_name" placeholder="Medication Name" onChange={handleChange} /><br />
        <input name="diagnosis" placeholder="Primary Diagnosis (ICD-10)" onChange={handleChange} /><br />
        <input name="provider_name" placeholder="Referring Provider" onChange={handleChange} /><br />
        <textarea name="patient_records" placeholder="Patient Records" onChange={handleChange} /><br />
        <button type="submit" disabled={loading}>
          {loading ? "Generating... (请等待)" : "Submit"}
        </button>
      </form>

      {/* 只有 completed 状态才显示 care plan —— 这是需求文档里的规则 */}
      {order && order.status === "completed" && (
        <div>
          <h2>Care Plan</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>{order.care_plan}</pre>
        </div>
      )}

      {order && order.status === "failed" && (
        <p style={{ color: "red" }}>生成失败，请重试</p>
      )}
    </div>
  );
}

export default App;