import {useEffect, useRef, useState} from "react";
import './App.css'
import { RotatingLines } from "react-loader-spinner";
import Table from "./Table.jsx";

export default function MainPage() {
    const canvasRef = useRef(null);
    const imgRef = useRef(null);
    const [image, setImage] = useState(null);
    const [points, setPoints] = useState([]);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

    // load image
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setDone(false);

        const img = new Image();
        img.onload = () => {
            imgRef.current = img;
            setImage(file);
            setPoints([]);
        };
        img.src = URL.createObjectURL(file);
    };

    // draw canvas image and points
    const drawCanvas = (img, pts) => {
        const canvas = canvasRef.current;
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        // draw points
        ctx.fillStyle = "red";
        pts.forEach(([x, y]) => {
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
        });
    };

    const undoDot = () => {
        setPoints(prev => {
            const newPoints = prev.slice(0, -1); // remove last
            redrawCanvas(newPoints);
            return newPoints;
        });
    };

    const redrawCanvas = (pointsArray) => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (imgRef.current) {
            ctx.drawImage(imgRef.current, 0, 0);
        }

        // draw points
        ctx.fillStyle = "red";
        pointsArray.forEach(([x, y]) => {
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
        });
    };

    // handle click
    const handleCanvasClick = (e) => {
        if (!imgRef.current || points.length >= 4) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();

        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const x = Math.round((e.clientX - rect.left) * scaleX);
        const y = Math.round((e.clientY - rect.top) * scaleY);

        const newPoints = [...points, [x, y]];
        setPoints(newPoints);
        drawCanvas(imgRef.current, newPoints);
    };

    // submit to backend
    const submit = async () => {
        if (points.length !== 4) {
            alert("Please place exactly 4 red dots.");
            return;
        }

        setLoading(true);

        const form = new FormData();
        form.append("image", image);
        form.append("points", JSON.stringify(points));
        form.append("name", image.name)

        try {
            const res = await fetch("http://localhost:8000/crop-quadrat", {
                method: "POST",
                body: form,
            });

            if (!res.ok) throw new Error("Server error");

            const data = await res.json();
            setResult({
                cropped: "data:image/png;base64," + data.cropped_image,
                context: "data:image/png;base64," + data.context_image,
                results: data.ai_result,
            });
        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(false);
            setDone(true);
        }
    };

    // run whenever image or points change
    useEffect(() => {
        if (!image || !imgRef.current) return;
        if (!canvasRef.current) return;

        drawCanvas(imgRef.current, points);
    }, [image, points]);

    return (
        <div className="page">
            <div className="card">
                <h2>Quadrat Crop and Analyze Tool</h2>

                <div className="instructions">
                    <p>Use this app to analyze the land cover of quadrat images.</p>
                    <p><strong>1.</strong> Upload an image.</p>
                    <p><strong>2.</strong> Click to place 4 red dots on the inner corners of the quadrat. If you mess up, press <strong>Undo Last Dot</strong>.</p>
                    <p><strong>3.</strong> Click <strong>Crop Quadrat</strong> to run the model.</p>
                </div>

                <input
                    className="file-input"
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                />

                {image && (
                    <div className="workspace">
                        <canvas
                            ref={canvasRef}
                            onClick={handleCanvasClick}
                            className="canvas"
                        />

                        <div className="controls">
                            <span>{points.length}/4 points placed</span>

                            <button
                                onClick={submit}
                                disabled={points.length !== 4 || loading || done}
                            >
                                {loading ? "Cropping…" : "Crop Quadrat"}
                            </button>

                            <button
                                className="secondary"
                                onClick={undoDot}
                                disabled={points.length === 0 || loading || done}
                            >
                                Undo Last Dot
                            </button>
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="loader">
                        <RotatingLines
                            strokeColor="grey"
                            strokeWidth="5"
                            animationDuration="0.75"
                            width="64"
                            visible={true}
                        />
                    </div>
                )}

                {result && (
                    <div className="results">
                        <div className="image-grid">
                            <div>
                                <h4>Cropped Quadrat</h4>
                                <img src={result.cropped} />
                            </div>

                            <div>
                                <h4>Context Image</h4>
                                <img src={result.context} />
                            </div>
                        </div>

                        <ul className="results-list">
                            {result.results.display_list.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/*<Table />*/}
        </div>
    );
}
