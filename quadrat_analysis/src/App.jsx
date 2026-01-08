import {useEffect, useRef, useState} from "react";
import './App.css'
import { RotatingLines } from "react-loader-spinner";

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
            // const canvas = canvasRef.current;
            // canvas.width = img.width;
            // canvas.height = img.height;
            //
            // const ctx = canvas.getContext("2d");
            // ctx.drawImage(img, 0, 0);

            imgRef.current = img;
            setImage(file);
            setPoints([]);
            // drawCanvas(img, []);
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
        // drawDot(x, y);
        // setPoints(prev => [...prev, [x, y]]);
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
        }
    };

    // run whenever image or points change
    useEffect(() => {
        if (!image || !imgRef.current) return;
        if (!canvasRef.current) return;

        drawCanvas(imgRef.current, points);
    }, [image, points]);

    return (
        <div style={{ padding: 24 }}>
            <h2>Quadrat Crop and Analyze Tool</h2>

            <input type="file" accept="image/*" onChange={handleImageUpload} />

            <br /><br />

            {image && (
                <>
                    <canvas
                        ref={canvasRef}
                        onClick={handleCanvasClick}
                        style={{ border: "1px solid black", maxWidth: "100%" }}
                    />
                    <p>{points.length}/4 points placed</p>
                    <button onClick={submit} disabled={points.length !== 4}>
                        Crop and Analyze Quadrat
                    </button>
                </>
            )}

            {image && !result && (
                <RotatingLines
                    strokeColor="grey"
                    strokeWidth="5"
                    animationDuration="0.75"
                    width="96"
                    visible={true}
                />
            )}

            {result && (
                <>
                    <h3>Cropped Quadrat</h3>
                    <img src={result.cropped} width="50%" height="50%"/>
                    <h3>Context Image</h3>
                    <img src={result.context} width="50%" height="50%"/>
                    <ul>
                        {result.results.display_list.map((item, i) => (
                            <li key={i}>{item}</li>
                        ))}
                    </ul>
                </>
            )}
        </div>
    );
}
