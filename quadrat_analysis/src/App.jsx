import { useRef, useState } from "react";
import './App.css'

export default function App() {
    const canvasRef = useRef(null);
    const imgRef = useRef(null);
    const [image, setImage] = useState(null);
    const [points, setPoints] = useState([]);
    const [result, setResult] = useState(null);

    // load image
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const img = new Image();
        img.onload = () => {
            const canvas = canvasRef.current;
            canvas.width = img.width;
            canvas.height = img.height;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);

            imgRef.current = img;
            setImage(file);
            setPoints([]);
        };

        img.src = URL.createObjectURL(file);
    };

    // draw dot
    const drawDot = (x, y) => {
        const ctx = canvasRef.current.getContext("2d");
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
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

        drawDot(x, y);
        setPoints(prev => [...prev, [x, y]]);
    };

    // submit to backend
    const submit = async () => {
        if (points.length !== 4) {
            alert("Please place exactly 4 red dots.");
            return;
        }

        const form = new FormData();
        form.append("image", image);
        form.append("points", JSON.stringify(points));

        const res = await fetch("http://localhost:8000/crop-quadrat", {
            method: "POST",
            body: form,
        });

        const data = await res.json();
        setResult({
            cropped: "data:image/png;base64," + data.cropped_image,
            context: "data:image/png;base64," + data.context_image,
        });
    };

    return (
        <div style={{ padding: 24 }}>
            <h2>Quadrat Crop Tool</h2>

            <input type="file" accept="image/*" onChange={handleImageUpload} />

            <br /><br />

            <canvas
                ref={canvasRef}
                onClick={handleCanvasClick}
                style={{ border: "1px solid black", maxWidth: "100%" }}
            />

            <p>{points.length}/4 points placed</p>

            <button onClick={submit} disabled={points.length !== 4}>
                Crop Quadrat
            </button>

            {result && (
                <>
                    <h3>Cropped Quadrat</h3>
                    <img src={result.cropped} width="50%" height="50%"/>

                    <h3>Context Image</h3>
                    <img src={result.context} width="50%" height="50%"/>
                </>
            )}
        </div>
    );
}
