export async function processText(text: string): Promise<string> {
  try {
    // Remove common noise
    let processed = text
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove multi-line comments
      .replace(/\/\/.*/g, '') // Remove single-line comments
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    // For now, we'll just return the processed text
    // In the future, we can add API integration if needed
    return processed;
  } catch (error) {
    // If processing fails, return the original text
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
