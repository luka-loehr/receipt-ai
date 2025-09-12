import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import dotenv from "dotenv";
import fs from "fs";
import multer from "multer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, "..");

dotenv.config({ path: path.resolve(projectRoot, ".env") });

const app = express();
app.use(cors());
app.use(express.json());

// Serve static files
app.use(express.static(path.join(__dirname, "public")));

const pngRelative = "outputs/png/daily_brief.png";
const pngPath = path.join(projectRoot, pngRelative);

function runPythonGenerate() {
  return new Promise((resolve, reject) => {
    const venvPython = path.join(projectRoot, "venv", "bin", "python");
    const entrypoint = path.join(projectRoot, "daily_brief.py");

    const env = { ...process.env };
    env.PREVIEW_PNG = "false";

    const child = spawn(venvPython, [entrypoint], { cwd: projectRoot, env });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));

    child.on("close", (code) => {
      if (code === 0) {
        resolve({ code, stdout, stderr });
      } else {
        reject(new Error(`Python exited with code ${code}: ${stderr || stdout}`));
      }
    });
  });
}

app.post("/generate", async (req, res) => {
  try {
    await runPythonGenerate();
    if (!fs.existsSync(pngPath)) {
      return res.status(500).json({ error: "PNG not found after generation" });
    }
    res.json({ ok: true, path: "/image?ts=" + Date.now() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/image", (req, res) => {
  res.sendFile(pngPath);
});

app.get("/health", (req, res) => {
  res.json({ ok: true });
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// New: capture upload page
app.get("/capture", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "capture.html"));
});

// New: capture API (text + optional image)
const upload = multer({ dest: path.join(projectRoot, "server", "uploads") });

function runPythonCapture({ text, imagePath }) {
  return new Promise((resolve, reject) => {
    const venvPython = path.join(projectRoot, "venv", "bin", "python");
    const entrypoint = path.join(projectRoot, "-m" );
    const modulePath = "src.capture_generate";

    const env = { ...process.env };
    env.PREVIEW_PNG = "false";
    if (text) env.TEXT = text;
    if (imagePath) env.IMAGE = imagePath;

    const child = spawn(venvPython, ["-m", modulePath], { cwd: projectRoot, env });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));

    child.on("close", (code) => {
      if (code === 0) {
        resolve({ code, stdout: stdout.trim(), stderr });
      } else {
        reject(new Error(`Python exited with code ${code}: ${stderr || stdout}`));
      }
    });
  });
}

app.post("/capture", upload.single("image"), async (req, res) => {
  try {
    const text = req.body?.text || "";
    const imagePath = req.file ? req.file.path : undefined;
    const result = await runPythonCapture({ text, imagePath });

    // The Python script prints the output path
    const outPathAbs = result.stdout;
    if (!fs.existsSync(outPathAbs)) {
      return res.status(500).json({ error: "PNG not created" });
    }

    // Serve via a fixed route
    const relFromRoot = path.relative(projectRoot, outPathAbs);
    app.get("/capture-image", (req2, res2) => res2.sendFile(outPathAbs));
    res.json({ ok: true, path: "/capture-image?ts=" + Date.now() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});
