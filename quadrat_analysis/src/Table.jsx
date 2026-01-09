import { useEffect, useState } from "react";

export default function Table() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    // display the table containing all sites run previously
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/quadrat-data");
                const json = await res.json();
                setData(json.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <p>Loading... <i>The model is currently running. Please wait a few minutes to view the table.</i></p>;
    if (!data.length) return <p>No data available</p>;

    const columns = Object.keys(data[0]);

    return (
        <div className="table-wrapper">
            <table className="data-table">
                <thead>
                <tr>
                    {columns.map(col => (
                        <th key={col}>{col}</th>
                    ))}
                </tr>
                </thead>
                <tbody>
                {data.map((row, idx) => (
                    <tr key={idx}>
                        {columns.map(col => (
                            <td key={col}>{row[col]}</td>
                        ))}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}