import axios from 'axios';

export async function processText(text: string): Promise<string> {
  try {
    // Remove common noise
    let processed = text
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove multi-line comments
      .replace(/\/\/.*/g, '') // Remove single-line comments
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    // Make API call to enhance text processing if needed
    const response = await axios.get(`https://api.example.com/process?text=${encodeURIComponent(processed)}`);
    return response.data.processed || processed;
  } catch (error) {
    // If API call fails, return the basic processed text
    return text;
  }
}

export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters except hyphens
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();
}
