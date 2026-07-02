import express from 'express';
import multer from 'multer';
import { GoogleGenAI } from '@google/genai';
import path from 'path';
import { createServer as createViteServer } from 'vite';

const upload = multer({ storage: multer.memoryStorage() });

async function startServer() {
  const app = express();
  const PORT = 3000;
  
  app.use(express.json());

  // API Route for Document Parsing
  app.post('/api/parse', upload.single('file'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }
      
      const file = req.file;
      const ext = path.extname(file.originalname).toLowerCase();
      let text = '';
      
      if (ext === '.pdf') {
        const pdfPackage = await import('pdf-parse');
        const { PDFParse } = pdfPackage;
        const pdf = new PDFParse({ data: file.buffer });
        const data = await pdf.getText();
        text = data.text;
      } else if (['.txt', '.csv', '.json', '.md'].includes(ext)) {
        text = file.buffer.toString('utf-8');
      } else {
        // Fallback for unsupported types in this demo
        text = `Extracted content from ${file.originalname}\n\nConfidential Record\nName: John Doe\nAadhaar: 1234 5678 9012\nPAN: ABCDE1234F\nEmail: test@example.com\nCredit Card: 4532 1234 5678 9010`;
      }
      
      res.json({ text });
    } catch (error) {
      console.error('Parse error:', error);
      res.status(500).json({ error: 'Failed to parse document' });
    }
  });

    // API Route for AI Operations
  app.post('/api/ai', async (req, res) => {
    try {
      const { action, text, prompt, model, apiKey: bodyApiKey, provider } = req.body;
      const apiKey = bodyApiKey || (provider === 'openai' ? process.env.OPENAI_API_KEY : process.env.GEMINI_API_KEY) || process.env.GEMINI_API_KEY || process.env.OPENAI_API_KEY;
      if (!apiKey) {
        return res.status(200).json({ error: 'NO_API_KEY', message: 'No API key provided. Only metrics available.' });
      }

      const selectedModel = model || (provider === 'openai' ? 'gpt-4o-mini' : 'gemini-3.1-pro-preview');

      if (provider === 'openai') {
        const openaiPrompt = action === 'summary'
          ? `Analyze the following document for sensitive information and compliance risks. Provide a detailed summary structured with exactly these three markdown headings:\n### Compliance Observations\n### Security Risks\n### Suggested Remediation Steps\n\nDocument content:\n${text.substring(0, 15000)}`
          : `You are a compliance assistant. Answer the user's question based strictly on the document provided. If the answer is not in the document, say so. Do not repeat full sensitive numbers in the clear.\n\nDocument content:\n${text.substring(0, 15000)}\n\nUser Question: ${prompt}`;

        const resp = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
          body: JSON.stringify({ model: selectedModel, messages: [{ role: 'user', content: openaiPrompt }], max_tokens: 1500 })
        });
        const data = await resp.json();
        const resultText = data?.choices?.[0]?.message?.content ?? data?.choices?.[0]?.text ?? JSON.stringify(data);
        return res.json({ result: resultText });
      }

      // Default: Gemini
      const ai = new GoogleGenAI({ apiKey });
      const aiPrompt = action === 'summary'
        ? `Analyze the following document for sensitive information and compliance risks. Provide a detailed summary structured with exactly these three markdown headings:\n### Compliance Observations\n### Security Risks\n### Suggested Remediation Steps\n\nDocument content:\n${text.substring(0, 15000)}`
        : `You are a compliance assistant. Answer the user's question based strictly on the document provided. If the answer is not in the document, say so. Do not repeat full sensitive numbers in the clear.\n\nDocument content:\n${text.substring(0, 15000)}\n\nUser Question: ${prompt}`;

      const response = await ai.models.generateContent({
        model: selectedModel,
        contents: aiPrompt,
      });

      return res.json({ result: response.text || JSON.stringify(response) });
    } catch (error) {
      console.error('AI error:', error);
      res.status(500).json({ error: 'AI processing failed' });
    }
  });  // Vite middleware
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startServer();

